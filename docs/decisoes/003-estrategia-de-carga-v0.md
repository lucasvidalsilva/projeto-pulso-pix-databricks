# 003 — Estratégia de carga da V0

Status: aceito
Data e hora: 2026-10-03T01:36:35-04:00

## Contexto

A V0 usará `EstatisticasTransacoesPix` no ano civil de 2025. A fonte é consultada por HTTP, tem atualização mensal e exige combinar `@Database` com um filtro exato de `AnoMes`. Não oferece fluxo de eventos ou change feed. O endpoint apresentou latência alta e falha HTTP 500 após uma sequência curta de consultas, por isso a unidade de recuperação afeta rastreabilidade e custo operacional.

Duas opções batch são viáveis:

1. **Unidade mensal parametrizada.** Cada execução consulta e valida uma competência; o backfill de 2025 usa 12 unidades independentes. Facilita retry, reprocessamento, evidência e isolamento de falhas, mas exige mais chamadas e controle de quais meses concluíram.
2. **Snapshot anual.** Uma execução trata todo o ano como uma unidade lógica. Tem fluxo inicial mais simples, mas aumenta payload, duração e custo de repetição, além de obrigar a refazer o ano quando apenas um mês falha ou precisa ser revisto.

Streaming não foi mantido como opção: a fonte publica agregados mensais por consulta e não fornece eventos ou mudanças contínuas; adicioná-lo não melhora a atualidade e criaria estado operacional sem necessidade observada.

## Decisão

Vidal escolheu a **unidade mensal parametrizada**, com backfill das 12 competências de 2025. A granularidade reduz o impacto da instabilidade observada e deixa explícito o mês processado sem ampliar o escopo funcional da V0.

Esta proposta não escolhe tecnologia de orquestração, isolamento entre targets nem operação de escrita. Esses temas serão decididos antes da persistência e da criação de recursos.

## Consequências

A ingestão terá `ano_mes` explícito, validação antes de persistir e capacidade de repetir apenas uma competência. Em contrapartida, a execução precisará controlar 12 resultados no backfill e respeitar espera entre chamadas.

Se o snapshot anual for escolhido, haverá menos unidades de execução, mas falha ou revisão parcial exigirá repetir o conjunto completo e comprovar que a consulta não foi truncada.
