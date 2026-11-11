"""
Baixa os zips anuais de dados historicos do INMET.

Uso:
    python baixa_inmet.py                      -> 2012 a 2023 na pasta inmet_zips
    python baixa_inmet.py 2000 2025            -> de 2000 a 2025
    python baixa_inmet.py 2012 2023 minha_pasta

Nao precisa instalar nada (so biblioteca padrao do Python).
Se um zip ja existe na pasta e esta completo, ele e pulado.
"""
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

URL = "https://portal.inmet.gov.br/uploads/dadoshistoricos/{ano}.zip"
CABECALHO = {"User-Agent": "Mozilla/5.0 (trabalho academico BD2)"}


def tamanho_remoto(ano):
    req = urllib.request.Request(URL.format(ano=ano), headers=CABECALHO, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as r:
        return int(r.headers.get("Content-Length", 0))


def baixa(ano, pasta):
    destino = pasta / f"{ano}.zip"
    try:
        esperado = tamanho_remoto(ano)
    except urllib.error.HTTPError as e:
        print(f"{ano}: indisponivel (HTTP {e.code}), pulando")
        return False
    except Exception as e:
        print(f"{ano}: erro ao consultar ({e}), pulando")
        return False

    if destino.exists() and esperado and destino.stat().st_size == esperado:
        print(f"{ano}: ja baixado, pulando")
        return True

    for tentativa in range(1, 4):
        try:
            req = urllib.request.Request(URL.format(ano=ano), headers=CABECALHO)
            with urllib.request.urlopen(req, timeout=120) as r, open(destino, "wb") as f:
                total = int(r.headers.get("Content-Length", 0))
                lido = 0
                while True:
                    bloco = r.read(1024 * 256)
                    if not bloco:
                        break
                    f.write(bloco)
                    lido += len(bloco)
                    if total:
                        print(f"\r{ano}: {lido / 1e6:6.1f} / {total / 1e6:.1f} MB", end="", flush=True)
            print(f"\r{ano}: ok ({destino.stat().st_size / 1e6:.1f} MB)            ")
            return True
        except Exception as e:
            print(f"\n{ano}: falhou na tentativa {tentativa} ({e})")
            time.sleep(3)
    print(f"{ano}: desisti depois de 3 tentativas")
    return False


def main():
    ini = int(sys.argv[1]) if len(sys.argv) > 1 else 2012
    fim = int(sys.argv[2]) if len(sys.argv) > 2 else 2023
    pasta = Path(sys.argv[3] if len(sys.argv) > 3 else "inmet_zips")
    pasta.mkdir(exist_ok=True)
    ok = [a for a in range(ini, fim + 1) if baixa(a, pasta)]
    print(f"\nbaixados/prontos: {ok}")
    faltam = [a for a in range(ini, fim + 1) if a not in ok]
    if faltam:
        print(f"faltaram: {faltam} (rode de novo ou baixe esses no navegador)")


if __name__ == "__main__":
    main()