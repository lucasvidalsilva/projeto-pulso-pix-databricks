# 002 — Primeira entrega de dados Pix

Status: aceito
Data e hora: 2026-10-03T00:36:41-04:00

## Contexto

A V0 precisa responder uma pergunta útil com dados públicos reais, preservar rastreabilidade e caber nas restrições da Databricks Free Edition. A investigação oficial encontrou quatro recursos principais do BCB, com licença ODbL e atualização mensal, e duas APIs do IBGE capazes de fornecer código territorial e estimativa populacional anual.

Foram consideradas três opções:

1. **Uso do Pix por segmento.** Usar `EstatisticasTransacoesPix` no ano civil de 2025 para explicar a evolução mensal de quantidade e valor por natureza, regiões e forma de iniciação. O grão bruto inclui ainda PF/PJ de pagador e recebedor, faixas etárias e finalidade. É a alternativa com série mais longa, uma única fonte e menos premissas, mas exige impedir dupla contagem em agregações e registrar que o recurso exclui transações liquidadas internamente pelos participantes.
2. **Intensidade municipal.** Usar `TransacoesPixPorMunicipio` em 2026, enriquecido pela API de localidades e pela estimativa populacional anual do IBGE. A chave municipal oficial é compatível e o resultado tem leitura territorial forte. Em contrapartida, a cobertura municipal observada é curta e ainda não foi delimitada; o endpoint apresentou retorno de mês diferente do solicitado e HTTP 500. Transações por residente não podem ser chamadas de adoção individual.
3. **Efetividade observada do MED.** Usar `EstatisticasFraudesPix` para acompanhar contestações, valores aceitos e devoluções. É um conjunto pequeno e relevante para risco, mas cobre apenas ocorrências registradas pelo MED, tem publicação 30 dias após o mês e contém uma definição de campo cuja nomenclatura e fórmula precisam ser reconciliadas antes de publicar taxa.

A Free Edition é serverless, limitada por quotas e por saída de rede. Nesta máquina, Git e uv estão disponíveis, mas Python, Codex CLI e Databricks CLI não estão no `PATH`. Portanto, autenticação, permissões, catálogo e acesso aos endpoints a partir do workspace ainda não foram validados. Nenhum recurso foi criado.

## Decisão

Vidal escolheu a **opção 1**, com recorte fechado de janeiro a dezembro de 2025. A V0 usará `EstatisticasTransacoesPix` para explicar a evolução mensal de quantidade e valor por natureza, regiões e forma de iniciação, preservando o grão integral da fonte na entrada.

Esta proposta não decide batch versus streaming, Jobs versus Pipelines, estratégia de escrita, histórico ou isolamento físico/lógico de dados. Streaming, simulador, CDC e ML permanecem fora do escopo.

## Consequências

Positivas: primeira entrega pequena e real; uma única licença e API; grão explícito; espaço para demonstrar contrato, idempotência, qualidade e agregação correta sem introduzir infraestrutura adicional.

Negativas: a consulta exige combinar o parâmetro de início `@Database` com um filtro exato de `AnoMes`; sem esse filtro, meses posteriores também podem ser retornados. A ingestão deverá rejeitar mês divergente, aplicar retry com espera para falhas transitórias e preservar evidência da resposta bruta. O recorte de 2025 não representa toda a história do Pix e a fonte agregada não permite conclusões sobre indivíduos ou fraude.
