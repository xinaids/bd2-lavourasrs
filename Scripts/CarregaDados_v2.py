import requests
import psycopg2
from psycopg2.extras import execute_values
import time

# ==========================================
# 1. CONFIGURAÇÃO DA CONEXÃO VIA DB_URI
# ==========================================
# Formato: postgresql://usuario:senha@host:porta/nome_do_banco
DB_URI = ""

# ==========================================
# 2. PARÂMETROS DA API DO SIDRA / IBGE
# ==========================================
LOCALIDADE_BR = "N6[all]"
ANOS = [str(ano) for ano in range(1990, 2024)]

# Lista de configurações para buscar tanto Lavouras Temporárias quanto Permanentes
CONFIG_EXTRACOES = [
    {
        "nome": "Temporárias (Soja, Milho, Cana, Arroz, Algodão, Feijão, Trigo)",
        "url_base": "https://servicodados.ibge.gov.br/api/v3/agregados/1612",
        "classificacao": "81",
        "culturas": "2689,2692,2696,2702,2711,2713,2716",
        "variaveis": {
            "109": "Área plantada (Hectares)",
            "216": "Área colhida (Hectares)",
            "214": "Quantidade produzida (Toneladas)",
            "215": "Valor da produção (Mil Reais)"
        }
    },
    {
        "nome": "Permanentes (Café)",
        "url_base": "https://servicodados.ibge.gov.br/api/v3/agregados/1613",
        "classificacao": "82",  # A classificação para lavouras permanentes muda para 82
        # 2723 é o código padrão para Café (Total) no IBGE
        "culturas": "2723",
        "variaveis": {
            # Equivale à Área plantada
            "2313": "Área destinada à colheita (Hectares)",
            "216": "Área colhida - Permanentes (Hectares)",
            "214": "Quantidade produzida (Toneladas)",
            "215": "Valor da produção (Mil Reais)"
        }
    }
]

# Unifica as variáveis de ambas as tabelas para criar as tabelas de Domínio
VARIAVEIS = {}
for config in CONFIG_EXTRACOES:
    VARIAVEIS.update(config["variaveis"])

# ==========================================
# 3. CRIAÇÃO AUTOMÁTICA DAS TABELAS NO POSTGRES
# ==========================================


def criar_tabelas():
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS regiao (
        id INT PRIMARY KEY,
        nome VARCHAR(50) NOT NULL,
        sigla VARCHAR(5) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS estado (
        id INT PRIMARY KEY,
        nome VARCHAR(50) NOT NULL,
        sigla VARCHAR(2) NOT NULL,
        regiao_id INT NOT NULL,
        FOREIGN KEY (regiao_id) REFERENCES regiao(id)
    );

    CREATE TABLE IF NOT EXISTS municipio (
        id VARCHAR(20) PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        estado_id INT NOT NULL,
        FOREIGN KEY (estado_id) REFERENCES estado(id)
    );

    -- Novas tabelas de dimensão
    CREATE TABLE IF NOT EXISTS variavel (
        id INT PRIMARY KEY,
        nome VARCHAR(100) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS produto (
        id INT PRIMARY KEY,
        nome VARCHAR(100) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS unidade (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(50) UNIQUE NOT NULL
    );

    -- Tabela fato refatorada com chaves estrangeiras
    CREATE TABLE IF NOT EXISTS producao_agricola (
        id SERIAL PRIMARY KEY,
        municipio_id VARCHAR(20) NOT NULL,
        produto_id INT NOT NULL,
        variavel_id INT NOT NULL,
        unidade_id INT NOT NULL,
        ano INT NOT NULL,
        valor NUMERIC,
        FOREIGN KEY (municipio_id) REFERENCES municipio(id),
        FOREIGN KEY (produto_id) REFERENCES produto(id),
        FOREIGN KEY (variavel_id) REFERENCES variavel(id),
        FOREIGN KEY (unidade_id) REFERENCES unidade(id)
    );
    """
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()
    print("-> Estrutura normalizada de tabelas criada/verificada com sucesso!")

# ==========================================
# 4. TRATAMENTO DO NOME DOS MUNICÍPIOS E UNIDADES
# ==========================================


def limpar_nome_municipio(mun_id, nome):
    if not nome:
        return nome
    if str(mun_id) == "4317103":
        return "Santana do Livramento"
    if " - " in nome:
        nome = nome.split(" - ")[0]
    return nome.replace("'", "").replace('"', "").strip()


def obter_id_unidade(cur, nome_unidade, cache_unidades):
    """Verifica se a unidade existe no banco. Se não, insere e devolve o ID."""
    if nome_unidade not in cache_unidades:
        cur.execute(
            "INSERT INTO unidade (nome) VALUES (%s) ON CONFLICT (nome) DO NOTHING RETURNING id;", (nome_unidade,))
        res = cur.fetchone()
        if res:
            cache_unidades[nome_unidade] = res[0]
        else:
            cur.execute("SELECT id FROM unidade WHERE nome = %s;",
                        (nome_unidade,))
            cache_unidades[nome_unidade] = cur.fetchone()[0]
    return cache_unidades[nome_unidade]

# ==========================================
# 5. CARGA DAS TABELAS DE DOMÍNIO
# ==========================================


def carregar_dominios():
    print("-> Carregando tabelas de domínio (Regiões, Estados e Variáveis)...")
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()

    # 5.1 Regiões
    regioes = [
        (1, 'Norte', 'NO'), (2, 'Nordeste', 'NE'),
        (3, 'Sudeste', 'SE'), (4, 'Sul', 'S'), (5, 'Centro-Oeste', 'CO')
    ]
    execute_values(
        cur, "INSERT INTO regiao (id, nome, sigla) VALUES %s ON CONFLICT (id) DO NOTHING;", regioes)

    # 5.2 Estados
    res = requests.get(
        "https://servicodados.ibge.gov.br/api/v1/localidades/estados")
    if res.status_code == 200:
        estados = [(e['id'], e['nome'], e['sigla'], e['regiao']['id'])
                   for e in res.json()]
        execute_values(
            cur, "INSERT INTO estado (id, nome, sigla, regiao_id) VALUES %s ON CONFLICT (id) DO NOTHING;", estados)

    # 5.3 Variáveis
    vars_data = [(int(k), v) for k, v in VARIAVEIS.items()]
    execute_values(
        cur, "INSERT INTO variavel (id, nome) VALUES %s ON CONFLICT (id) DO NOTHING;", vars_data)

    conn.commit()
    print("-> Domínios inseridos com sucesso!")
    cur.close()
    conn.close()

# ==========================================
# 6. INGESTÃO DOS DADOS
# ==========================================


def executar_ingestao_brasil():
    criar_tabelas()
    carregar_dominios()

    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()

    total_registros = 0
    municipios_cadastrados = set()
    produtos_cadastrados = set()
    cache_unidades = {}

    print("\nIniciando coleta dos dados de produção agrícola para o BRASIL INTEIRO...\n")

    # Loop para rodar primeiro a Tabela 1612 e depois a Tabela 1613
    for config in CONFIG_EXTRACOES:
        print(f"\n---> Extraindo dados de: {config['nome']}")

        for ano in ANOS:
            for cod_var in config["variaveis"].keys():
                # A URL agora é montada dinamicamente com base no bloco atual
                url = f"{config['url_base']}/periodos/{ano}/variaveis/{cod_var}?localidades={LOCALIDADE_BR}&classificacao={config['classificacao']}[{config['culturas']}]"

                sucesso = False
                tentativas = 0

                while not sucesso and tentativas < 3:
                    try:
                        response = requests.get(url, timeout=45)

                        if response.status_code == 200:
                            raw_data = response.json()
                            novos_municipios = []
                            novos_produtos = []
                            producoes_para_inserir = []

                            for bloco in raw_data:
                                var_id = int(cod_var)
                                unidade_nome = bloco['unidade']
                                unidade_id = obter_id_unidade(
                                    cur, unidade_nome, cache_unidades)

                                for resultado in bloco['resultados']:
                                    cat_dict = resultado['classificacoes'][0]['categoria']
                                    prod_id = int(list(cat_dict.keys())[0])
                                    prod_nome = list(cat_dict.values())[0]

                                    if prod_id not in produtos_cadastrados:
                                        novos_produtos.append(
                                            (prod_id, prod_nome))
                                        produtos_cadastrados.add(prod_id)

                                    for serie in resultado['series']:
                                        mun_id = serie['localidade']['id']
                                        mun_nome = limpar_nome_municipio(
                                            mun_id, serie['localidade']['nome'])
                                        estado_id = int(str(mun_id)[:2])

                                        if mun_id not in municipios_cadastrados:
                                            novos_municipios.append(
                                                (mun_id, mun_nome, estado_id))
                                            municipios_cadastrados.add(mun_id)

                                        for ano_resp, valor in serie['serie'].items():
                                            if valor is not None and valor != "...":
                                                try:
                                                    val_num = float(valor)
                                                    producoes_para_inserir.append((
                                                        mun_id, prod_id, var_id, unidade_id, int(
                                                            ano_resp), val_num
                                                    ))
                                                except ValueError:
                                                    pass

                            if novos_municipios:
                                execute_values(
                                    cur, "INSERT INTO municipio (id, nome, estado_id) VALUES %s ON CONFLICT (id) DO NOTHING;", novos_municipios)

                            if novos_produtos:
                                execute_values(
                                    cur, "INSERT INTO produto (id, nome) VALUES %s ON CONFLICT (id) DO NOTHING;", novos_produtos)

                            if producoes_para_inserir:
                                insert_prod_agricola = """
                                INSERT INTO producao_agricola 
                                (municipio_id, produto_id, variavel_id, unidade_id, ano, valor) 
                                VALUES %s;
                                """
                                execute_values(
                                    cur, insert_prod_agricola, producoes_para_inserir)

                            conn.commit()

                            qtd = len(producoes_para_inserir)
                            total_registros += qtd
                            print(
                                f"[OK] Ano: {ano} | Variável: {cod_var} | Registros salvos: {qtd}")

                            sucesso = True
                            time.sleep(0.3)

                        else:
                            print(
                                f"[!] HTTP {response.status_code} no ano {ano}, var {cod_var}. Tentando de novo...")
                            tentativas += 1
                            time.sleep(3)
                    # O IBGE retorna HTTP 500 em variáveis de área (113/114) de lavouras permanentes
                    # nos anos muito antigos (ex: 1990). O loop tenta 3x e segue normalmente.
                    except Exception as e:
                        print(f"[!] Erro de conexão: {e}. Tentando de novo...")
                        tentativas += 1
                        time.sleep(3)

    cur.close()
    conn.close()
    print(f"\n==========================================")
    print(f"CONCLUÍDO! {total_registros} registros salvos no PostgreSQL!")
    print(f"==========================================")


if __name__ == "__main__":
    executar_ingestao_brasil()
