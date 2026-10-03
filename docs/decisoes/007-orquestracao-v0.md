# 007 — Orquestração da V0

Status: proposto
Data e hora: 2026-10-03T09:43:19-04:00

## Contexto

A V0 fará uma requisição HTTP batch para uma competência, preservará a resposta em um Volume, validará o contrato e substituirá somente essa competência na Silver. A extração e a gravação do arquivo são efeitos imperativos; a transformação tabular pode ser declarativa. A implementação deve continuar pequena, observável e compatível com a Free Edition, cujas capacidades reais ainda não foram verificadas.

Duas opções são viáveis:

1. **Lakeflow Job com tarefas batch (recomendada).** Um Job parametrizado por `ano_mes` coordena a ingestão Python e a transformação/publicação, inicialmente em duas tarefas com dependência explícita. Oferece retries, parâmetros, ordem e histórico de execução sem introduzir um segundo recurso de orquestração. A transformação pode continuar expressa em SQL executado pelo Job. O custo é implementar explicitamente os checks e o overwrite seletivo.
2. **Lakeflow Job + Spark Declarative Pipeline.** O Job faz a chamada HTTP e grava o bruto; depois aciona um Pipeline batch para materializar e validar a Silver. Oferece expectativas e linhagem administradas para a parte tabular, mas adiciona um recurso, uma fronteira operacional e mais configuração para uma única fonte e tabela na V0.

Um Pipeline isolado não foi mantido como opção: a requisição HTTP e a escrita imutável do arquivo são efeitos externos que ainda exigiriam código/orquestração imperativa. Streaming e Auto Loader não entram, porque a fonte é mensal e consultada sob demanda.

## Decisão

Aguardando escolha de Vidal.

Recomendação técnica: **Lakeflow Job com tarefas batch**. É o menor mecanismo que cobre o fluxo completo e mantém SQL como linguagem preferencial da transformação, sem transformar uma carga mensal em arquitetura contínua.

Nenhum recurso, notebook ou YAML de Job será criado antes da escolha e da verificação da Databricks CLI/workspace.

## Consequências

Com Job apenas, o primeiro recurso poderá ter parâmetro `ano_mes`, uma tarefa de ingestão/validação e outra de publicação Silver, com dependência e retries limitados. A separação exata entre as tarefas será confirmada durante a implementação conforme o meio de execução disponível na Free Edition.

Com Job + Pipeline, a Silver ganha semântica declarativa administrada, mas deploy, depuração e evidência de execução passam a envolver dois recursos. Essa complexidade só se justifica se Vidal quiser demonstrar Pipelines já na V0.
