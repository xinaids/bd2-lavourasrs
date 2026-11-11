"""
Le os zips anuais do INMET (portal.inmet.gov.br/uploads/dadoshistoricos/ANO.zip)
e gera:
  1) um CSV com a chuva mensal por estacao;
  2) um arquivo .sql unico (mesmo nome do CSV) com os dados 2008-2023 ja dentro,
     tabelas e views prontas, para carregar no banco "lavouras" e mandar para o grupo.

Uso:
    python inmet_chuva_rs.py PASTA_COM_OS_ZIPS chuva_mensal_brasil.csv          (Brasil todo)
    python inmet_chuva_rs.py PASTA_COM_OS_ZIPS chuva_mensal_rs.csv RS           (so o RS)
    python inmet_chuva_rs.py PASTA_COM_OS_ZIPS chuva_mensal.csv RS,SC,PR        (varios)

Requer: pip install pandas
Saida do CSV (uma linha por estacao/ano/mes):
    estacao, codigo, uf, latitude, longitude, ano, mes, chuva_mm, horas_validas
"""
import io
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

ANO_INI_SQL, ANO_FIM_SQL = 2008, 2023


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def parse_meta(linhas):
    meta = {}
    for ln in linhas:
        if ":" in ln:
            chave, _, valor = ln.partition(":")
            meta[sem_acento(chave).strip().upper()] = valor.strip().strip(";").strip()
    return meta


def nome_do_arquivo(caminho):
    """INMET_CO_DF_A001_BRASILIA_01-01-2025_A_31-12-2025.CSV -> ('A001', 'BRASILIA')"""
    base = Path(caminho).name
    m = re.match(r"INMET_[A-Z]+_[A-Z]{2}_([A-Z0-9]+)_(.+?)_\d{2}-\d{2}-\d{4}_A_", base, re.I)
    return (m.group(1), m.group(2)) if m else (None, None)


def parse_data(serie):
    s = serie.astype(str).str.strip()
    iso = s.str.match(r"^\d{4}[-/]\d{2}[-/]\d{2}$")
    saida = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    saida[iso] = pd.to_datetime(s[iso].str.replace("/", "-"), format="%Y-%m-%d", errors="coerce")
    saida[~iso] = pd.to_datetime(s[~iso].str.replace("-", "/"), format="%d/%m/%Y", errors="coerce")
    return saida


def le_estacao(bruto, nome_arquivo):
    texto = bruto.decode("latin-1")
    linhas = texto.splitlines()
    meta = parse_meta(linhas[:8])
    df = pd.read_csv(
        io.StringIO("\n".join(linhas[8:])),
        sep=";",
        decimal=",",
        na_values=["-9999", "-9999.0", ""],
        low_memory=False,
    )
    col_chuva = next((c for c in df.columns if str(c).upper().startswith("PRECIPITA")), None)
    if col_chuva is None:
        return None
    data = parse_data(df.iloc[:, 0])
    chuva = pd.to_numeric(df[col_chuva], errors="coerce")
    chuva = chuva.where(chuva >= 0)  # valores negativos = erro de leitura
    base = pd.DataFrame({"data": data, "chuva": chuva}).dropna(subset=["data"])
    base["ano"] = base["data"].dt.year
    base["mes"] = base["data"].dt.month
    mensal = base.groupby(["ano", "mes"]).agg(
        chuva_mm=("chuva", lambda x: x.sum(min_count=1)),  # mes sem leitura fica vazio, nao 0
        horas_validas=("chuva", "count"),
    ).reset_index()
    cod_arq, nome_arq = nome_do_arquivo(nome_arquivo)
    # o nome vem do nome do arquivo (sempre presente); o cabecalho muda de formato entre os anos
    mensal["estacao"] = (nome_arq or meta.get("ESTACAO", "")).replace("_", " ").strip()
    mensal["codigo"] = cod_arq or meta.get("CODIGO (WMO)", "")
    mensal["uf"] = meta.get("UF", "")
    mensal["latitude"] = float(meta.get("LATITUDE", "nan").replace(",", "."))
    mensal["longitude"] = float(meta.get("LONGITUDE", "nan").replace(",", "."))
    return mensal


# ---------------------------------------------------------------- SQL unico
SQL_ABERTURA = """-- CLIMA INMET (chuva mensal {ini}-{fim}, estacoes do INMET) para o banco "lavouras".
-- Arquivo unico: ja traz os dados dentro. Rodar no banco lavouras (psql, DBeaver, pgAdmin...):
--   docker cp clima_inmet.sql metabase-postgres:/tmp/clima_inmet.sql
--   docker exec -i metabase-postgres psql -U metabase -d lavouras -f /tmp/clima_inmet.sql
-- Fonte: INMET, dados historicos (portal.inmet.gov.br/dadoshistoricos).
-- chuva_mm = soma da chuva horaria no mes; horas_validas = horas com leitura no mes
-- (meses com poucas horas sao descartados na view chuva_municipio_mes).

CREATE EXTENSION IF NOT EXISTS unaccent;

DROP TABLE IF EXISTS chuva_estacao_mes CASCADE;
CREATE TABLE chuva_estacao_mes (
  estacao        text,
  codigo         text,
  uf             char(2),
  latitude       numeric,
  longitude      numeric,
  ano            int,
  mes            int,
  chuva_mm       numeric,   -- soma da chuva horaria no mes
  horas_validas  int,       -- horas com leitura no mes (maximo ~720-744)
  PRIMARY KEY (codigo, ano, mes)
);

"""

SQL_FECHAMENTO = """
-- sigla da UF -> nome do estado (como esta na tabela estado)
DROP TABLE IF EXISTS uf_estado CASCADE;
CREATE TABLE uf_estado (uf char(2) PRIMARY KEY, nome text);
INSERT INTO uf_estado VALUES
 ('AC','Acre'),('AL','Alagoas'),('AP','Amapá'),('AM','Amazonas'),('BA','Bahia'),
 ('CE','Ceará'),('DF','Distrito Federal'),('ES','Espírito Santo'),('GO','Goiás'),
 ('MA','Maranhão'),('MT','Mato Grosso'),('MS','Mato Grosso do Sul'),('MG','Minas Gerais'),
 ('PA','Pará'),('PB','Paraíba'),('PR','Paraná'),('PE','Pernambuco'),('PI','Piauí'),
 ('RJ','Rio de Janeiro'),('RN','Rio Grande do Norte'),('RS','Rio Grande do Sul'),
 ('RO','Rondônia'),('RR','Roraima'),('SC','Santa Catarina'),('SP','São Paulo'),
 ('SE','Sergipe'),('TO','Tocantins');

-- estacao -> municipio (pelo nome; tira o que vem depois de " - " ou "(")
-- Exemplo: "CAXIAS DO SUL - CRIUVA" vira "CAXIAS DO SUL".
DROP VIEW IF EXISTS estacao_municipio CASCADE;
CREATE VIEW estacao_municipio AS
SELECT DISTINCT ON (c.codigo)
       c.codigo, c.estacao, c.uf, m.id AS municipio_id, m.nome AS municipio
FROM (SELECT DISTINCT codigo, estacao, uf FROM chuva_estacao_mes) c
JOIN uf_estado u  ON u.uf = c.uf
JOIN estado    e  ON unaccent(lower(e.nome)) = unaccent(lower(u.nome))
JOIN municipio m  ON m.estado_id = e.id
 AND unaccent(lower(m.nome)) =
     unaccent(lower(btrim(regexp_replace(c.estacao, '\\s*[-(].*$', ''))))
ORDER BY c.codigo, m.id;

-- chuva mensal por municipio: so meses com >= 600 horas de leitura (~80%);
-- se houver mais de uma estacao no municipio, fica a de mais horas validas.
DROP VIEW IF EXISTS chuva_municipio_mes CASCADE;
CREATE VIEW chuva_municipio_mes AS
SELECT DISTINCT ON (em.municipio_id, c.ano, c.mes)
       em.municipio_id, c.codigo, c.ano, c.mes, c.chuva_mm, c.horas_validas
FROM chuva_estacao_mes c
JOIN estacao_municipio em ON em.codigo = c.codigo
WHERE c.horas_validas >= 600 AND c.chuva_mm IS NOT NULL
ORDER BY em.municipio_id, c.ano, c.mes, c.horas_validas DESC;

-- ===== CONFERENCIAS =====

-- estacoes que casaram com um municipio, por UF
SELECT s.uf,
       COUNT(*)                    AS estacoes,
       COUNT(em.codigo)            AS casaram,
       COUNT(*) - COUNT(em.codigo) AS sem_municipio
FROM (SELECT DISTINCT codigo, uf FROM chuva_estacao_mes) s
LEFT JOIN estacao_municipio em ON em.codigo = s.codigo
GROUP BY s.uf ORDER BY s.uf;

-- estacoes do RS que NAO casaram (para ajustar na mao)
SELECT DISTINCT c.codigo, c.estacao
FROM chuva_estacao_mes c
LEFT JOIN estacao_municipio em ON em.codigo = c.codigo
WHERE c.uf = 'RS' AND em.codigo IS NULL
ORDER BY c.estacao;

-- municipios do RS com chuva em 2022 (ano da estiagem)
SELECT COUNT(DISTINCT cm.municipio_id) AS municipios_rs_2022
FROM chuva_municipio_mes cm
JOIN municipio m ON m.id = cm.municipio_id
JOIN estado e ON e.id = m.estado_id
WHERE e.nome = 'Rio Grande do Sul' AND cm.ano = 2022;
"""


def q(txt):
    return "'" + str(txt).replace("'", "''") + "'"


def gera_sql(df, caminho):
    d = df[(df.ano >= ANO_INI_SQL) & (df.ano <= ANO_FIM_SQL) & (df.horas_validas > 0) & df.chuva_mm.notna()].copy()
    # um nome por estacao: o do ano mais recente (o nome do INMET muda entre anos)
    ultimo = df.sort_values("ano").groupby("codigo")["estacao"].last()
    d["estacao"] = d["codigo"].map(ultimo)
    d["latitude"] = d["latitude"].round(5)
    d["longitude"] = d["longitude"].round(5)
    linhas = [
        f"({q(r.estacao)},{q(r.codigo)},{q(r.uf)},{r.latitude},{r.longitude},{r.ano},{r.mes},{r.chuva_mm},{r.horas_validas})"
        for r in d.itertuples()
    ]
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(SQL_ABERTURA.format(ini=ANO_INI_SQL, fim=ANO_FIM_SQL))
        f.write(f"-- {len(linhas)} linhas de dados\n")
        cols = "estacao,codigo,uf,latitude,longitude,ano,mes,chuva_mm,horas_validas"
        for k in range(0, len(linhas), 1000):
            f.write(f"INSERT INTO chuva_estacao_mes ({cols}) VALUES\n")
            f.write(",\n".join(linhas[k:k + 1000]) + ";\n")
        f.write(SQL_FECHAMENTO)
    return len(linhas)


def main(pasta, saida, ufs=None):
    """ufs: lista de siglas (ex.: ['RS','SC']) ou None para todos os estados."""
    partes = []
    for caminho in sorted(Path(pasta).glob("*.zip")):
        with zipfile.ZipFile(caminho) as z:
            nomes = []
            for n in z.namelist():
                m = re.search(r"INMET_[A-Z]+_([A-Z]{2})_", n)
                if m and n.upper().endswith(".CSV") and (ufs is None or m.group(1) in ufs):
                    nomes.append(n)
            print(f"{caminho.name}: {len(nomes)} estacoes")
            for n in nomes:
                r = le_estacao(z.read(n), n)
                if r is not None:
                    partes.append(r)
    if not partes:
        sys.exit("nenhuma estacao encontrada")
    out = pd.concat(partes, ignore_index=True)
    out = out[["estacao", "codigo", "uf", "latitude", "longitude", "ano", "mes", "chuva_mm", "horas_validas"]]
    out["chuva_mm"] = out["chuva_mm"].round(1)
    out.to_csv(saida, index=False, encoding="utf-8")
    print(f"pronto: {saida} ({len(out)} linhas)")
    caminho_sql = str(Path(saida).with_suffix(".sql"))
    n = gera_sql(out, caminho_sql)
    print(f"pronto: {caminho_sql} ({n} linhas de dados, anos {ANO_INI_SQL}-{ANO_FIM_SQL})")


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    ufs = [u.strip().upper() for u in sys.argv[3].split(",")] if len(sys.argv) == 4 else None
    main(sys.argv[1], sys.argv[2], ufs)