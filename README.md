# BD2 - Lavouras RS

Trabalho da disciplina de **Banco de Dados 2 (IBI-BDD002)** — Ciência da
Computação, IFRS Campus Ibirubá — 2026/2.

Análise da produção agrícola dos municípios do Rio Grande do Sul (soja, milho,
trigo, arroz e outras culturas) utilizando **Metabase** como ferramenta de
Business Intelligence, com dados extraídos do **IBGE/SIDRA**.

## 👥 Integrantes

- Mateus
- Kerlon
- Michel

## 🎯 Objetivo

Analisar a evolução da produção agrícola dos municípios do RS ao longo dos anos,
identificando:

- Municípios que se destacam como maiores produtores de cada cultura
- Evolução da área plantada, produtividade e valor da produção ao longo dos anos
- Impacto de eventos climáticos (ex.: estiagem de 2022) na produtividade
- Distribuição geográfica das culturas no estado
- Participação de cada cultura no valor total da produção agrícola do RS

## 🎯 Público-alvo

Gestores públicos municipais e órgãos de assistência técnica rural (Secretaria
da Agricultura, Emater/RS-Ascar), para direcionar políticas públicas, programas
de assistência técnica e resposta a eventos climáticos adversos.

## 🛠️ Ferramenta

**[Metabase](https://www.metabase.com/)** — plataforma open source de Business
Intelligence (licença AGPL v3), utilizada para consulta, visualização e criação
de dashboards a partir dos dados coletados.

## 📊 Base de Dados

**Produção Agrícola Municipal (PAM)** — IBGE/SIDRA

| Tabela | Tipo | Culturas |
|--------|------|----------|
| [1612](https://sidra.ibge.gov.br/tabela/1612) | Lavouras Temporárias | Soja, Milho, Cana, Arroz, Algodão, Feijão, Trigo |
| [1613](https://sidra.ibge.gov.br/tabela/1613) | Lavouras Permanentes | Café |

- Nível territorial: todos os municípios do Brasil
- Período: 1990 – 2023
- Variáveis coletadas: área plantada, área colhida, quantidade produzida e valor da produção

## 🗄️ Modelo de Banco de Dados

O banco é normalizado com as seguintes tabelas:

```
regiao ──< estado ──< municipio ──< producao_agricola >── produto
                                          │
                                       variavel
                                       unidade
```

- **regiao / estado / municipio** — dimensões geográficas
- **produto** — cultura agrícola (soja, milho, café, etc.)
- **variavel** — métrica coletada (área plantada, quantidade produzida, etc.)
- **unidade** — unidade de medida (Hectares, Toneladas, Mil Reais)
- **producao_agricola** — tabela fato com valor anual por município/produto/variável

## 📁 Scripts

| Arquivo | Descrição |
|---------|-----------|
| `Scripts/CarregaDados_v1.py` | Modelo inicial — extrai apenas lavouras temporárias (Tabela 1612), com produto e variável como texto direto na tabela fato |
| `Scripts/CarregaDados_v2.py` | Modelo atual — extração dinâmica de temporárias (1612) e permanentes (1613), com schema totalmente normalizado (tabelas `produto`, `variavel`, `unidade`) |

Para usar qualquer script, preencha a variável `DB_URI` com a string de conexão
PostgreSQL no formato `postgresql://usuario:senha@host:porta/banco`.

## 💾 Backup

O diretório `Backups/Banco/` contém o dump completo do banco de dados com todos
os dados do IBGE já carregados (`Backup_ibge.zip`), dispensando a necessidade de
rodar a ingestão do zero.

## 📄 Entregas

| Entrega | Descrição |
|---------|-----------|
| `entregas/3.7/` | Trabalho I — Parte I: apresentação sobre a ferramenta Metabase (objetivo, características, fluxo, módulos, licença e cases de sucesso) |
| `entregas/4.11/` | Trabalho I — Parte II: dashboard completo com visualizações no Metabase |

## 📚 Disciplina

Banco de Dados 2 (IBI-BDD002) — Prof. Edimar Manica  
IFRS Campus Ibirubá — Ciência da Computação — 4º Semestre — 2026/2
