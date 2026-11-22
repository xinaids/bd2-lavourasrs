# Trabalho II — Dashboard de Análise da Produção Agrícola do RS

**Disciplina:** Banco de Dados 2 (IBI-BDD002)  
**Curso:** Ciência da Computação — Bacharelado  
**Campus:** IFRS Ibirubá  
**Grupo:** Metabase — Mateus, Kerlon e Michel  
**Docente:** Edimar Manica  
**Ferramenta:** Metabase (open source, licença AGPL v3)  
**Base de dados:** Produção Agrícola Municipal (PAM — IBGE/SIDRA, 1990–2025) e Série Climática Histórica / ENSO  
**Data de entrega:** 27/11/2026  

---

## 1. Público-Alvo

O dashboard é direcionado a **um único público: o(a) secretário(a) municipal de
Agricultura de um município do Rio Grande do Sul** (e a sua equipe), que decide
onde aplicar o orçamento e os programas de apoio ao produtor rural do
município. Ele(a) pode usar essas informações para:

- Comparar o seu município com os líderes de produção e de rendimento, e
  verificar o peso econômico de cada cultura no estado
- Direcionar programas de assistência técnica (por exemplo, em parceria com a
  Emater/RS-Ascar) para as culturas e regiões com queda de produtividade
- Planejar ações de resposta a eventos climáticos adversos (estiagem, excesso
  hídrico, geada) e fundamentar pedidos de apoio ao governo estadual e federal
- Subsidiar decisões sobre investimento em infraestrutura rural (armazenagem,
  irrigação, estradas) com base nos municípios e culturas de maior relevância
- Acompanhar a evolução da produção agrícola ano a ano, com dados oficiais e
  comparáveis, avaliando riscos associados a ciclos de *El Niño* e *La Niña*

O painel não é um relatório técnico para pesquisadores nem uma análise de
mercado para investidores: as perguntas e a linguagem foram pensadas para quem
decide as ações de agricultura do município.

---

## 2. Objetivo Geral do Dashboard

Analisar a evolução da produção agrícola dos municípios brasileiros ao longo de
**36 safras (1990 a 2025)**, com destaque para o Rio Grande do Sul, observando
área plantada, área perdida, produtividade (`kg/ha`), quantidade produzida
(`toneladas`) e valor bruto da produção (`R$`). Estruturado em **5 abas
temáticas** e **17 visualizações** (além de 5 indicadores-chave), o painel
permite filtrar dinamicamente por **Cultura**, **Estado**, **Ano**,
**Município**, **Região** e **Fenômeno Climático (ENSO)**, quantificando o
impacto histórico de eventos extremos (como as estiagens de 2020–2022 no Sul) e
oferecendo uma matriz preditiva de risco por cenário climático.

---

## 3. Ferramenta Utilizada

**Metabase** — plataforma open source de Business Intelligence licenciada sob
AGPL v3, utilizada para consulta, visualização e publicação de dashboards
interativos a partir dos dados armazenados no PostgreSQL.

**Objetivo da ferramenta:** permitir que qualquer pessoa de uma organização,
mesmo sem conhecimento técnico de banco de dados, faça perguntas aos dados,
crie visualizações e compartilhe dashboards, sem depender de um analista de BI
para cada consulta.

**Características da ferramenta:**

1. **Código aberto (AGPL v3)** — a Community Edition é gratuita; as edições Pro
   e Enterprise acrescentam recursos pagos.
2. **Instalação própria ou em nuvem** — pode ser executado em infraestrutura
   própria (Docker ou arquivo JAR) ou contratado como serviço (Metabase Cloud).
3. **Conexão com vários bancos de dados** — PostgreSQL, MySQL, SQL Server,
   BigQuery, MongoDB, entre outros; as consultas rodam no banco de origem, sem
   copiar os dados para o Metabase.
4. **Editor visual de perguntas (query builder)** — filtros, agrupamentos,
   ordenação e junções montados pela interface, sem escrever SQL.
5. **Editor de SQL nativo** — para consultas mais complexas, com variáveis e
   filtros de campo (*Field Filters*) que viram filtros do dashboard.
6. **Dashboards interativos multi-abas** — organização temática em múltiplas
   abas na mesma tela, permitindo conectar ou isolar filtros por cartão.
7. **Variedade de visualizações** — tabela, barras, linhas, área, dispersão,
   pizza/rosca, mapa coroplético, treemap, gráfico combinado com eixo duplo e
   formatação condicional.
8. **Modelo de dados com metadados** — permite descrever tabelas e colunas,
   definir tipos semânticos (categoria, moeda, coordenadas) e relacionamentos
   entre tabelas.
9. **Exploração automática (X-ray)** — gera automaticamente uma análise
   exploratória de uma tabela ou de uma pergunta.
10. **Alertas e assinaturas** — envio de gráficos e dashboards por e-mail ou
    Slack, em horários programados ou quando uma condição é atingida.
11. **Organização e permissões** — perguntas e dashboards agrupados em
    coleções, com permissões por grupos de usuários.
12. **Compartilhamento e exportação** — links públicos, incorporação em outras
    páginas, exportação dos resultados em CSV, XLSX e JSON, e API REST para
    automação.

---

## 4. Arquitetura de Dados e Views Materializadas (PostgreSQL)

A base relacional principal (`producao_agricola`) concentra aproximadamente
**2,9 milhões de registros** distribuídos entre municípios, culturas, anos e
variáveis do IBGE/SIDRA, complementada pela tabela estadual `clima_historico`
(precipitação anual em `mm` e classificação anual do fenômeno ENSO: *El Niño*,
*La Niña* e *Neutro*).

Para garantir tempo de resposta interativo nos gráficos analíticos e evitar
distorções estatísticas ao cruzar granularidades diferentes (dados agrícolas
municipais × dados climáticos estaduais), foram criadas **duas Views
Materializadas** no PostgreSQL antes da construção das consultas do dashboard:

1. **`mv_historico_expansao_perda`** — consolida anualmente, por Unidade da
   Federação (`uf`) e `cultura` (além da linha totalizadora `'Todas (Total do
   Estado)'`), as métricas físicas (`area_plantada_ha`, `area_colhida_ha`,
   `producao_toneladas`), o fenômeno ENSO vigente, a área perdida não colhida
   (`area_perdida_ha`), a variação anual de área plantada
   (`taxa_investimento_yoy_pct`) e a aceleração da taxa de perda em pontos
   percentuais (`aceleracao_perda_pp`).
2. **`mv_matriz_cenarios_enso`** — agrega toda a série histórica por tripla
   `(uf, cultura, fenomeno_enso)`, calculando médias históricas de
   precipitação, investimento anual, perda em hectares, percentual médio de
   quebra, aceleração da perda e safra média esperada em toneladas.

### Script SQL de Criação das Views Materializadas

Execute o script abaixo no PostgreSQL para criar e indexar as duas views
materializadas necessárias para os gráficos **6, 7, 9 e 14 a 17**:

```sql
-- ============================================================================
-- 1. VIEW MATERIALIZADA: HISTÓRICO DE EXPANSÃO, PRODUTIVIDADE E PERDAS
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS mv_matriz_cenarios_enso;
DROP MATERIALIZED VIEW IF EXISTS mv_historico_expansao_perda;

CREATE MATERIALIZED VIEW mv_historico_expansao_perda AS
WITH dados_base AS (
    SELECT
        pa.ano,
        e.sigla AS uf,
        p.nome AS cultura,
        SUM(CASE WHEN pa.variavel_id IN (109, 2313) THEN pa.valor ELSE 0 END) AS area_plantada_ha,
        SUM(CASE WHEN pa.variavel_id = 216 THEN pa.valor ELSE 0 END) AS area_colhida_ha,
        SUM(CASE WHEN pa.variavel_id = 214 THEN pa.valor ELSE 0 END) AS producao_toneladas
    FROM producao_agricola pa
    INNER JOIN produto p ON pa.produto_id = p.id
    INNER JOIN municipio m ON pa.municipio_id = m.id
    INNER JOIN estado e ON m.estado_id = e.id
    WHERE pa.variavel_id IN (109, 2313, 216, 214)
    GROUP BY GROUPING SETS (
        (pa.ano, e.sigla, p.nome),
        (pa.ano, e.sigla)
    )
),
consolidado AS (
    SELECT
        d.ano,
        d.uf,
        COALESCE(d.cultura, 'Todas (Total do Estado)') AS cultura,
        c.fenomeno_enso,
        d.area_plantada_ha,
        d.area_colhida_ha,
        GREATEST(d.area_plantada_ha - d.area_colhida_ha, 0) AS area_perdida_ha,
        d.producao_toneladas
    FROM dados_base d
    LEFT JOIN estado e ON d.uf = e.sigla
    LEFT JOIN clima_historico c ON c.estado_id = e.id AND c.ano = d.ano
)
SELECT
    ano,
    uf,
    cultura,
    fenomeno_enso,
    area_plantada_ha,
    area_colhida_ha,
    area_perdida_ha,
    producao_toneladas,
    ROUND(
        ((area_plantada_ha - LAG(area_plantada_ha) OVER (PARTITION BY uf, cultura ORDER BY ano)) /
        NULLIF(LAG(area_plantada_ha) OVER (PARTITION BY uf, cultura ORDER BY ano), 0)) * 100,
        2
    ) AS taxa_investimento_yoy_pct,
    ROUND(
        ((area_perdida_ha / NULLIF(area_plantada_ha, 0)) * 100) -
        ((LAG(area_perdida_ha) OVER (PARTITION BY uf, cultura ORDER BY ano) /
          NULLIF(LAG(area_plantada_ha) OVER (PARTITION BY uf, cultura ORDER BY ano), 0)) * 100),
        2
    ) AS aceleracao_perda_pp
FROM consolidado;

CREATE INDEX idx_mv_hist_uf_cultura_ano
    ON mv_historico_expansao_perda (uf, cultura, ano);

-- ============================================================================
-- 2. VIEW MATERIALIZADA: MATRIZ PREDITIVA DE CENÁRIOS CLIMÁTICOS (ENSO)
-- ============================================================================
CREATE MATERIALIZED VIEW mv_matriz_cenarios_enso AS
WITH series_com_yoy AS (
    SELECT
        h.uf,
        h.cultura,
        h.fenomeno_enso,
        h.ano,
        c.precipitacao_anual_mm,
        h.taxa_investimento_yoy_pct,
        h.area_plantada_ha,
        h.area_perdida_ha,
        (h.area_perdida_ha / NULLIF(h.area_plantada_ha, 0)) * 100 AS quebra_lavoura_pct,
        ((h.area_perdida_ha - LAG(h.area_perdida_ha) OVER (PARTITION BY h.uf, h.cultura ORDER BY h.ano)) /
         NULLIF(LAG(h.area_perdida_ha) OVER (PARTITION BY h.uf, h.cultura ORDER BY h.ano), 0)) * 100 AS crescimento_perda_yoy_pct,
        h.aceleracao_perda_pp,
        h.producao_toneladas
    FROM mv_historico_expansao_perda h
    INNER JOIN estado e ON h.uf = e.sigla
    LEFT JOIN clima_historico c ON c.estado_id = e.id AND c.ano = h.ano
    WHERE h.fenomeno_enso IS NOT NULL
)
SELECT
    uf,
    cultura,
    fenomeno_enso,
    COUNT(DISTINCT ano) AS anos_ocorrencia,
    ROUND(AVG(precipitacao_anual_mm)::numeric, 2) AS chuva_media_mm,
    ROUND(AVG(taxa_investimento_yoy_pct)::numeric, 2) AS taxa_mestre_investimento_pct,
    ROUND(AVG(area_perdida_ha)::numeric, 0) AS perda_media_ha,
    ROUND(AVG(quebra_lavoura_pct)::numeric, 2) AS quebra_media_lavoura_pct,
    ROUND(AVG(crescimento_perda_yoy_pct)::numeric, 2) AS crescimento_medio_perda_yoy_pct,
    ROUND(AVG(aceleracao_perda_pp)::numeric, 2) AS aceleracao_media_perda_pp,
    ROUND(AVG(producao_toneladas)::numeric, 0) AS safra_media_toneladas
FROM series_com_yoy
GROUP BY uf, cultura, fenomeno_enso;

CREATE INDEX idx_mv_matriz_uf_cultura_enso
    ON mv_matriz_cenarios_enso (uf, cultura, fenomeno_enso);
```

---

## 5. Estrutura e Visualizações do Dashboard

O dashboard é organizado em **5 abas temáticas**, totalizando **5 indicadores
(KPIs)**, **1 cartão dinâmico de contexto (Legenda)** e **17 gráficos**
distribuídos de forma equilibrada (entre 2 e 4 visualizações por aba).

### Escopo dos Filtros por Aba

Para preservar a coerência analítica — evitando, por exemplo, que um filtro de
ano único mutile gráficos de série temporal —, cada filtro possui visibilidade e
conexão configuradas por aba:

| Filtro no Painel | Aba 1 (`Visão Geral`) | Aba 2 (`Evolução Histórica`) | Aba 3 (`Detalhamento Geográfico`) | Aba 4 (`Clima & Pluviometria`) | Aba 5 (`Risco, Perdas e Cenários`) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Cultura** | Visível | Visível | Visível | Visível *(desconectado dos mapas de chuva)* | Visível |
| **Estado (UF)** | Visível | Visível | Visível | Visível | Visível |
| **Anos** | Visível | *Oculto* | Visível | Visível *(conectado ao Mapa Hídrico)* | *Oculto* |
| **Município** | *Oculto* | *Oculto* | Visível | *Oculto* | *Oculto* |
| **Fenômeno ENSO** | *Oculto* | *Oculto* | *Oculto* | *Oculto* | Visível *(conectado à Matriz Preditiva)* |

---

### Indicadores-Chave (KPIs) e Legenda Dinâmica

Presentes no topo da **Aba 1 (`Visão Geral e Desempenho`)** — enquanto o
cartão **Legenda** acompanha todas as abas exibindo o recorte ativo (ex.:
*Todas as culturas • 1990 a 2025 (36 safras)*):

| Indicador (KPI) | Valor Agregado (1990–2025) | Variável IBGE / Fórmula |
| :--- | :---: | :--- |
| **Valor Total de Produção em Reais** | `R$ 6,6T` | `SUM(valor) * 1000` (`variavel_id = 215` — Mil Reais) |
| **Quantidade Produzida em Toneladas** | `25,2B T` | `SUM(valor)` (`variavel_id = 214` — Toneladas) |
| **Área Plantada em Hectares** | `2,1B Ha` | `SUM(valor)` (`variavel_id IN (109, 2313)`) |
| **Rendimento Médio de Produção** | `12.074 Kg/Ha` | `(SUM(producao_t) * 1000) / NULLIF(SUM(area_colhida_ha), 0)` |
| **Quantidade de Municípios Produtores** | `5.550` | `COUNT(DISTINCT municipio_id)` com produção `> 0` |

---

### Resumo dos 17 Gráficos por Aba

| Aba | Nº | Gráfico | Tipo de Visualização | Fonte Principal |
| :--- | :-: | :--- | :--- | :--- |
| **1. Visão Geral** | 1 | Participação das culturas no uso do solo | Rosca (Donut) | `producao_agricola` |
| **1. Visão Geral** | 2 | Comparativo de valor de produção | Colunas (Barras verticais) | `producao_agricola` |
| **2. Evolução Histórica** | 3 | Relação histórica Volume produzido × Área plantada | Combinado (Barras + Linha, 2 eixos) | `producao_agricola` |
| **2. Evolução Histórica** | 4 | Evolução de Produção | Linhas | `producao_agricola` |
| **2. Evolução Histórica** | 5 | Evolução comparativa de culturas | Linhas múltiplas | `producao_agricola` |
| **2. Evolução Histórica** | 6 | Matriz de crescimento regional (quinquênios) | Tabela com escala de cores | `mv_historico_expansao_perda` |
| **3. Detalh. Geográfico** | 7 | Mapa de Eficiência de Cultura | Mapa coroplético (Brasil/UF) | `mv_historico_expansao_perda` |
| **3. Detalh. Geográfico** | 8 | Ranking de Municípios Polos — Top 10 | Colunas (Barras verticais) | `producao_agricola` |
| **3. Detalh. Geográfico** | 9 | Dispersão de Área vs. Eficiência | Dispersão (Scatter plot) | `mv_historico_expansao_perda` |
| **3. Detalh. Geográfico** | 10 | Concentração de Riqueza Agrícola | Mapa de árvore (Treemap) | `producao_agricola` |
| **4. Clima & Pluviometria** | 11 | Mapa de Impacto Hídrico | Mapa coroplético (Brasil/UF) | `clima_historico` |
| **4. Clima & Pluviometria** | 12 | Comparativo de Impacto (Médias por Fenômeno) | Colunas (Barras verticais) | `clima_historico` |
| **4. Clima & Pluviometria** | 13 | Linha do Tempo (Chuva vs. Fenômeno) | Colunas agrupadas por evento | `clima_historico` |
| **4. Clima & Pluviometria** | 14 | Chuva vs. Quebra de Safra | Combinado (2 linhas, 2 eixos) | `clima_historico` + `mv_historico_expansao_perda` |
| **5. Risco & Cenários** | 15 | Evolução Física: Área Plantada vs. Área Perdida | Colunas agrupadas (2 eixos) | `mv_historico_expansao_perda` |
| **5. Risco & Cenários** | 16 | Expansão de Campo (%) vs. Aceleração da Perda (p.p.) | Linhas (2 eixos) | `mv_historico_expansao_perda` |
| **5. Risco & Cenários** | 17 | Matriz Preditiva de Risco e Investimento (ENSO) | Tabela analítica com escala de cores | `mv_matriz_cenarios_enso` |

---

### Aba 1 — Visão Geral e Desempenho

#### Gráfico 1 — Participação das culturas no uso do solo

**O quê:** participação percentual e absoluta (em hectares) de cada cultura na
área cultivada total (`variavel_id IN (109, 2313)`, contemplando culturas
temporárias e área destinada à colheita de culturas permanentes).  
**Como:** gráfico de rosca (donut) com o total acumulado no centro e o
percentual de cada lavoura na legenda.

![Gráfico 1 — Participação das culturas no uso do solo](imagens/image1.png)

**Por quê:** evidencia o grau de concentração territorial do agronegócio (como
o domínio de Soja com 40,71%, Milho com 25,71% e Cana-de-açúcar com 12,65%) e
permite ao gestor avaliar a necessidade de políticas de diversificação.

**SQL (registro):**

```sql
SELECT
    produto.nome AS cultura,
    SUM(producao_agricola.valor) AS area_plantada_ha
FROM producao_agricola
INNER JOIN produto ON producao_agricola.produto_id = produto.id
INNER JOIN municipio ON producao_agricola.municipio_id = municipio.id
INNER JOIN estado ON municipio.estado_id = estado.id
WHERE producao_agricola.variavel_id IN (109, 2313)
  [[ AND {{filtro_produto}} ]]
  [[ AND {{filtro_estado}} ]]
  [[ AND {{filtro_ano}} ]]
GROUP BY produto.id, produto.nome
HAVING SUM(producao_agricola.valor) > 0
ORDER BY area_plantada_ha DESC;
```

---

#### Gráfico 2 — Comparativo de valor de produção

**O quê:** valor bruto da produção em reais (`R$`) por cultura (`variavel_id =
215` convertida de Mil Reais para Reais), ordenado do maior para o menor.  
**Como:** gráfico de colunas coloridas por cultura com rótulos de valores no
topo.

![Gráfico 2 — Comparativo de valor de produção](imagens/image2.png)

**Por quê:** contrapõe o peso econômico ao peso físico das lavouras, mostrando
quais cadeias geram maior retorno financeiro para o estado ou município.

**SQL (registro):**

```sql
SELECT
    produto.nome AS eixo_agrupamento,
    produto.nome AS cultura,
    SUM(producao_agricola.valor) * 1000 AS valor_total_producao
FROM producao_agricola
INNER JOIN produto ON producao_agricola.produto_id = produto.id
INNER JOIN municipio ON producao_agricola.municipio_id = municipio.id
INNER JOIN estado ON municipio.estado_id = estado.id
WHERE producao_agricola.variavel_id = 215
  [[ AND {{filtro_produto}} ]]
  [[ AND {{filtro_estado}} ]]
  [[ AND {{filtro_ano}} ]]
GROUP BY produto.id, produto.nome
HAVING SUM(producao_agricola.valor) > 0
ORDER BY valor_total_producao DESC;
```

---

### Aba 2 — Evolução Histórica

#### Gráfico 3 — Relação histórica Volume produzido × Área plantada

**O quê:** comparação anual entre a quantidade produzida em toneladas (eixo Y
esquerdo) e a área plantada em hectares (eixo Y direito) de 1990 a 2025.  
**Como:** gráfico combinado com barras azuis para toneladas e linha verde com
marcadores para hectares.

![Gráfico 3 — Relação histórica Volume produzido × Área plantada](imagens/image3.png)

**Por quê:** permite distinguir se o crescimento da produção decorreu de
expansão territorial ou de ganhos tecnológicos de produtividade por hectare.

**SQL (registro):**

```sql
SELECT
    producao_agricola.ano AS ano_safra,
    SUM(CASE WHEN producao_agricola.variavel_id = 214 THEN producao_agricola.valor ELSE 0 END) AS quantidade_produzida,
    SUM(CASE WHEN producao_agricola.variavel_id IN (109, 2313) THEN producao_agricola.valor ELSE 0 END) AS area_plantada
FROM producao_agricola
INNER JOIN produto ON producao_agricola.produto_id = produto.id
INNER JOIN municipio ON producao_agricola.municipio_id = municipio.id
INNER JOIN estado ON municipio.estado_id = estado.id
WHERE producao_agricola.variavel_id IN (214, 109, 2313)
  [[ AND {{filtro_produto}} ]]
  [[ AND {{filtro_estado}} ]]
GROUP BY producao_agricola.ano
ORDER BY producao_agricola.ano ASC;
```

---

#### Gráfico 4 — Evolução de Produção

**O quê:** série temporal do volume físico colhido (em toneladas) entre 1990 e
2025.  
**Como:** gráfico de linhas com marcadores anuais.

![Gráfico 4 — Evolução de Produção](imagens/image4.png)

**Por quê:** destaca a trajetória estrutural da safra e evidencia visualmente
quedas abruptas causadas por choques climáticos (como as quebras de 2005, 2012
e 2022 no Rio Grande do Sul).

**SQL (registro):**

```sql
SELECT
    producao_agricola.ano AS ano,
    SUM(producao_agricola.valor) AS quantidade_total
FROM producao_agricola
INNER JOIN produto ON producao_agricola.produto_id = produto.id
INNER JOIN municipio ON producao_agricola.municipio_id = municipio.id
INNER JOIN estado ON municipio.estado_id = estado.id
WHERE producao_agricola.variavel_id = 214
  [[ AND {{filtro_produto}} ]]
  [[ AND {{filtro_estado}} ]]
GROUP BY producao_agricola.ano
ORDER BY producao_agricola.ano ASC;
```

---

#### Gráfico 5 — Evolução comparativa de culturas

**O quê:** evolução histórica do valor da produção (`R$`) desagregada por
cultura de 1990 a 2025.  
**Como:** gráfico de linhas múltiplas coloridas por cultura.

![Gráfico 5 — Evolução comparativa de culturas](imagens/image5.png)

**Por quê:** demonstra a transformação econômica do campo ao longo de três
décadas, evidenciando o salto financeiro da soja e do milho a partir de 2020.

**SQL (registro):**

```sql
SELECT
    producao_agricola.ano AS ano,
    produto.nome AS cultura,
    SUM(producao_agricola.valor) * 1000 AS valor_producao
FROM producao_agricola
INNER JOIN produto ON producao_agricola.produto_id = produto.id
INNER JOIN municipio ON producao_agricola.municipio_id = municipio.id
INNER JOIN estado ON municipio.estado_id = estado.id
WHERE producao_agricola.variavel_id = 215
  [[ AND {{filtro_produto}} ]]
  [[ AND {{filtro_estado}} ]]
GROUP BY producao_agricola.ano, produto.nome
ORDER BY producao_agricola.ano ASC, valor_producao DESC;
```

---

#### Gráfico 6 — Matriz de crescimento regional

**O quê:** volume produzido (em toneladas) por estado agrupado em 7 intervalos
quinquenais (`1990 - 1995` a `2021 a 2025`), com filtro adicional por
macrorregião ou fronteira agrícola (`MATOPIBA`, `SEALBA`, `AMACRO`).  
**Como:** tabela matricial com formatação condicional (gradiente de cor por
intensidade de produção) lida diretamente da view materializada
`mv_historico_expansao_perda`.

![Gráfico 6 — Matriz de crescimento regional](imagens/image6.png)

**Por quê:** permite comparar o avanço das novas fronteiras agrícolas
(Centro-Oeste e MATOPIBA) frente às regiões produtoras tradicionais (Sul e
Sudeste).

**SQL (registro):**

```sql
SELECT 
    estado.nome AS estado,
    ROUND(SUM(CASE WHEN mv_historico_expansao_perda.ano BETWEEN 1990 AND 1995 THEN mv_historico_expansao_perda.producao_toneladas ELSE 0 END), 0) AS "1990 - 1995",
    ROUND(SUM(CASE WHEN mv_historico_expansao_perda.ano BETWEEN 1996 AND 2000 THEN mv_historico_expansao_perda.producao_toneladas ELSE 0 END), 0) AS "1996 - 2000",
    ROUND(SUM(CASE WHEN mv_historico_expansao_perda.ano BETWEEN 2001 AND 2005 THEN mv_historico_expansao_perda.producao_toneladas ELSE 0 END), 0) AS "2001 - 2005",
    ROUND(SUM(CASE WHEN mv_historico_expansao_perda.ano BETWEEN 2006 AND 2010 THEN mv_historico_expansao_perda.producao_toneladas ELSE 0 END), 0) AS "2006 - 2010",
    ROUND(SUM(CASE WHEN mv_historico_expansao_perda.ano BETWEEN 2011 AND 2015 THEN mv_historico_expansao_perda.producao_toneladas ELSE 0 END), 0) AS "2011 - 2015",
    ROUND(SUM(CASE WHEN mv_historico_expansao_perda.ano BETWEEN 2016 AND 2020 THEN mv_historico_expansao_perda.producao_toneladas ELSE 0 END), 0) AS "2016 - 2020",
    ROUND(SUM(CASE WHEN mv_historico_expansao_perda.ano >= 2021 THEN mv_historico_expansao_perda.producao_toneladas ELSE 0 END), 0) AS "2021 a 2025"
FROM mv_historico_expansao_perda
INNER JOIN estado ON mv_historico_expansao_perda.uf = estado.sigla
WHERE mv_historico_expansao_perda.cultura <> 'Todas (Total do Estado)'
  [[ AND {{filtro_estado}} ]]
  [[ AND {{filtro_produto}} ]]
  [[ AND (
      ('Norte' IN ({{filtro_regiao}}) AND estado.nome IN ('Acre', 'Amapá', 'Amazonas', 'Pará', 'Rondônia', 'Roraima', 'Tocantins')) OR
      ('Nordeste' IN ({{filtro_regiao}}) AND estado.nome IN ('Alagoas', 'Bahia', 'Ceará', 'Maranhão', 'Paraíba', 'Pernambuco', 'Piauí', 'Rio Grande do Norte', 'Sergipe')) OR
      ('Centro-Oeste' IN ({{filtro_regiao}}) AND estado.nome IN ('Goiás', 'Mato Grosso', 'Mato Grosso do Sul', 'Distrito Federal')) OR
      ('Sudeste' IN ({{filtro_regiao}}) AND estado.nome IN ('Espírito Santo', 'Minas Gerais', 'Rio de Janeiro', 'São Paulo')) OR
      ('Sul' IN ({{filtro_regiao}}) AND estado.nome IN ('Paraná', 'Rio Grande do Sul', 'Santa Catarina')) OR
      ('MATOPIBA' IN ({{filtro_regiao}}) AND estado.nome IN ('Maranhão', 'Tocantins', 'Piauí', 'Bahia')) OR
      ('SEALBA' IN ({{filtro_regiao}}) AND estado.nome IN ('Sergipe', 'Alagoas', 'Bahia')) OR
      ('AMACRO' IN ({{filtro_regiao}}) AND estado.nome IN ('Amazonas', 'Acre', 'Rondônia'))
  ) ]]
GROUP BY estado.nome
HAVING SUM(mv_historico_expansao_perda.producao_toneladas) > 0
ORDER BY estado.nome ASC;
```

---

### Aba 3 — Detalhamento Geográfico

#### Gráfico 7 — Mapa de Eficiência de Cultura

**O quê:** rendimento médio ponderado (`kg/ha`) por Unidade da Federação,
calculado pela razão entre produção total em quilogramas e área colhida em
hectares.  
**Como:** mapa coroplético do Brasil dividido por estados.

![Gráfico 7 — Mapa de Eficiência de Cultura](imagens/image7.png)

**Por quê:** permite comparar instantaneamente a eficiência agronômica do Rio
Grande do Sul frente aos demais estados produtores.

**SQL (registro):**

```sql
SELECT
    mv_historico_expansao_perda.uf AS estado,
    ROUND(
        (SUM(mv_historico_expansao_perda.producao_toneladas) * 1000) /
        NULLIF(SUM(mv_historico_expansao_perda.area_colhida_ha), 0),
        0
    ) AS rendimento_medio_kg_ha
FROM mv_historico_expansao_perda
WHERE mv_historico_expansao_perda.cultura <> 'Todas (Total do Estado)'
  [[ AND {{filtro_estado}} ]]
  [[ AND {{filtro_produto}} ]]
  [[ AND {{filtro_ano}} ]]
GROUP BY mv_historico_expansao_perda.uf
HAVING SUM(mv_historico_expansao_perda.area_colhida_ha) > 0
ORDER BY rendimento_medio_kg_ha DESC;
```

---

#### Gráfico 8 — Ranking de Municípios Polos — Top 10

**O quê:** os 10 municípios com maior volume produzido (em toneladas) de acordo
com os filtros de cultura, estado, ano e município selecionados.  
**Como:** gráfico de colunas com cores distintas por município e rótulos de
volume no topo.

![Gráfico 8 — Ranking de Municípios Polos — Top 10](imagens/image8.png)

**Por quê:** desce da escala estadual para a municipal, identificando os polos
produtores que lideram a safra e servem de parâmetro comparativo para a gestão
local.

**SQL (registro):**

```sql
SELECT
    municipio.nome || ' - ' || estado.sigla AS municipio_estado,
    municipio.nome || ' - ' || estado.sigla AS municipio_legenda,
    SUM(producao_agricola.valor) AS quantidade_produzida_toneladas
FROM producao_agricola
INNER JOIN produto ON producao_agricola.produto_id = produto.id
INNER JOIN municipio ON producao_agricola.municipio_id = municipio.id
INNER JOIN estado ON municipio.estado_id = estado.id
WHERE producao_agricola.variavel_id = 214
  [[ AND {{filtro_produto}} ]]
  [[ AND {{filtro_estado}} ]]
  [[ AND {{filtro_ano}} ]]
  [[ AND {{filtro_municipio}} ]]
GROUP BY municipio.id, municipio.nome, estado.sigla
HAVING SUM(producao_agricola.valor) > 0
ORDER BY quantidade_produzida_toneladas DESC
LIMIT 10;
```

---

#### Gráfico 9 — Dispersão de Área vs. Eficiência

**O quê:** cruzamento entre área plantada em hectares (eixo X) e rendimento
médio em `kg/ha` (eixo Y) para cada estado produtor.  
**Como:** gráfico de dispersão (scatter plot) com uma bolha por estado.

![Gráfico 9 — Dispersão de Área vs. Eficiência](imagens/image9.png)

**Por quê:** diferencia estados extensivos de estados intensivos em
tecnologia, mostrando onde há oportunidade de elevar a produtividade sem
depender apenas de abertura de novas áreas.

**SQL (registro):**

```sql
SELECT 
    estado.nome AS estado,
    SUM(mv_historico_expansao_perda.area_plantada_ha) AS area_plantada,
    ROUND(
        (SUM(mv_historico_expansao_perda.producao_toneladas) * 1000) /
        NULLIF(SUM(mv_historico_expansao_perda.area_colhida_ha), 0),
        0
    ) AS rendimento_medio_kg_ha
FROM mv_historico_expansao_perda
INNER JOIN estado ON mv_historico_expansao_perda.uf = estado.sigla
WHERE mv_historico_expansao_perda.cultura <> 'Todas (Total do Estado)'
  [[ AND {{filtro_estado}} ]]
  [[ AND {{filtro_produto}} ]]
  [[ AND {{filtro_ano}} ]]
GROUP BY estado.nome
HAVING SUM(mv_historico_expansao_perda.area_plantada_ha) > 0
ORDER BY area_plantada DESC;
```

---

#### Gráfico 10 — Concentração de Riqueza Agrícola

**O quê:** participação proporcional de cada estado no valor bruto total da
produção nacional (`R$`).  
**Como:** mapa de árvore (treemap) exibindo o valor absoluto e o percentual de
cada UF (liderado por MT com 19,69%, SP com 13,32%, PR com 12,44%, MG com
11,27% e RS com 9,92%).

![Gráfico 10 — Concentração de Riqueza Agrícola](imagens/image10.png)

**Por quê:** ilustra a concentração econômica do agronegócio brasileiro e
dimensiona o peso financeiro do Rio Grande do Sul na balança agrícola
nacional.

**SQL (registro):**

```sql
SELECT
    estado.sigla AS estado,
    SUM(producao_agricola.valor) * 1000 AS valor_total_producao
FROM producao_agricola
INNER JOIN produto ON producao_agricola.produto_id = produto.id
INNER JOIN municipio ON producao_agricola.municipio_id = municipio.id
INNER JOIN estado ON municipio.estado_id = estado.id
WHERE producao_agricola.variavel_id = 215
  [[ AND {{filtro_produto}} ]]
  [[ AND {{filtro_estado}} ]]
  [[ AND {{filtro_ano}} ]]
GROUP BY estado.sigla
HAVING SUM(producao_agricola.valor) > 0
ORDER BY valor_total_producao DESC;
```

---

### Aba 4 — Clima & Pluviometria

#### Gráfico 11 — Mapa de Impacto Hídrico

**O quê:** distribuição espacial da precipitação média anual (em milímetros)
pelos estados brasileiros, filtrável por ano e estado.  
**Como:** mapa coroplético do Brasil colorido por faixa pluviométrica (`mm`).

![Gráfico 11 — Mapa de Impacto Hídrico](imagens/image11.png)

**Por quê:** permite inspecionar a distribuição geográfica das chuvas em anos
específicos de crise hídrica ou excesso pluviométrico.

**SQL (registro):**

```sql
SELECT 
    estado.sigla,
    ROUND(AVG(clima_historico.precipitacao_anual_mm)::numeric, 2) AS precipitacao_media_mm
FROM clima_historico
INNER JOIN estado 
    ON clima_historico.estado_id = estado.id
WHERE 1=1
  [[ AND {{filtro_estado}} ]]
  [[ AND {{ano_analise}} ]]
GROUP BY estado.sigla
ORDER BY precipitacao_media_mm DESC;
```

---

#### Gráfico 12 — Comparativo de Impacto (Médias por Fenômeno)

**O quê:** precipitação média histórica (`mm`) agrupada pelas três fases do
ciclo ENSO (*El Niño*, *La Niña* e *Neutro*).  
**Como:** gráfico de colunas verticais comparando os três regimes climáticos.

![Gráfico 12 — Comparativo de Impacto (Médias por Fenômeno)](imagens/image12.png)

**Por quê:** quando filtrado para um estado específico como o Rio Grande do
Sul, evidencia numericamente o déficit hídrico característico de anos de
*La Niña* frente ao aumento de chuvas em anos de *El Niño*.

**SQL (registro):**

```sql
SELECT 
    clima_historico.fenomeno_enso, 
    ROUND(AVG(clima_historico.precipitacao_anual_mm)::numeric, 2) AS precipitacao_media_mm
FROM clima_historico
INNER JOIN estado 
    ON clima_historico.estado_id = estado.id
WHERE clima_historico.fenomeno_enso IS NOT NULL
  [[ AND {{sigla_estado}} ]]
GROUP BY clima_historico.fenomeno_enso
ORDER BY precipitacao_media_mm DESC;
```

---

#### Gráfico 13 — Linha do Tempo (Chuva vs. Fenômeno)

**O quê:** série histórica anual da precipitação média (`mm`) colorida conforme
o fenômeno ENSO predominante em cada ano (`Neutro`, `El Niño` e `La Niña`).  
**Como:** gráfico de colunas cronológicas categorizadas por evento climático.

![Gráfico 13 — Linha do Tempo (Chuva vs. Fenômeno)](imagens/image13.png)

**Por quê:** evidencia os ciclos plurianuais de estiagem e excesso hídrico ao
longo das décadas, permitindo correlacionar visualmente sequências de *La Niña*
com quedas de safra.

**SQL (registro):**

```sql
SELECT 
    clima_historico.ano, 
    ROUND(AVG(clima_historico.precipitacao_anual_mm)::numeric, 2) AS precipitacao_media_mm, 
    clima_historico.fenomeno_enso
FROM clima_historico
INNER JOIN estado 
    ON clima_historico.estado_id = estado.id
WHERE clima_historico.fenomeno_enso IS NOT NULL
  [[ AND {{sigla_estado}} ]]
GROUP BY clima_historico.ano, clima_historico.fenomeno_enso
ORDER BY clima_historico.ano ASC;
```

---

#### Gráfico 14 — Chuva vs. Quebra de Safra

**O quê:** sobreposição da precipitação média anual (`mm`, eixo esquerdo) com
o volume total produzido em toneladas (eixo direito), calculados em CTEs
separadas para evitar multiplicação cartesiana entre municípios e estados.  
**Como:** gráfico combinado de duas linhas com eixos independentes.

![Gráfico 14 — Chuva vs. Quebra de Safra](imagens/image14.png)

**Por quê:** comprova visualmente a sensibilidade hídrica das lavouras,
mostrando como vales na curva de precipitação antecedem ou coincidem com
quebras bruscas na colheita.

**SQL (registro):**

```sql
WITH clima_anual AS (
    SELECT 
        clima_historico.ano,
        ROUND(AVG(clima_historico.precipitacao_anual_mm)::numeric, 2) AS precipitacao_media_mm
    FROM clima_historico
    INNER JOIN estado 
        ON clima_historico.estado_id = estado.id
    WHERE 1=1
      [[ AND {{sigla_estado}} ]]
    GROUP BY clima_historico.ano
),
producao_anual AS (
    SELECT 
        mv_historico_expansao_perda.ano,
        SUM(mv_historico_expansao_perda.producao_toneladas) AS total_producao_toneladas
    FROM mv_historico_expansao_perda
    INNER JOIN estado 
        ON mv_historico_expansao_perda.uf = estado.sigla
    WHERE mv_historico_expansao_perda.cultura <> 'Todas (Total do Estado)'
      [[ AND {{sigla_estado}} ]]
      [[ AND {{cultura}} ]]
    GROUP BY mv_historico_expansao_perda.ano
)
SELECT 
    clima_anual.ano,
    clima_anual.precipitacao_media_mm,
    producao_anual.total_producao_toneladas
FROM clima_anual
INNER JOIN producao_anual 
    ON clima_anual.ano = producao_anual.ano
ORDER BY clima_anual.ano ASC;
```

---

### Aba 5 — Risco, Perdas e Cenários

#### Gráfico 15 — Evolução Física da Lavoura: Área Plantada vs. Área Perdida (ha)

**O quê:** comparação anual entre a área total plantada (eixo Y esquerdo) e a
área perdida não colhida (eixo Y direito) em hectares desde 1991.  
**Como:** gráfico de colunas agrupadas com dois eixos Y independentes.

![Gráfico 15 — Evolução Física da Lavoura: Área Plantada vs. Área Perdida (ha)](imagens/image15.png)

**Por quê:** mensura diretamente o prejuízo físico em hectares sofrido pelos
produtores em anos de adversidade climática, subsidiando pedidos de seguro
agrícola e renegociação de crédito rural.

**SQL (registro):**

```sql
SELECT 
    ano AS "Ano",
    MAX(fenomeno_enso) AS "Evento",
    SUM(area_plantada_ha) AS "Área Plantada (ha)",
    SUM(area_perdida_ha) AS "Área Perdida (ha)"
FROM mv_historico_expansao_perda
WHERE ano >= 1991
  AND cultura <> 'Todas (Total do Estado)'
  [[ AND {{cultura}} ]]
  [[ AND {{sigla_estado}} ]]
GROUP BY ano
ORDER BY ano ASC;
```

---

#### Gráfico 16 — Expansão de Campo (%) vs. Aceleração da Perda (p.p.)

**O quê:** cruzamento dinâmico (recalculado via funções de janela `LAG()` sobre
os agregados anuais) entre a taxa anual de expansão da área plantada (`%`) e a
aceleração da taxa de perda (`p.p.`).  
**Como:** gráfico de linhas com eixos independentes (expansão à direita e
aceleração da perda à esquerda).

![Gráfico 16 — Expansão de Campo (%) vs. Aceleração da Perda (p.p.)](imagens/image16.png)

**Por quê:** avalia o risco financeiro da expansão agrícola: identifica anos em
que o produtor ampliou fortemente o investimento em área plantada e enfrentou
salto abrupto na frustração de colheita.

**SQL (registro):**

```sql
WITH base_anual AS (
    SELECT 
        ano,
        MAX(fenomeno_enso) AS evento,
        SUM(area_plantada_ha) AS area_plantada,
        SUM(area_perdida_ha) AS area_perdida
    FROM mv_historico_expansao_perda
    WHERE ano >= 1990
      AND cultura <> 'Todas (Total do Estado)'
      [[ AND {{cultura}} ]]
      [[ AND {{sigla_estado}} ]]
    GROUP BY ano
),
metricas_yoy AS (
    SELECT 
        ano AS "Ano",
        evento AS "Evento",
        ROUND(
            ((area_plantada - LAG(area_plantada) OVER (ORDER BY ano)) / 
            NULLIF(LAG(area_plantada) OVER (ORDER BY ano), 0)) * 100,
            2
        ) AS "Expansão de Campo (%)",
        ROUND(
            ((area_perdida / NULLIF(area_plantada, 0)) * 100) - 
            ((LAG(area_perdida) OVER (ORDER BY ano) / NULLIF(LAG(area_perdida) OVER (ORDER BY ano), 0)) * 100),
            2
        ) AS "Aceleração da Perda (p.p.)"
    FROM base_anual
)
SELECT *
FROM metricas_yoy
WHERE "Ano" >= 1991
ORDER BY "Ano" ASC;
```

---

#### Gráfico 17 — Matriz Preditiva de Risco e Investimento por Cenário Climático (ENSO)

**O quê:** consolidação preditiva baseada no histórico observado de 36 safras,
detalhando por UF, cultura e cenário climático (*El Niño*, *La Niña* ou
*Neutro*) a chuva média esperada, taxa média de investimento, perda média em
hectares, percentual médio de quebra, aceleração da perda e safra esperada em
toneladas.  
**Como:** tabela analítica interativa com formatação condicional em escala de
cores nas colunas de risco, alimentada pela view materializada
`mv_matriz_cenarios_enso`.

![Gráfico 17 — Matriz Preditiva de Risco e Investimento por Cenário Climático (ENSO)](imagens/image17.png)

**Por quê:** serve como ferramenta de apoio à decisão prospectiva: diante da
previsão meteorológica para a próxima safra (ex.: confirmação de *La Niña*), o
gestor identifica imediatamente quais culturas do seu estado possuem maior
probabilidade histórica de quebra.

**SQL (registro):**

```sql
SELECT
  uf AS "UF",
  cultura AS "Cultura",
  fenomeno_enso AS "Evento Climático",
  anos_ocorrencia AS "Anos Analisados",
  chuva_media_mm AS "Chuva Média (mm)",
  taxa_mestre_investimento_pct AS "Taxa Mestre Investimento (% a.a.)",
  perda_media_ha AS "Perda Média (ha)",
  quebra_media_lavoura_pct AS "Quebra Média (%)",
  crescimento_medio_perda_yoy_pct AS "Crescimento da Perda YoY (%)",
  aceleracao_media_perda_pp AS "Aceleração da Perda (p.p.)",
  safra_media_toneladas AS "Safra Esperada (Ton)"
FROM
  mv_matriz_cenarios_enso
WHERE
  cultura <> 'Todas (Total do Estado)'
  AND safra_media_toneladas > 0
  [[ AND {{cultura}} ]]
  [[ AND {{sigla_estado}} ]]
  [[ AND {{previsao_fenomeno}} ]]
ORDER BY
  uf ASC,
  quebra_media_lavoura_pct DESC NULLS LAST;
```

---

## 6. Potencialidades da Ferramenta

1. **Gratuito e open source** — zero custo de licenciamento; a versão
   Community Edition oferece todas as funcionalidades essenciais de BI sem
   exigir contrato ou pagamento de assinatura.
2. **Interface visual sem SQL para consultas básicas** — usuários sem
   conhecimento de banco de dados conseguem montar perguntas, filtros e
   agrupamentos arrastando campos pela interface, sem escrever uma linha de
   código.
3. **Joins visuais entre tabelas relacionais** — o editor de modelo de dados
   permite definir relacionamentos entre tabelas (chaves estrangeiras) de forma
   gráfica, e o Metabase os traduz automaticamente em JOINs nas consultas
   geradas.
4. **Variedade de tipos de visualização no mesmo motor de dados** — a mesma
   consulta pode ser apresentada como tabela, gráfico de barras, linha, rosca,
   treemap ou mapa coroplético sem alterar a query, facilitando a escolha do
   visual mais adequado a cada público.
5. **Self-hosted via Docker — controle total sobre hospedagem dos dados** — é
   possível rodar o Metabase inteiramente na infraestrutura própria, sem
   enviar dados a servidores de terceiros, atendendo requisitos de privacidade
   e LGPD.
6. **Filtros de dashboard a partir de variáveis no SQL nativo** — ao marcar uma
   variável como *Field Filter* (`[[ AND {{filtro}} ]]`), o Metabase gera
   automaticamente listas de seleção no dashboard e ignora a cláusula quando o
   filtro está vazio ou desconectado.
7. **Controle de escopo de filtros por aba e por cartão** — permite que um
   mesmo cartão de legenda ou KPI acompanhe todas as abas enquanto filtros
   pontuais (como `Ano` ou `Fenômeno ENSO`) sejam ocultados nas abas de série
   histórica contínua.
8. **Gráfico combinado com eixo duplo** — séries com escalas muito diferentes
   (toneladas × hectares, ou precipitação em `mm` × produção em toneladas)
   podem ser sobrepostas no mesmo gráfico, cada uma com seu eixo e tipo visual.

---

## 7. Fragilidades da Ferramenta

1. **Sincronização de schema não é automática nem confiável** — após adicionar
   ou alterar tabelas e views materializadas no PostgreSQL, o Metabase pode
   exibir objetos "sem campos" até que uma sincronização manual seja forçada
   pelo administrador.
2. **Mensagens de erro pouco informativas** — erros de tipagem em joins (ex.:
   *"operador não existe: character varying = integer"*) são exibidos sem
   indicar qual relacionamento está incorreto, exigindo inspeção nos logs do
   banco.
3. **Funcionalidades avançadas de colaboração e auditoria reservadas à versão
   paga** — controle granular de permissões por linha, auditoria de acessos,
   SSO e suporte oficial estão disponíveis apenas nas edições Pro/Enterprise.
4. **Desempenho em consultas analíticas sobre tabelas volumosas sem pré-agregação**
   — a base principal contém aproximadamente 2,9 milhões de linhas; consultas
   com múltiplos joins e funções de janela apresentaram latência elevada,
   exigindo a criação de **Views Materializadas** (`mv_historico_expansao_perda`
   e `mv_matriz_cenarios_enso`) no PostgreSQL para garantir fluidez na
   navegação.
5. **Curva de aprendizado para modelagem relacional** — embora a interface
   visual abstraia o SQL, erros na definição de chaves estrangeiras ou
   granularidades no modelo de dados resultam em agregações silenciosamente
   multiplicadas sem aviso explícito.
6. **Configuração frágil das variáveis (Field Filters) e apelidos (aliases)** —
   como o Metabase injeta o nome completo da tabela no SQL gerado ao usar
   *Field Filters* (ex.: `mv_historico_expansao_perda.cultura IN (...)`), o uso
   de apelidos (`FROM tabela alias`) ou o mapeamento para a tabela errada
   provoca falhas de execução no PostgreSQL.
7. **Anos tratados como números** — colunas inteiras, como o ano, são exibidas
   com separador de milhar (`2.012`) e tratadas como escala numérica por padrão,
   exigindo ajuste de tipo semântico para *Categoria* ou formatação manual.
8. **Eixo duplo não é automático** — ao combinar séries de escalas diferentes,
   o Metabase coloca tudo no mesmo eixo, fazendo a série de menor grandeza
   ficar achatada junto ao zero até que cada série seja atribuída manualmente
   ao eixo esquerdo ou direito.