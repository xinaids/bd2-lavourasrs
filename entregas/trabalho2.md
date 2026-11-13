# Trabalho II — Dashboard de Análise da Produção Agrícola do RS

**Disciplina:** Banco de Dados 2 (IBI-BDD002)  
**Curso:** Ciência da Computação — Bacharelado  
**Campus:** IFRS Ibirubá  
**Grupo:** Metabase — Mateus, Kerlon e Michel  
**Docente:** Edimar Manica  
**Ferramenta:** Metabase (open source, licença AGPL v3)  
**Base de dados:** Produção Agrícola Municipal (PAM) — IBGE/SIDRA  
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
- Planejar ações de resposta a eventos climáticos adversos (estiagem, geada) e
  fundamentar pedidos de apoio ao governo estadual e federal
- Subsidiar decisões sobre investimento em infraestrutura rural (armazenagem,
  irrigação, estradas) com base nos municípios e culturas de maior relevância
- Acompanhar a evolução da produção agrícola ano a ano, com dados oficiais e
  comparáveis

O painel não é um relatório técnico para pesquisadores nem uma análise de
mercado para investidores: as perguntas e a linguagem foram pensadas para quem
decide as ações de agricultura do município.

---

## 2. Objetivo Geral do Dashboard

Analisar a evolução da produção agrícola dos municípios brasileiros, com
destaque para o Rio Grande do Sul, observando área plantada, produtividade,
quantidade produzida e valor da produção ao longo da série histórica
disponível na base do IBGE/SIDRA. O dashboard permite filtrar por cultura, ano e
estado, busca evidenciar tendências, identificar municípios de destaque
produtivo e quantificar o impacto de eventos climáticos (como a estiagem de
2022) na produtividade das lavouras, fornecendo subsídio concreto para a tomada
de decisão do gestor municipal de agricultura.

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
6. **Dashboards interativos** — vários gráficos na mesma tela, com filtros que
   atuam sobre todos os gráficos conectados.
7. **Variedade de visualizações** — tabela, barras, linhas, área, dispersão,
   pizza/rosca, mapa, funil, tabela dinâmica (pivot), gráfico combinado, entre
   outras.
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

## 4. Visualizações do Dashboard

Além dos 10 gráficos abaixo, o dashboard traz 5 indicadores (KPIs): valor
total da produção, rendimento médio, área plantada, quantidade produzida e
contagem de municípios. Os filtros disponíveis são cultura, ano e estado.

> **Nota:** o campo **Como** (print com dados reais) será preenchido conforme
> cada gráfico for finalizado no Metabase. O campo **SQL (registro)** guarda a
> consulta usada, para que outras pessoas possam reproduzir o gráfico em suas
> próprias bases.

**Resumo dos gráficos e dos tipos de visualização:**

| Nº | Gráfico | Tipo de visualização |
|----|---------|----------------------|
| 1  | Eficiência agrícola por estado | Mapa |
| 2  | Peso financeiro das culturas | Barras horizontais |
| 3  | Evolução histórica da produção | Linhas |
| 4  | Participação das culturas no uso do solo | Rosca (donut) |
| 5  | Relação entre área plantada e eficiência | Dispersão (scatter) |
| 6  | Evolução comparativa de culturas | Área empilhada |
| 7  | Matriz de crescimento regional | Tabela dinâmica (pivot) |
| 8  | Ranking de municípios polos | Barras horizontais |
| 9  | Volume produzido × área plantada | Combinado (barras + linha) |
| 10 | Concentração de riqueza agrícola | Mapa de árvore (treemap) |

São **10 gráficos** e **9 tipos diferentes** de visualização (mapa, barras
horizontais, linhas, rosca, dispersão, área empilhada, tabela dinâmica,
combinado e treemap).

---

### Gráfico 1 — Eficiência agrícola por estado

**O quê:** rendimento médio (kg/ha, calculado como quantidade produzida ÷ área
plantada) de cada unidade da federação, para a cultura selecionada no filtro.  
**Como:** mapa do Brasil, com os estados coloridos por faixa de rendimento.

<!-- ![Gráfico 1](../imagens/grafico1.png) -->
[inserir print aqui]

**Por quê:** mostra rapidamente quais estados são mais e menos produtivos e
onde o RS se posiciona, indicando onde a assistência técnica pode ter mais
efeito.

**SQL (registro):**

```sql
-- preencher após validar no banco
```

---

### Gráfico 2 — Peso financeiro das culturas

**O quê:** valor total da produção (em bilhões de reais) de cada cultura, para
o ano e o estado escolhidos nos filtros (padrão: 2023, todos os estados).  
**Como:** gráfico de barras horizontais, uma barra por cultura, cada uma com uma
cor, ordenadas da maior para a menor.

![Gráfico 2 — Peso financeiro das culturas](../imagens/grafico2.png)

**Por quê:** cria um ranking econômico das culturas e mostra onde está o maior
retorno financeiro, ajudando a priorizar apoio e políticas.

**SQL (registro):**

Versão usada no Metabase (com as variáveis de filtro `ano` e `estado`, ambas do
tipo Field Filter). A variável `variavel` "Valor da produção" existe em três
moedas na base (Mil Cruzeiros, Mil Cruzeiros Reais e Mil Reais), por isso a
consulta filtra a unidade `Mil Reais`:

```sql
SELECT
  p.nome AS cultura,
  p.nome AS legenda,
  ROUND(SUM(pa.valor) / 1000000.0, 2) AS bilhoes_de_reais
FROM producao_agricola pa
JOIN produto   p ON pa.produto_id   = p.id
JOIN variavel  v ON pa.variavel_id  = v.id
JOIN unidade   u ON pa.unidade_id   = u.id
JOIN municipio m ON pa.municipio_id = m.id
JOIN estado    e ON m.estado_id     = e.id
WHERE v.nome = 'Valor da produção (Mil Reais)'
  AND u.nome = 'Mil Reais'
  AND {{ano}}
  [[AND {{estado}}]]
GROUP BY p.id, p.nome
ORDER BY bilhoes_de_reais DESC;
```

Versão para rodar direto no PostgreSQL (sem variáveis do Metabase; troque o ano
e, se quiser, descomente o filtro de estado):

```sql
SELECT
  p.nome AS cultura,
  ROUND(SUM(pa.valor) / 1000000.0, 2) AS bilhoes_de_reais
FROM producao_agricola pa
JOIN produto   p ON pa.produto_id   = p.id
JOIN variavel  v ON pa.variavel_id  = v.id
JOIN unidade   u ON pa.unidade_id   = u.id
JOIN municipio m ON pa.municipio_id = m.id
JOIN estado    e ON m.estado_id     = e.id
WHERE v.nome = 'Valor da produção (Mil Reais)'
  AND u.nome = 'Mil Reais'
  AND pa.ano = 2023
  -- AND e.nome = 'Rio Grande do Sul'
GROUP BY p.id, p.nome
ORDER BY bilhoes_de_reais DESC;
```

---

### Gráfico 3 — Evolução histórica da produção

**O quê:** quantidade produzida (ou valor da produção) por ano, de 2013 a 2023,
para a cultura e o estado selecionados.  
**Como:** gráfico de linhas (série temporal), com os anos no eixo X.

<!-- ![Gráfico 3](../imagens/grafico3.png) -->
[inserir print aqui]

**Por quê:** evidencia tendências de crescimento, estagnação e quebras de safra
por seca ou geada (como a estiagem de 2022 no RS), apoiando planejamento e
resposta a eventos climáticos.

**SQL (registro):**

```sql
-- preencher após validar no banco
```

---

### Gráfico 4 — Participação das culturas no uso do solo

**O quê:** percentual da área plantada (em hectares) de cada cultura em relação
ao total, para o ano e o estado escolhidos nos filtros (padrão: 2023, todos os
estados). Para o café, que é cultura permanente, usa-se a área destinada à
colheita, pois a base não traz área plantada para ele.  
**Como:** gráfico de rosca (donut), com o total de hectares no centro e o
percentual de cada cultura na legenda.

![Gráfico 4 — Participação das culturas no uso do solo](../imagens/grafico4.png)

**Por quê:** mostra quais culturas ocupam mais espaço no território e o quanto
a produção depende de poucas culturas. O gestor pode avaliar essa dependência e
decidir entre incentivar a diversificação ou reforçar o apoio às culturas
dominantes.

**SQL (registro):**

Versão usada no Metabase (com as variáveis de filtro `ano` e `estado`, ambas do
tipo Field Filter). A consulta usa a variável "Área plantada" para todas as
culturas e "Área destinada à colheita" apenas para o café, evitando contar a
mesma área duas vezes:

```sql
SELECT
  p.nome AS cultura,
  SUM(pa.valor) AS hectares
FROM producao_agricola pa
JOIN produto   p ON pa.produto_id   = p.id
JOIN variavel  v ON pa.variavel_id  = v.id
JOIN municipio m ON pa.municipio_id = m.id
JOIN estado    e ON m.estado_id     = e.id
WHERE (   v.nome = 'Área plantada (Hectares)'
       OR (v.nome = 'Área destinada à colheita (Hectares)' AND p.nome ILIKE 'Café%'))
  AND {{ano}}
  [[AND {{estado}}]]
GROUP BY p.id, p.nome
ORDER BY hectares DESC;
```

Versão para rodar direto no PostgreSQL (sem variáveis do Metabase; troque o ano
e, se quiser, descomente o filtro de estado):

```sql
SELECT
  p.nome AS cultura,
  SUM(pa.valor) AS hectares
FROM producao_agricola pa
JOIN produto   p ON pa.produto_id   = p.id
JOIN variavel  v ON pa.variavel_id  = v.id
JOIN municipio m ON pa.municipio_id = m.id
JOIN estado    e ON m.estado_id     = e.id
WHERE (   v.nome = 'Área plantada (Hectares)'
       OR (v.nome = 'Área destinada à colheita (Hectares)' AND p.nome ILIKE 'Café%'))
  AND pa.ano = 2023
  -- AND e.nome = 'Rio Grande do Sul'
GROUP BY p.id, p.nome
ORDER BY hectares DESC;
```

---

### Gráfico 5 — Relação entre área plantada e eficiência

**O quê:** área plantada (eixo X) cruzada com o rendimento médio em kg/ha (eixo
Y) para cada estado produtor.  
**Como:** gráfico de dispersão (scatter), com um ponto por estado.

<!-- ![Gráfico 5](../imagens/grafico5.png) -->
[inserir print aqui]

**Por quê:** mostra que o maior estado não é necessariamente o mais produtivo,
identificando estados que produzem muito em pouca área e estados com grandes
áreas e baixa eficiência. A assistência técnica pode priorizar estados com
muita área e baixa eficiência e usar os mais eficientes como referência de boas
práticas.

**SQL (registro):**

```sql
-- preencher após validar no banco
```

---

### Gráfico 6 — Evolução comparativa de culturas

**O quê:** valor da produção das principais culturas ao longo dos anos.  
**Como:** gráfico de área empilhada.

<!-- ![Gráfico 6](../imagens/grafico6.png) -->
[inserir print aqui]

**Por quê:** mostra o crescimento histórico do setor e como a proporção de cada
cultura muda com o tempo, por exemplo se a soja está ocupando o espaço que era
de outro produto. O gestor pode antecipar mudanças no perfil produtivo, como o
avanço da soja, e adaptar capacitação e crédito às culturas que crescem.

**SQL (registro):**

```sql
-- preencher após validar no banco
```

---

### Gráfico 7 — Matriz de crescimento regional

**O quê:** valor total da produção, com os estados nas linhas e os anos nas
colunas.  
**Como:** tabela dinâmica (pivot table).

<!-- ![Gráfico 7](../imagens/grafico7.png) -->
[inserir print aqui]

**Por quê:** permite ler os dados em formato de matriz e identificar
rapidamente quais estados estão estagnados e quais estão em expansão ano após
ano. O gestor pode identificar estados e anos de queda e direcionar apoio às
regiões estagnadas, usando os números exatos em relatórios.

**SQL (registro):**

```sql
-- preencher após validar no banco
```

---

### Gráfico 8 — Ranking de municípios polos

**O quê:** os 10 municípios com maior quantidade produzida (toneladas) da
cultura selecionada, para o ano e o estado escolhidos nos filtros (padrão:
soja, 2023, todos os estados).  
**Como:** gráfico de barras horizontais, com uma cor para cada município.

![Gráfico 8 — Ranking de municípios polos](../imagens/grafico8.png)

**Por quê:** desce da visão por estado para os municípios que realmente movem a
produção, e permite ao gestor municipal comparar seu município com os líderes.

**SQL (registro):**

Versão usada no Metabase (com as variáveis de filtro `cultura`, `ano` e
`estado`, as três do tipo Field Filter, que geram listas de seleção no
dashboard):

```sql
SELECT
  m.nome || ' - ' || e.nome AS municipio,
  m.nome || ' - ' || e.nome AS legenda,
  SUM(pa.valor) AS toneladas
FROM producao_agricola pa
JOIN municipio m ON pa.municipio_id = m.id
JOIN estado    e ON m.estado_id     = e.id
JOIN produto   p ON pa.produto_id   = p.id
JOIN variavel  v ON pa.variavel_id  = v.id
WHERE v.nome = 'Quantidade produzida (Toneladas)'
  AND {{cultura}}
  AND {{ano}}
  [[AND {{estado}}]]
GROUP BY m.id, m.nome, e.nome
ORDER BY toneladas DESC
LIMIT 10;
```

Versão para rodar direto no PostgreSQL (sem variáveis do Metabase; troque a
cultura, o ano e, se quiser, descomente o filtro de estado):

```sql
SELECT
  m.nome || ' - ' || e.nome AS municipio,
  SUM(pa.valor) AS toneladas
FROM producao_agricola pa
JOIN municipio m ON pa.municipio_id = m.id
JOIN estado    e ON m.estado_id     = e.id
JOIN produto   p ON pa.produto_id   = p.id
JOIN variavel  v ON pa.variavel_id  = v.id
WHERE v.nome = 'Quantidade produzida (Toneladas)'
  AND p.nome ILIKE 'Soja%'
  AND pa.ano = 2023
  -- AND e.nome = 'Rio Grande do Sul'
GROUP BY m.id, m.nome, e.nome
ORDER BY toneladas DESC
LIMIT 10;
```

---

### Gráfico 9 — Relação histórica entre volume produzido e área plantada

**O quê:** quantidade produzida (toneladas) e área plantada ao longo dos anos,
para o produto filtrado.  
**Como:** gráfico combinado, com barras para a quantidade produzida e linha
para a área plantada.

<!-- ![Gráfico 9](../imagens/grafico9.png) -->
[inserir print aqui]

**Por quê:** mostra como a produção cresceu. Se as barras sobem e a linha de
área fica estável, houve ganho de produtividade. Se ambas sobem juntas, o
crescimento veio da expansão da área plantada. O gestor pode usar essa leitura
para decidir se o apoio deve focar em ganho de produtividade ou em ampliação de
área.

**SQL (registro):**

```sql
-- preencher após validar no banco
```

---

### Gráfico 10 — Concentração de riqueza agrícola

**O quê:** participação de cada estado no valor total da produção nacional.  
**Como:** mapa de árvore (treemap), com retângulos proporcionais ao valor.

<!-- ![Gráfico 10](../imagens/grafico10.png) -->
[inserir print aqui]

**Por quê:** é mais legível que uma pizza quando há 27 estados e mostra
rapidamente a dominância econômica de alguns estados e o peso relativo do RS.
Permite dimensionar o peso econômico de cada estado e do RS no país, apoiando
pedidos de recursos e políticas para o setor.

**SQL (registro):**

```sql
-- preencher após validar no banco
```

---

## 5. Potencialidades da Ferramenta

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
   geradas, dispensando SQL manual para navegação entre dimensões.

4. **Variedade de tipos de visualização no mesmo motor de dados** — a mesma
   consulta pode ser apresentada como tabela, gráfico de barras, linha, pizza,
   funil ou mapa coroplético sem alterar a query, facilitando a escolha do
   visual mais adequado a cada público.

5. **Self-hosted via Docker — controle total sobre hospedagem dos dados** — é
   possível rodar o Metabase inteiramente na infraestrutura própria, sem
   enviar dados a servidores de terceiros, atendendo requisitos de privacidade
   e LGPD em projetos com dados sensíveis.

6. **Filtros de dashboard a partir de variáveis no SQL nativo** — ao marcar uma
   variável como *Field Filter*, o Metabase gera automaticamente listas de
   seleção (cultura, ano, estado) no dashboard, mesmo em consultas escritas à
   mão, como nos gráficos 2, 4 e 8.

7. **Gráfico combinado com eixo duplo** — séries com escalas muito diferentes
   (rendimento em kg/ha e chuva em mm) podem ser sobrepostas no mesmo gráfico,
   cada uma com seu eixo e seu tipo (barra ou linha), como no gráfico 9
   (toneladas × hectares).

---

## 6. Fragilidades da Ferramenta

1. **Sincronização de schema não é automática nem confiável** — após adicionar
   ou alterar tabelas no PostgreSQL, o Metabase pode apresentar as tabelas
   "sem campos" até que uma sincronização manual seja forçada pelo
   administrador, causando confusão e interrompendo o fluxo de trabalho.

2. **Mensagens de erro pouco informativas** — erros de tipagem em joins (ex.:
   *"operador não existe: character varying = integer"*) são exibidos sem
   indicar qual relacionamento está incorreto, dificultando o diagnóstico sem
   recorrer aos logs do banco diretamente.

3. **Funcionalidades avançadas de colaboração e auditoria reservadas à versão
   paga** — controle granular de permissões por linha, auditoria de acessos,
   SSO e suporte oficial estão disponíveis apenas nas edições Pro/Enterprise,
   criando limitações relevantes para uso em ambientes institucionais.

4. **Desempenho em consultas com vários joins sobre tabelas grandes** — a base
   utilizada contém aproximadamente 2,9 milhões de linhas; consultas que
   encadeiam vários joins (produção → município → estado) e agregam a série
   histórica inteira levaram cerca de 3 segundos para responder. O tempo é
   aceitável nesta base, mas tende a aumentar em bases maiores e pode exigir
   índices e ajustes no banco, fora do Metabase.

5. **Curva de aprendizado para modelagem relacional** — embora a interface
   visual abstrai o SQL, o usuário ainda precisa compreender o conceito de
   chaves estrangeiras e cadeias de relacionamento para configurar o modelo de
   dados corretamente. Erros na definição dos relacionamentos no Metabase
   resultam em resultados silenciosamente incorretos nos gráficos, sem aviso
   explícito.

6. **Configuração frágil das variáveis (Field Filters)** — se o campo vinculado
   ou o alias (como `pa.ano` ou `e.nome`) não for preenchido exatamente como na
   consulta, a execução falha com erros como *"missing required parameters"* ou
   *"referência inválida para tabela"*, e o problema só aparece ao rodar.

7. **Anos tratados como números** — colunas inteiras, como o ano, são exibidas
   com separador de milhar (2.012) e tratadas como escala numérica, o que exige
   converter para texto na consulta (`ano::text`) ou ajustar a formatação
   coluna a coluna.

8. **Eixo duplo não é automático** — ao combinar séries de escalas diferentes,
   o Metabase coloca tudo no mesmo eixo, e a série de menor valor vira uma
   linha achatada até que cada série seja configurada
   manualmente (tipo de gráfico e posição do eixo).
