# Trabalho II — Planejamento do Dashboard

**Curso:** Ciência da Computação — Bacharelado

**Disciplina:** Banco de Dados 2 (IBI-BDD002)

**Campus:** IFRS Ibirubá

**Professor:** Edimar Manica

**Grupo:** Mateus, Kerlon e Michel

**Projeto:** Lavouras RS — dashboard de produção agrícola (IBGE/SIDRA, Tabela 1612)

**Ferramenta:** Metabase

**Público-alvo:** gestores públicos municipais e órgãos de assistência técnica rural (Secretaria da Agricultura, Emater/RS-Ascar)

**Data de entrega:** 16/10/2026

Obs.: o dashboard tem filtros de cultura (e de estado) e também 4 indicadores (KPIs) de valor total, rendimento médio, área plantada e quantidade produzida. Abaixo estão os 10 gráficos/mapas planejados.

---

## Gráfico 1 — Eficiência agrícola por estado

**Quais dados:** rendimento médio (kg/ha, calculado como quantidade produzida ÷ área plantada) de cada unidade da federação, para a cultura selecionada no filtro.

**Como serão exibidos:** mapa coroplético do Brasil, com os estados coloridos por faixa de rendimento.

**Importância:** mostra rapidamente quais estados são mais e menos produtivos e onde o RS se posiciona, indicando onde a assistência técnica pode ter mais efeito.

---

## Gráfico 2 — Peso financeiro das culturas

**Quais dados:** valor total da produção de cada cultura.

**Como serão exibidos:** gráfico de colunas verticais, uma coluna por cultura, ordenadas da maior para a menor.

**Importância:** cria um ranking econômico das culturas e mostra onde está o maior retorno financeiro, ajudando a priorizar apoio e políticas.

---

## Gráfico 3 — Evolução histórica da produção

**Quais dados:** quantidade produzida (ou valor da produção) por ano, de 2013 a 2023, para a cultura e o estado selecionados.

**Como serão exibidos:** gráfico de linhas (série temporal), com os anos no eixo X.

**Importância:** evidencia tendências de crescimento, estagnação e quebras de safra por seca ou geada (como a estiagem de 2022 no RS), apoiando planejamento e resposta a eventos climáticos.

---

## Gráfico 4 — Participação das culturas no uso do solo

**Quais dados:** percentual da área plantada de cada cultura em relação ao total, no ano selecionado.

**Como serão exibidos:** gráfico de rosca (donut).

**Importância:** mostra quais culturas ocupam mais espaço no território e o quanto a produção depende de poucas culturas.

---

## Gráfico 5 — Relação entre área plantada e eficiência

**Quais dados:** área plantada (eixo X) cruzada com o rendimento médio em kg/ha (eixo Y) para cada estado produtor.

**Como serão exibidos:** gráfico de dispersão (scatter), com um ponto por estado.

**Importância:** mostra que o maior estado não é necessariamente o mais produtivo, identificando estados que produzem muito em pouca área e estados com grandes áreas e baixa eficiência.

---

## Gráfico 6 — Evolução comparativa de culturas

**Quais dados:** valor da produção das principais culturas ao longo dos anos.

**Como serão exibidos:** gráfico de área empilhada.

**Importância:** mostra o crescimento histórico do setor e como a proporção de cada cultura muda com o tempo, por exemplo se a soja está ocupando o espaço que era de outro produto.

---

## Gráfico 7 — Matriz de crescimento regional

**Quais dados:** valor total da produção, com os estados nas linhas e os anos nas colunas.

**Como serão exibidos:** tabela dinâmica (pivot table).

**Importância:** permite ler os dados em formato de matriz e identificar rapidamente quais estados estão estagnados e quais estão em expansão ano após ano.

---

## Gráfico 8 — Ranking de municípios polos

**Quais dados:** os 10 municípios com maior quantidade produzida (toneladas) da cultura selecionada no filtro.

**Como serão exibidos:** gráfico de barras horizontais.

**Importância:** desce da visão por estado para os municípios que realmente movem a produção, e permite ao gestor municipal comparar seu município com os líderes.

---

## Gráfico 9 — Relação histórica entre volume produzido e área plantada

**Quais dados:** quantidade produzida (toneladas) e área plantada ao longo dos anos, para o produto filtrado.

**Como serão exibidos:** gráfico combinado, com barras para a quantidade produzida e linha para a área plantada.

**Importância:** mostra como a produção cresceu. Se as barras sobem e a linha de área fica estável, houve ganho de produtividade. Se ambas sobem juntas, o crescimento veio da expansão da área plantada.

---

## Gráfico 10 — Concentração de riqueza agrícola

**Quais dados:** participação de cada estado no valor total da produção nacional.

**Como serão exibidos:** mapa de árvore (treemap), com retângulos proporcionais ao valor.

**Importância:** é mais legível que uma pizza quando há 27 estados e mostra rapidamente a dominância econômica de alguns estados e o peso relativo do RS.
