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
# Tabela 1612: Lavouras temporárias
# N6[all] = Todos os municípios do Brasil

URL_BASE = "https://servicodados.ibge.gov.br/api/v3/agregados/1612"

LOCALIDADE_BR = "N6[all]"

CULTURAS = "2692,2696,2698,2699,2702,2711,2713,2716"

# Variáveis separadas para consultar uma a uma:

VARIAVEIS = {
    "109": "Área plantada (Hectares)",
    "216": "Área colhida (Hectares)",
    "214": "Quantidade produzida (Toneladas)",
    "215": "Valor da produção (Mil Reais)"
}

# Anos de 1990 até 2023
ANOS = [str(ano) for ano in range(1990, 2024)]


FALHAS = [
    {"ano": "1996", "var": "214"},
    {"ano": "2012", "var": "215"}
]

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

    CREATE TABLE IF NOT EXISTS producao_agricola (
        id SERIAL PRIMARY KEY,
        municipio_id VARCHAR(20) NOT NULL,
        produto VARCHAR(100) NOT NULL,
        variavel VARCHAR(100) NOT NULL,
        unidade VARCHAR(50),
        ano INT NOT NULL,
        valor NUMERIC,
        FOREIGN KEY (municipio_id) REFERENCES municipio(id)
    );
    """
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()
    print("-> Estrutura de tabelas (regiao, estado, municipio, producao_agricola) criada/verificada com sucesso!")

# ==========================================
# 4. TRATAMENTO DO NOME DOS MUNICÍPIOS
# ==========================================


def limpar_nome_municipio(mun_id, nome):
    if not nome:
        return nome
    # 1. Trata EXCLUSIVAMENTE o município de Sant'Ana do Livramento no RS (Código IBGE 4317103)
    if str(mun_id) == "4317103":
        return "Santana do Livramento"
    # 2. Para TODOS os outros municípios do Brasil:
    # Remove sufixos como " - RS", " - SP", etc.
    if " - " in nome:
        nome = nome.split(" - ")[0]
    # Remove aspas simples e duplas mantendo o nome oficial
    nome = nome.replace("'", "").replace('"', "")
    return nome.strip()

# ==========================================
# 5. CARGA DAS TABELAS DE DOMÍNIO (REGIÕES E ESTADOS)
# ==========================================


def carregar_regioes_e_estados():
    print("-> Carregando tabela de Regiões e Estados...")
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    regioes = [
        (1, 'Norte', 'NO'),
        (2, 'Nordeste', 'NE'),
        (3, 'Sudeste', 'SE'),
        (4, 'Sul', 'S'),
        (5, 'Centro-Oeste', 'CO')
    ]
    execute_values(
        cur, "INSERT INTO regiao (id, nome, sigla) VALUES %s ON CONFLICT (id) DO NOTHING;", regioes)
    res = requests.get(
        "https://servicodados.ibge.gov.br/api/v1/localidades/estados")
    if res.status_code == 200:
        estados_data = res.json()
        estados = []
        for est in estados_data:
            estados.append((
                est['id'],
                est['nome'],
                est['sigla'],
                est['regiao']['id']
            ))
        execute_values(
            cur, "INSERT INTO estado (id, nome, sigla, regiao_id) VALUES %s ON CONFLICT (id) DO NOTHING;", estados)
        conn.commit()
        print("-> Regiões e Estados inseridos com sucesso!")
    cur.close()
    conn.close()

# ==========================================
# 6. INGESTÃO DOS DADOS PARA O BRASIL INTEIRO
# ==========================================


def executar_ingestao_brasil():
    criar_tabelas()
    carregar_regioes_e_estados()
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    total_registros = 0
    municipios_cadastrados = set()
    print("\nIniciando coleta dos dados de produção agrícola para o BRASIL INTEIRO...\n")
    for ano in ANOS:
        for cod_var in VARIAVEIS.keys():
            url = f"{URL_BASE}/periodos/{ano}/variaveis/{cod_var}?localidades={LOCALIDADE_BR}&classificacao=81[{CULTURAS}]"
            sucesso = False
            tentativas = 0
            while not sucesso and tentativas < 3:
                try:
                    response = requests.get(url, timeout=300)
                    if response.status_code == 200:
                        raw_data = response.json()
                        novos_municipios = []
                        producoes_para_inserir = []
                        for bloco in raw_data:
                            nome_var = bloco['variavel']
                            unidade = bloco['unidade']
                            for resultado in bloco['resultados']:
                                produto = list(
                                    resultado['classificacoes'][0]['categoria'].values())[0]
                                for serie in resultado['series']:
                                    mun_id = serie['localidade']['id']
                                    # Passa o mun_id para a limpeza ser pontual no 4317103
                                    mun_nome = limpar_nome_municipio(
                                        mun_id, serie['localidade']['nome'])
                                    # Extrai ID do Estado pelos 2 primeiros dígitos do código IBGE do município
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
                                                    mun_id, produto, nome_var, unidade, int(
                                                        ano_resp), val_num
                                                ))
                                            except ValueError:
                                                pass
                        # Inserção de novos municípios na tabela 'municipio'
                        if novos_municipios:
                            insert_mun = "INSERT INTO municipio (id, nome, estado_id) VALUES %s ON CONFLICT (id) DO NOTHING;"
                            execute_values(cur, insert_mun, novos_municipios)
                        # Inserção de dados na tabela de fatos 'producao_agricola'
                        if producoes_para_inserir:
                            insert_prod = """
                            INSERT INTO producao_agricola
                            (municipio_id, produto, variavel, unidade, ano, valor)
                            VALUES %s;
                            """
                            execute_values(cur, insert_prod,
                                           producoes_para_inserir)
                            conn.commit()
                            qtd = len(producoes_para_inserir)
                            total_registros += qtd
                            print(
                                f"[OK BRASIL] Ano: {ano} | Variável: {cod_var} | Registros salvos: {qtd}")
                        sucesso = True
                        time.sleep(0.3)
                    else:
                        print(
                            f"[!] HTTP {response.status_code} no ano {ano}, var {cod_var}. Tentando de novo...")
                        tentativas += 1
                        time.sleep(3)
                except Exception as e:
                    print(f"[!] Erro de conexão: {e}. Tentando de novo...")
                    tentativas += 1
                    time.sleep(3)
    cur.close()
    conn.close()
    print(f"\n==========================================")
    print(
        f"CONCLUÍDO! {total_registros} registros salvos no PostgreSQL para o Brasil!")
    print(f"==========================================")


if __name__ == "__main__":
    executar_ingestao_brasil()
