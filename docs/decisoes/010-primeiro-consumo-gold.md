# 010 — Primeiro consumo analítico da V0

Status: proposto
Data e hora: 2026-10-03T18:21:09-04:00

## Contexto

A Silver contém as 12 competências de 2025, 163.161 linhas e o grão integral da fonte. A pergunta da V0 é como quantidade e valor do Pix variaram por natureza, regiões e forma de iniciação. Antes de criar `workspace.gold`, é necessário escolher um contrato voltado ao consumo, sem apenas copiar a Silver.

Três opções são viáveis:

1. **Uma Gold combinada `uso_pix_mensal` (recomendada).** Grão: mês × natureza × forma de iniciação × região pagadora × região recebedora; medidas `valor_total` e `quantidade_total`. O conjunto observado teria 16.496 linhas, cerca de um décimo da Silver, e permitiria cruzar os eixos da pergunta original. O custo é um grão menos simples para consumidores e maior esparsidade que agregados separados.
2. **Duas Golds focadas.** `uso_pix_mensal` no grão mês × natureza × forma de iniciação teria 648 linhas; `fluxo_regional_mensal` no grão mês × região pagadora × região recebedora teria 432. Os contratos ficam pequenos e fáceis de explicar, mas não permitem cruzar natureza ou iniciação com fluxo regional e duplicam medidas e manutenção.
3. **Não materializar Gold ainda.** Versionar consultas analíticas sobre a Silver e validar primeiro quais cortes serão consumidos. É a opção de menor infraestrutura, mas repete definições entre consultas e deixa o consumidor exposto ao grão detalhado.

## Decisão

Aguardando escolha de Vidal.

Recomendação técnica: **opção 1**, porque responde aos três eixos da pergunta aprovada com uma única tabela ainda pequena. A Gold deve somar somente `valor` e `quantidade`; métricas derivadas entram apenas quando houver definição e consumidor claros.

## Consequências

A opção 1 preserva cruzamentos e reduz o volume, mas exige documentar o grão para evitar agregações incorretas. A opção 2 simplifica cada consumo e reduz mais o volume, ao custo de perder cruzamentos e manter duas tabelas. A opção 3 adia o contrato Gold e favorece exploração, mas oferece menos reutilização e governança semântica.
