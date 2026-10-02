# Mapa do Pulso Pix

## Propósito

Entender comportamento e crescimento do Pix com dados públicos rastreáveis. Investigar risco somente quando os dados e o grão sustentarem a análise. Construir escolhas e evidências que Vidal consiga explicar em entrevista.

## Funcionamento atual

Scaffold e regras de trabalho disponíveis. Nenhum dado ingerido ou recurso Databricks criado.

A sequência abaixo é uma orientação de investigação, não um pipeline implementado:

1. Verificar fonte, grão, cobertura, licença, atualização e acesso.
2. Escolher a primeira pergunta e a menor entrega útil.
3. Preservar a entrada; tratar e validar conforme seu impacto.
4. Publicar indicador com consumidor e definição claros.
5. Verificar resultado e registrar evidência e limites.

## Escolhas vigentes

| Tema | Convenção |
| --- | --- |
| Participação | Vidal escolhe arquitetura; agente executa detalhes e etapas |
| Código | Português, SQL declarativo; Python/PySpark conforme necessidade |
| Organização | Contexto próximo, menos arquivos; notebooks conforme propósito |
| Dados | Medallion como referência, bruto preservado, qualidade por impacto |
| Catálogo lógico | `pulso_pix`; `bronze`, `silver`, `gold`, `sandbox` conforme necessidade |
| Ambientes | `dev` e `portfolio` no mesmo workspace; separar dados antes de escrever |
| Documentação | Este mapa + ADRs curtos + README de entrada |
| Entrega | Branch + PR, commits automáticos; checks relevantes |

Detalhes operacionais estão no [AGENTS.md](../AGENTS.md). Método reutilizável está na skill Vidal, instalada no projeto pelo scaffold.

## Evolução e decisões

- [001 — Método de desenvolvimento](decisoes/001-metodo-de-desenvolvimento.md): aceito por Vidal.
- Próxima decisão: primeira fonte, pergunta analítica, grão e recorte da V0.

## Fontes candidatas

- BCB: estatísticas públicas do Pix; verificar recursos específicos antes de definir indicadores.
- IBGE: contexto municipal; verificar chaves, períodos e compatibilidade antes de cruzar.

Não presumir que MED tem detalhe municipal ou que dados agregados permitem identificar fraude individual. Eventos sintéticos não estão aprovados e, se adotados, devem ter proveniência separada.

## Próxima entrega

Investigar uma fonte real, amostra e contrato; verificar acesso do workspace; apresentar 2–3 opções de V0 com trade-offs e aguardar Vidal. Criar somente a implementação escolhida.

## Evidências e limites

Ainda não há resultados de dados, benchmarks, testes Databricks ou deploy. Validação do scaffold não valida uma solução de dados.

Depois de uma entrega, registrar aqui: pergunta → decisão → implementação → evidência → limite, com links para código e ADR quando necessários.
