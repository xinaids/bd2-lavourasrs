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
ANOS = [str(ano) for ano in range(1990, 2027)]

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
        "classificacao": "82",
        "culturas": "2723",
        "variaveis": {
            "2313": "Área destinada à colheita (Hectares)",
            "216": "Área colhida - Permanentes (Hectares)",
            "214": "Quantidade produzida (Toneladas)",
            "215": "Valor da produção (Mil Reais)"
        }
    }
]


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

    -- NOVA TABELA: CLIMA HISTÓRICO
    CREATE TABLE IF NOT EXISTS clima_historico (
        id SERIAL PRIMARY KEY,
        estado_id INT NOT NULL,
        ano INT NOT NULL,
        precipitacao_anual_mm NUMERIC,
        fenomeno_enso VARCHAR(20),
        FOREIGN KEY (estado_id) REFERENCES estado(id),
        UNIQUE (estado_id, ano)
    );
    """
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()
    print("-> Estrutura normalizada de tabelas (IBGE + Clima) criada/verificada com sucesso!")

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
    regioes = [
        (1, 'Norte', 'NO'), (2, 'Nordeste', 'NE'),
        (3, 'Sudeste', 'SE'), (4, 'Sul', 'S'), (5, 'Centro-Oeste', 'CO')
    ]
    execute_values(
        cur, "INSERT INTO regiao (id, nome, sigla) VALUES %s ON CONFLICT (id) DO NOTHING;", regioes)
    res = requests.get(
        "https://servicodados.ibge.gov.br/api/v1/localidades/estados")
    if res.status_code == 200:
        estados = [(e['id'], e['nome'], e['sigla'], e['regiao']['id'])
                   for e in res.json()]
        execute_values(
            cur, "INSERT INTO estado (id, nome, sigla, regiao_id) VALUES %s ON CONFLICT (id) DO NOTHING;", estados)
    vars_data = [(int(k), v) for k, v in VARIAVEIS.items()]
    execute_values(
        cur, "INSERT INTO variavel (id, nome) VALUES %s ON CONFLICT (id) DO NOTHING;", vars_data)
    conn.commit()
    print("-> Domínios inseridos com sucesso!")
    cur.close()
    conn.close()

# ==========================================
# 6. FUNÇÃO DE CONVERSÃO DE MOEDAS ANTIGAS
# ==========================================


def normalizar_moeda_para_real(ano, valor_original):
    if ano <= 1992:
        return valor_original / 2750000.0
    elif ano == 1993:
        return valor_original / 2750.0
    else:
        return valor_original

# ==========================================
# 7. INGESTÃO DOS DADOS DO IBGE
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
    for config in CONFIG_EXTRACOES:
        print(f"\n---> Extraindo dados de: {config['nome']}")
        for ano in ANOS:
            for cod_var in config["variaveis"].keys():
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
                                                    ano_int = int(ano_resp)
                                                    if str(var_id) == "215":
                                                        val_num = normalizar_moeda_para_real(
                                                            ano_int, val_num) * 1000
                                                    producoes_para_inserir.append((
                                                        mun_id, prod_id, var_id, unidade_id, ano_int, val_num
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
                    except Exception as e:
                        print(f"[!] Erro de conexão: {e}. Tentando de novo...")
                        tentativas += 1
                        time.sleep(3)
    cur.close()
    conn.close()
    print(f"\n==========================================")
    print(
        f"CONCLUÍDO! {total_registros} registros salvos no PostgreSQL (IBGE)!")
    print(f"==========================================")

# ==========================================
# 8. INGESTÃO DOS DADOS DE CLIMA (NASA POWER)
# ==========================================


def executar_ingestao_clima():
    print("\n==========================================")
    print("Iniciando ingestão Climática (NASA POWER API)...")
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    enso_historico = {
        1990: "Neutro", 1991: "El Niño", 1992: "El Niño", 1993: "Neutro", 1994: "El Niño",
        1995: "La Niña", 1996: "La Niña", 1997: "El Niño", 1998: "La Niña", 1999: "La Niña",
        2000: "La Niña", 2001: "Neutro", 2002: "El Niño", 2003: "Neutro", 2004: "Neutro",
        2005: "La Niña", 2006: "El Niño", 2007: "La Niña", 2008: "La Niña", 2009: "El Niño",
        2010: "La Niña", 2011: "La Niña", 2012: "Neutro", 2013: "Neutro", 2014: "Neutro",
        2015: "El Niño", 2016: "La Niña", 2017: "La Niña", 2018: "El Niño", 2019: "El Niño",
        2020: "La Niña", 2021: "La Niña", 2022: "La Niña", 2023: "El Niño", 2024: "El Niño",
        2025: "Neutro", 2026: "La Niña"
    }
    # Dicionário de Coordenadas (Latitude, Longitude) focadas nas áreas agrícolas
    coords_estados = {
        11: (-10.7, -62.8),  # RO
        12: (-9.0, -70.5),  # AC
        13: (-3.1, -60.0),  # AM
        14: (2.8, -60.6),   # RR
        15: (-3.2, -52.2),  # PA
        16: (1.4, -51.8),   # AP
        17: (-10.1, -48.3),  # TO - Pedro Afonso
        21: (-7.5, -46.0),  # MA - Balsas (MATOPIBA)
        22: (-8.9, -44.2),  # PI - Uruçuí (MATOPIBA)
        23: (-5.2, -39.3),  # CE
        24: (-5.7, -36.5),  # RN
        25: (-7.1, -36.8),  # PB
        26: (-8.3, -37.9),  # PE
        27: (-9.6, -36.6),  # AL
        28: (-10.6, -37.4),  # SE
        29: (-12.1, -44.9),  # BA - Barreiras (MATOPIBA)
        31: (-19.0, -46.0),  # MG - Triângulo Mineiro
        32: (-19.3, -40.5),  # ES
        33: (-22.9, -43.2),  # RJ
        35: (-21.5, -48.3),  # SP - Ribeirão Preto
        41: (-24.9, -53.4),  # PR - Cascavel
        42: (-27.0, -51.1),  # SC
        43: (-28.6, -53.6),  # RS - Cruz Alta
        50: (-21.2, -54.4),  # MS - Dourados
        51: (-12.7, -55.7),  # MT - Sorriso
        52: (-17.7, -50.9),  # GO - Rio Verde
        53: (-15.7, -47.9)  # DF
    }
    dados_para_inserir = []
    for estado_id, (lat, lon) in coords_estados.items():
        print(f"\n---> Extraindo chuva da NASA para o Estado ID: {estado_id}")
        # A NASA permite blocos maiores, então vamos fazer ano a ano de 1990 a 2025 de forma limpa
        for ano in range(1990, 2027):
            fenomeno = enso_historico.get(ano, "Neutro")
            # PRECTOTCORR é o parâmetro oficial da NASA para Chuva Corrigida (Precipitation)
            url_nasa = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR&community=AG&longitude={lon}&latitude={lat}&start={ano}0101&end={ano}1231&format=JSON"
            sucesso = False
            while not sucesso:
                try:
                    resp = requests.get(url_nasa, timeout=30)
                    if resp.status_code == 200:
                        json_nasa = resp.json()
                        # A NASA devolve um dicionário com os dias do ano e a chuva em mm/dia
                        chuvas_diarias = json_nasa['properties']['parameter']['PRECTOTCORR']
                        # Soma todos os dias do ano (ignorando -999.0 que é o código de erro da NASA para dados ausentes)
                        chuva_anual = sum(
                            valor for valor in chuvas_diarias.values() if valor != -999.0)
                        print(f"  [OK] {ano} processado: {chuva_anual:.1f} mm")
                        dados_para_inserir.append(
                            (estado_id, ano, chuva_anual, fenomeno))
                        sucesso = True
                        # Pausa para não sobrecarregar o servidor
                        time.sleep(0.5)
                    else:
                        print(
                            f"  [!] HTTP {resp.status_code}. Pausando e tentando novamente...")
                        time.sleep(3)
                except Exception as e:
                    print(f"  [!] Erro de conexão: {e}. Tentando novamente...")
                    time.sleep(3)
    insert_query = """
    INSERT INTO clima_historico (estado_id, ano, precipitacao_anual_mm, fenomeno_enso)
    VALUES %s
    ON CONFLICT (estado_id, ano)
    DO UPDATE SET
        precipitacao_anual_mm = EXCLUDED.precipitacao_anual_mm,
        fenomeno_enso = EXCLUDED.fenomeno_enso;
    """
    execute_values(cur, insert_query, dados_para_inserir)
    conn.commit()
    cur.close()
    conn.close()
    print(
        f"\n-> SUCESSO ABSOLUTO! {len(dados_para_inserir)} registros climáticos (100% sem falhas) inseridos no banco.")
    print("==========================================\n")


if __name__ == "__main__":
    # 1. Executa a ingestão do IBGE (PAM 1990-2025)
    executar_ingestao_brasil()

    # 2. Executa a ingestão de Clima (NASA 1990-2026)
    executar_ingestao_clima()
