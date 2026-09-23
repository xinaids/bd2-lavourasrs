# Trabalho II — Dashboard de Análise da Produção Agrícola do RS

**Disciplina:** Banco de Dados 2 (IBI-BDD002)  
**Curso:** Ciência da Computação — Bacharelado  
**Campus:** IFRS Ibirubá  
**Grupo:** Mateus, Kerlon e Michel  
**Docente:** Edimar Manica  
**Ferramenta:** Metabase (open source, licença AGPL v3)  
**Base de dados:** Produção Agrícola Municipal (PAM) — IBGE/SIDRA  
**Data de entrega:** 27/11/2026  

---

## 1. Público-Alvo

O dashboard é direcionado principalmente a **gestores públicos municipais e
órgãos de assistência técnica rural** (Secretaria da Agricultura,
Emater/RS-Ascar), que podem utilizar essas informações para:

- Direcionar políticas públicas e programas de assistência técnica para regiões
  com queda de produtividade
- Planejar ações de resposta a eventos climáticos adversos (seca, geadas)
- Subsidiar decisões sobre investimento em infraestrutura rural (armazenagem,
  irrigação, logística) com base nos municípios de maior relevância produtiva
- Acompanhar a evolução da produção agrícola do estado ano a ano, com dados
  oficiais e comparáveis

Secundariamente, as informações também são úteis para **cooperativas agrícolas,
instituições financeiras de crédito rural e o próprio produtor**, para decisões
de plantio, avaliação de risco de safra e planejamento de investimento.

---

## 2. Objetivo Geral do Dashboard

Analisar a evolução da produção agrícola dos municípios do Rio Grande do Sul —
com foco em soja, milho, trigo e arroz — observando área plantada,
produtividade e valor da produção ao longo da série histórica disponível no
IBGE/SIDRA (1990–2023). O dashboard busca evidenciar tendências, identificar
municípios de destaque produtivo e quantificar o impacto de eventos climáticos
(como a estiagem de 2022) na produtividade das lavouras, fornecendo subsídio
concreto para tomada de decisão em políticas de assistência técnica rural.

---

## 3. Ferramenta Utilizada

**Metabase** — plataforma open source de Business Intelligence licenciada sob
AGPL v3, utilizada para consulta, visualização e publicação de dashboards
interativos a partir dos dados armazenados no PostgreSQL.

---

## 4. Visualizações do Dashboard

> **Nota:** Esta seção será preenchida após a finalização dos dashboards no
> Metabase. Cada bloco abaixo corresponde a um gráfico; inserir o print e
> completar os campos "O quê" e "Por quê" conforme o gráfico for criado.

---

### Gráfico 1 — [NOME DO GRÁFICO]

**O quê:** [Descrever quais dados são exibidos, métricas, filtros e período]  
**Como:**  
[inserir print aqui]  
**Por quê:** [Explicar a importância dessa visualização para o público-alvo e
quais decisões ela subsidia]

---

### Gráfico 2 — [NOME DO GRÁFICO]

**O quê:** [Descrever quais dados são exibidos, métricas, filtros e período]  
**Como:**  
[inserir print aqui]  
**Por quê:** [Explicar a importância dessa visualização para o público-alvo e
quais decisões ela subsidia]

---

### Gráfico 3 — [NOME DO GRÁFICO]

**O quê:** [Descrever quais dados são exibidos, métricas, filtros e período]  
**Como:**  
[inserir print aqui]  
**Por quê:** [Explicar a importância dessa visualização para o público-alvo e
quais decisões ela subsidia]

---

### Gráfico 4 — [NOME DO GRÁFICO]

**O quê:** [Descrever quais dados são exibidos, métricas, filtros e período]  
**Como:**  
[inserir print aqui]  
**Por quê:** [Explicar a importância dessa visualização para o público-alvo e
quais decisões ela subsidia]

---

### Gráfico 5 — [NOME DO GRÁFICO]

**O quê:** [Descrever quais dados são exibidos, métricas, filtros e período]  
**Como:**  
[inserir print aqui]  
**Por quê:** [Explicar a importância dessa visualização para o público-alvo e
quais decisões ela subsidia]

---

### Gráfico 6 — [NOME DO GRÁFICO]

**O quê:** [Descrever quais dados são exibidos, métricas, filtros e período]  
**Como:**  
[inserir print aqui]  
**Por quê:** [Explicar a importância dessa visualização para o público-alvo e
quais decisões ela subsidia]

---

### Gráfico 7 — [NOME DO GRÁFICO]

**O quê:** [Descrever quais dados são exibidos, métricas, filtros e período]  
**Como:**  
[inserir print aqui]  
**Por quê:** [Explicar a importância dessa visualização para o público-alvo e
quais decisões ela subsidia]

---

### Gráfico 8 — [NOME DO GRÁFICO]

**O quê:** [Descrever quais dados são exibidos, métricas, filtros e período]  
**Como:**  
[inserir print aqui]  
**Por quê:** [Explicar a importância dessa visualização para o público-alvo e
quais decisões ela subsidia]

---

### Gráfico 9 — [NOME DO GRÁFICO]

**O quê:** [Descrever quais dados são exibidos, métricas, filtros e período]  
**Como:**  
[inserir print aqui]  
**Por quê:** [Explicar a importância dessa visualização para o público-alvo e
quais decisões ela subsidia]

---

### Gráfico 10 — [NOME DO GRÁFICO]

**O quê:** [Descrever quais dados são exibidos, métricas, filtros e período]  
**Como:**  
[inserir print aqui]  
**Por quê:** [Explicar a importância dessa visualização para o público-alvo e
quais decisões ela subsidia]

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

---

## 6. Fragilidades da Ferramenta

1. **Sincronização de schema não é automática nem confiável** — após adicionar
   ou alterar tabelas no PostgreSQL, o Metabase pode apresentar as tabelas
   "sem campos" até que uma sincronização manual seja forçada pelo
   administrador, causando confusão e interrompendo o fluxo de trabalho.

2. **Mensagens de erro pouco informativas** — erros de tipagem em joins (ex.:
   *"operador não existe: integer = character varying"*) são exibidos sem
   indicar qual relacionamento está incorreto, dificultando o diagnóstico sem
   recorrer aos logs do banco diretamente.

3. **Funcionalidades avançadas de colaboração e auditoria reservadas à versão
   paga** — controle granular de permissões por linha, auditoria de acessos,
   SSO e suporte oficial estão disponíveis apenas nas edições Pro/Enterprise,
   criando limitações relevantes para uso em ambientes institucionais.

4. **Performance degradada em consultas com múltiplos joins sobre tabelas
   grandes** — a base utilizada contém aproximadamente 2,9 milhões de linhas;
   dashboards com cadeias de joins encadeados (município → estado → região)
   apresentaram lentidão perceptível, exigindo criação de índices adicionais e
   ajuste de configurações do PostgreSQL fora do Metabase.

5. **Curva de aprendizado para modelagem relacional** — embora a interface
   visual abstrai o SQL, o usuário ainda precisa compreender o conceito de
   chaves estrangeiras e cadeias de relacionamento para configurar o modelo de
   dados corretamente. Erros na definição dos relacionamentos no Metabase
   resultam em resultados silenciosamente incorretos nos gráficos, sem aviso
   explícito.
