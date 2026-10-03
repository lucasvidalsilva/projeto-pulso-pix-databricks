# 005 — Reexecução e histórico mensal

Status: aceito
Data e hora: 2026-10-03T09:25:13-04:00

## Contexto

A fonte entrega uma fotografia completa de cada `AnoMes`, e a V0 processará uma competência por vez. A reexecução precisa corrigir uma competência sem duplicar métricas, remover linhas que tenham desaparecido da fonte e preservar evidência suficiente para investigar revisões.

Três opções são viáveis:

1. **Resposta bruta imutável e overwrite seletivo na Silver.** Cada extração bem-sucedida preserva a resposta original com metadados de execução; a tabela tratada substitui atomicamente apenas o `ano_mes` processado. É simples, remove registros obsoletos e limita o impacto da reexecução. O custo é manter versões brutas e identificar qual extração alimentou a versão atual.
2. **Resposta bruta imutável e MERGE na Silver.** A tabela tratada atualiza e insere pelo grão completo, além de excluir, dentro da competência, chaves ausentes na nova resposta. Permite mudanças linha a linha, mas exige uma condição de MERGE longa e uma exclusão cuidadosamente limitada ao mês; sem a exclusão, dados removidos pela fonte ficariam obsoletos na tabela.
3. **Versões estruturadas append-only.** Todas as reexecuções permanecem também na camada tratada, identificadas por versão. Preserva histórico máximo, mas aumenta armazenamento, complexidade das consultas e risco de dupla contagem se o consumidor não selecionar a versão corrente.

## Decisão

Vidal escolheu **resposta bruta imutável e overwrite seletivo do mês na Silver**. O comportamento corresponde à fotografia mensal completa da fonte, torna a reexecução idempotente no dado corrente e preserva o histórico onde ele tem maior valor: a evidência bruta.

Esta decisão não escolhe ainda entre Job e Pipeline nem cria tabelas, volumes ou schemas.

## Consequências

Uma falha antes da substituição não altera a competência publicada; uma execução concluída troca somente o mês validado. Será necessário definir metadados mínimos da extração e retenção do bruto antes da implementação física.

MERGE ou append-only na Silver adicionariam flexibilidade de histórico estruturado, mas exigiriam mais lógica de consumo e qualidade sem uma necessidade observada na V0.
