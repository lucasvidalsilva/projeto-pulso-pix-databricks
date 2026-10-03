# 007 — Orquestração da V0

Status: aceito
Data e hora: 2026-10-03T11:18:18-04:00

## Contexto

A V0 fará uma requisição HTTP batch para uma competência, preservará a resposta em um Volume, validará o contrato e substituirá somente essa competência na Silver. A extração e a gravação do arquivo são efeitos imperativos; a transformação tabular pode ser declarativa. A implementação deve continuar pequena, observável e compatível com a Free Edition, cujas capacidades reais ainda não foram verificadas.

Duas opções são viáveis:

1. **Lakeflow Job com tarefas batch (recomendada).** Um Job parametrizado por `ano_mes` coordena a ingestão Python e a transformação/publicação, inicialmente em duas tarefas com dependência explícita. Oferece retries, parâmetros, ordem e histórico de execução sem introduzir um segundo recurso de orquestração. A transformação pode continuar expressa em SQL executado pelo Job. O custo é implementar explicitamente os checks e o overwrite seletivo.
2. **Lakeflow Job + Spark Declarative Pipeline.** O Job faz a chamada HTTP e grava o bruto; depois aciona um Pipeline batch para materializar e validar a Silver. Oferece expectativas e linhagem administradas para a parte tabular, mas adiciona um recurso, uma fronteira operacional e mais configuração para uma única fonte e tabela na V0.

Um Pipeline isolado não foi mantido como opção: a requisição HTTP e a escrita imutável do arquivo são efeitos externos que ainda exigiriam código/orquestração imperativa. Streaming e Auto Loader não entram, porque a fonte é mensal e consultada sob demanda.

## Decisão

Vidal escolheu **Lakeflow Job com tarefas batch**, parametrizado por `ano_mes`. A V0 não usará Spark Declarative Pipeline. A escolha mantém um único recurso de orquestração e permite que a ingestão continue em Python e a transformação declarativa em SQL.

Nenhum recurso, notebook ou YAML de Job foi criado nesta decisão. A verificação de 2026-10-03 confirmou que a Databricks CLI e o WinGet estão ausentes do `PATH`; a implementação do recurso fica condicionada à instalação externa da CLI atual e à validação do workspace, conforme a skill oficial Databricks Core.

## Consequências

Com Job apenas, o primeiro recurso terá parâmetro `ano_mes`, uma tarefa de ingestão/validação e outra de publicação Silver, com dependência e retries limitados. A separação exata entre as tarefas será confirmada durante a implementação conforme o meio de execução disponível na Free Edition.

Com Job + Pipeline, a Silver ganha semântica declarativa administrada, mas deploy, depuração e evidência de execução passam a envolver dois recursos. Essa complexidade só se justifica se Vidal quiser demonstrar Pipelines já na V0.
