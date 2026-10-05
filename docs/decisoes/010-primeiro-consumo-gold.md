# 010 — Primeiro consumo analítico da V0

Status: aceito
Data e hora: 2026-10-04T18:04:14-04:00

## Contexto

A Silver contém as 12 competências de 2025, 163.161 linhas e o grão integral da fonte. A pergunta da V0 é como quantidade e valor do Pix variaram por natureza, regiões e forma de iniciação. Antes de criar `workspace.gold`, é necessário escolher um contrato voltado ao consumo, sem apenas copiar a Silver.

Três opções são viáveis:

1. **Uma Gold combinada `uso_pix_mensal` (recomendada).** Grão: mês × natureza × forma de iniciação × região pagadora × região recebedora; medidas `valor_total` e `quantidade_total`. O conjunto observado teria 16.496 linhas, cerca de um décimo da Silver, e permitiria cruzar os eixos da pergunta original. O custo é um grão menos simples para consumidores e maior esparsidade que agregados separados.
2. **Duas Golds focadas.** `uso_pix_mensal` no grão mês × natureza × forma de iniciação teria 648 linhas; `fluxo_regional_mensal` no grão mês × região pagadora × região recebedora teria 432. Os contratos ficam pequenos e fáceis de explicar, mas não permitem cruzar natureza ou iniciação com fluxo regional e duplicam medidas e manutenção.
3. **Não materializar Gold ainda.** Versionar consultas analíticas sobre a Silver e validar primeiro quais cortes serão consumidos. É a opção de menor infraestrutura, mas repete definições entre consultas e deixa o consumidor exposto ao grão detalhado.

## Decisão

Vidal escolheu a opção 1: uma Gold combinada `workspace.gold.uso_pix_mensal`, no grão mês × natureza × forma de iniciação × região pagadora × região recebedora, com `valor_total` e `quantidade_total`.

A publicação reutiliza a `python_wheel_task` e o overwrite seletivo mensal já aceitos nas decisões 009 e 005. Métricas derivadas entram apenas quando houver definição e consumidor claros.

## Consequências

A Gold preserva os cruzamentos da pergunta da V0 e reduz o volume exposto ao consumidor, mas seu grão precisa permanecer explícito para evitar agregações incorretas. A tabela não carrega as dimensões PF/PJ, faixa etária e finalidade da Silver; análises nesses eixos continuam consultando a Silver até existir outro consumo aprovado.

Silver e Gold são gravadas em sequência pela mesma tarefa, sem transação entre tabelas. Se a gravação da Gold falhar depois da Silver, o Job termina com falha e a reexecução mensal idempotente recompõe as duas camadas; consumidores não devem interpretar sucesso parcial como publicação concluída.
