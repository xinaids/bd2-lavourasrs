"""
Estimativa de produtividade da soja (Embrapa Agritec v2 /produtividade)
para os municipios do RS, safras 2012-2023, plantio fixo em 15/11.

Antes de rodar, defina as credenciais como variaveis de ambiente
(NUNCA coloque no codigo, no chat ou no GitHub):

  Windows (cmd):
    set EMBRAPA_KEY=seu_consumer_key
    set EMBRAPA_SECRET=seu_consumer_secret

  (ou, so para um teste rapido, um token ja gerado: set EMBRAPA_TOKEN=...)

Uso:
    python agritec_soja.py municipios.csv saida.csv

  municipios.csv = uma coluna "id" (codigo IBGE) por municipio, ex.:
    id
    4310009
    4314902

Gera:
  saida.csv  -> uma linha por municipio/safra (retomavel: se parar, rode de novo)
  saida.sql  -> cria a tabela clima_agritec e carrega os dados

Safra Y = plantio em 15/11 de Y-1 (mesma definicao da chuva do INMET).
So biblioteca padrao do Python.
"""
import base64
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://api.cnptia.embrapa.br/agritec/v2/produtividade"
TOKEN_URL = "https://api.cnptia.embrapa.br/token"

ID_CULTURA = 60          # soja
ID_CULTIVAR = 717334     # AV BUENA RR (ciclo medio); so fixa o coeficiente
CAD = 70                 # mm de agua disponivel no solo
EXPECTATIVA = 3.0        # t/ha, fixa: a variacao entre anos vem so do clima
SAFRA_INI, SAFRA_FIM = 2012, 2023
PAUSA = 0.4              # segundos entre chamadas

CAMPOS = ["municipio_id", "safra", "data_plantio", "dias", "prod_almejada",
          "prod_media_municipio", "fator_clima", "isna_medio", "dias_isna_baixo",
          "deficiencia_total", "chuva_total_mm", "dias_tmax_35"]


class Token:
    def __init__(self):
        self.fixo = os.environ.get("EMBRAPA_TOKEN")
        self.key = os.environ.get("EMBRAPA_KEY")
        self.secret = os.environ.get("EMBRAPA_SECRET")
        self.valor = self.fixo
        self.expira = 0
        if not (self.fixo or (self.key and self.secret)):
            sys.exit("Defina EMBRAPA_KEY e EMBRAPA_SECRET (ou EMBRAPA_TOKEN).")

    def obtem(self, forcar=False):
        if self.fixo:
            return self.fixo
        if forcar or not self.valor or time.time() > self.expira:
            cred = base64.b64encode(f"{self.key}:{self.secret}".encode()).decode()
            req = urllib.request.Request(
                TOKEN_URL, data=b"grant_type=client_credentials", method="POST",
                headers={"Authorization": f"Basic {cred}",
                         "Content-Type": "application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req, timeout=60) as r:
                dados = json.load(r)
            self.valor = dados["access_token"]
            self.expira = time.time() + int(dados.get("expires_in", 3600)) - 120
        return self.valor


def chama(token, municipio, data_plantio):
    q = urllib.parse.urlencode({
        "idCultura": ID_CULTURA, "idCultivar": ID_CULTIVAR,
        "codigoIBGE": municipio, "cad": CAD,
        "dataPlantio": data_plantio, "expectativaProdutividade": EXPECTATIVA})
    for tentativa in range(1, 4):
        try:
            req = urllib.request.Request(
                f"{BASE}?{q}",
                headers={"accept": "application/json",
                         "Authorization": f"Bearer {token.obtem()}"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)["data"]
        except urllib.error.HTTPError as e:
            corpo = e.read().decode("utf-8", "replace")[:300]
            if e.code == 401:
                token.obtem(forcar=True)
                continue
            if e.code == 429:
                print("  limite de chamadas atingido (429). Pare e rode de novo depois.")
                sys.exit(1)
            if e.code == 400:
                return {"erro": corpo}
            if e.code >= 500:
                # erro interno da API: nao insiste (cada tentativa gasta cota)
                return {"erro": f"HTTP {e.code}", "http": e.code}
            print(f"  HTTP {e.code}: {corpo} (tentativa {tentativa})")
        except Exception as e:
            print(f"  erro de rede: {e} (tentativa {tentativa})")
        time.sleep(3)
    return {"erro": "falhou 3 vezes"}


def resume(municipio, safra, data_plantio, d):
    """Transforma as series diarias em uma linha por municipio/safra."""
    almejada = d["produtividadeAlmejada"]
    media = d["produtividadeMediaMunicipio"]
    isna = d["isna"]
    n = len(almejada)
    return {
        "municipio_id": municipio,
        "safra": safra,
        "data_plantio": data_plantio,
        "dias": n,
        "prod_almejada": round(almejada[-1], 4),
        "prod_media_municipio": round(media[-1], 4),
        "fator_clima": round(almejada[-1] / EXPECTATIVA, 4),
        "isna_medio": round(sum(isna) / len(isna), 4),
        "dias_isna_baixo": sum(1 for v in isna if v < 0.5),
        "deficiencia_total": round(sum(d["deficienciaHidrica"]), 2),
        "chuva_total_mm": round(sum(d["precipitacao"]), 1),
        "dias_tmax_35": sum(1 for v in d["temperaturaMaxima"] if v >= 35),
    }


def le_municipios(caminho):
    with open(caminho, newline="", encoding="utf-8-sig") as f:
        return [int(l["id"]) for l in csv.DictReader(f)]


def le_feitos(caminho):
    if not Path(caminho).exists():
        return set()
    with open(caminho, newline="", encoding="utf-8") as f:
        return {(int(l["municipio_id"]), int(l["safra"])) for l in csv.DictReader(f)}


def gera_sql(csv_path, sql_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    with open(sql_path, "w", encoding="utf-8", newline="\n") as s:
        s.write("-- Estimativa Embrapa Agritec (soja, plantio 15/11) por municipio e safra.\n")
        s.write("-- fator_clima = produtividade almejada final / expectativa (3 t/ha); 1 = sem perda.\n")
        s.write("-- Seguro para rodar varias vezes: NAO apaga a tabela; so acrescenta linhas novas.\n")
        s.write("CREATE TABLE IF NOT EXISTS clima_agritec (\n"
                "  municipio_id int, safra int, data_plantio date, dias int,\n"
                "  prod_almejada numeric, prod_media_municipio numeric, fator_clima numeric,\n"
                "  isna_medio numeric, dias_isna_baixo int, deficiencia_total numeric,\n"
                "  chuva_total_mm numeric, dias_tmax_35 int,\n"
                "  PRIMARY KEY (municipio_id, safra));\n")
        for i in range(0, len(linhas), 200):
            bloco = linhas[i:i + 200]
            s.write("INSERT INTO clima_agritec VALUES\n")
            vals = []
            for l in bloco:
                vals.append("(%s,%s,'%s',%s,%s,%s,%s,%s,%s,%s,%s,%s)" % (
                    l["municipio_id"], l["safra"], l["data_plantio"], l["dias"],
                    l["prod_almejada"], l["prod_media_municipio"], l["fator_clima"],
                    l["isna_medio"], l["dias_isna_baixo"], l["deficiencia_total"],
                    l["chuva_total_mm"], l["dias_tmax_35"]))
            s.write(",\n".join(vals) + "\nON CONFLICT (municipio_id, safra) DO NOTHING;\n")
        s.write("\n-- conferencia: fator medio por safra\n"
                "SELECT safra, COUNT(*) AS municipios, ROUND(AVG(fator_clima),3) AS fator_medio,\n"
                "       ROUND(AVG(isna_medio),3) AS isna_medio\n"
                "FROM clima_agritec GROUP BY safra ORDER BY safra;\n")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    municipios = le_municipios(sys.argv[1])
    saida = sys.argv[2]
    feitos = le_feitos(saida)
    token = Token()
    falhas_path = Path(saida).with_suffix(".falhas.txt")
    sem_dados = set()
    if falhas_path.exists():
        sem_dados = {int(x) for x in falhas_path.read_text().split()}
        print(f"{len(sem_dados)} municipios ja marcados como sem dados na API: pulando.")
    pares = [(m, s) for m in municipios if m not in sem_dados
             for s in range(SAFRA_INI, SAFRA_FIM + 1) if (m, s) not in feitos]
    print(f"{len(municipios)} municipios, {len(pares)} chamadas a fazer "
          f"({len(feitos)} ja prontas).")
    novo = not Path(saida).exists()
    with open(saida, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        for i, (m, s) in enumerate(pares, 1):
            if m in sem_dados:
                continue
            data = f"{s - 1}-11-15"
            d = chama(token, m, data)
            if "erro" in d:
                print(f"[{i}/{len(pares)}] {m} safra {s}: ERRO {d['erro']}")
                if d.get("http", 0) >= 500 or "400" in str(d["erro"])[:40] or "dados-invalidos" in str(d["erro"]):
                    # sem calculo de soja para este municipio: nao gasta mais cota
                    sem_dados.add(m)
                    with open(falhas_path, "a") as ff:
                        ff.write(f"{m}\n")
                    print(f"  -> municipio {m} sem dados na API, pulando as demais safras")
                continue
            linha = resume(m, s, data, d)
            w.writerow(linha)
            f.flush()
            print(f"[{i}/{len(pares)}] {m} safra {s}: fator {linha['fator_clima']} "
                  f"isna {linha['isna_medio']}")
            time.sleep(PAUSA)
    sql = str(Path(saida).with_suffix(".sql"))
    gera_sql(saida, sql)
    print(f"\nprontos: {saida} e {sql}")


if __name__ == "__main__":
    main()