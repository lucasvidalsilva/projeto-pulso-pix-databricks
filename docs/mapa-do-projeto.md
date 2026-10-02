# Mapa do Pulso Pix

## Propósito

Entender comportamento e crescimento do Pix com dados públicos rastreáveis. Investigar risco somente quando os dados e o grão sustentarem a análise. Construir escolhas e evidências que Vidal consiga explicar em entrevista.

## Funcionamento atual

Scaffold e regras de trabalho disponíveis. A investigação inicial de fontes foi realizada em 2026-10-02 e a V0 aguarda escolha de Vidal. Nenhum dado foi ingerido e nenhum recurso Databricks foi criado.

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
- [002 — Primeira entrega de dados Pix](decisoes/002-primeira-entrega-pix.md): proposta com três opções; aguarda escolha de Vidal.

## Fontes investigadas

### Banco Central do Brasil

O [conjunto Estatísticas do Pix](https://dadosabertos.bcb.gov.br/pt_BR/dataset/pix) tem licença ODbL, periodicidade mensal e início geral informado em novembro de 2020. A especificação Swagger consultada em 2026-10-02 expõe JSON, XML, CSV, texto e HTML, com `$filter`, `$orderby` e `$top`; exige `$top` maior que zero, mas não declara teto nem limite de requisições.

| Recurso | Grão e medidas | Cobertura e atualização | Limites de interpretação |
| --- | --- | --- | --- |
| `EstatisticasTransacoesPix` | Mês × PF/PJ pagador × PF/PJ recebedor × regiões × faixas etárias × forma de iniciação × natureza × finalidade; valor em R$ e quantidade | Conjunto mensal desde 2020-11; cobertura exata do recurso ainda precisa de enumeração operacional | Exclui transações liquidadas nos livros do próprio participante e não representa eventos individuais |
| `TransacoesPixPorMunicipio` | Mês × código IBGE do município; valor, quantidade e pessoas pagadoras/recebedoras, separados por PF/PJ | Recurso publicado em 2026-01; uma consulta válida confirmou 2026-08, mas o primeiro mês ainda não foi comprovado | Agregado municipal; não mede adoção individual e apresentou comportamento inconsistente para mês inválido |
| `EstatisticasFraudesPix` | Aparentemente uma linha mensal com contestações, devoluções, valores e bloqueios cautelares do MED | Mensal, publicado 30 dias após o fim do mês; início específico ainda não confirmado | Mede registros do MED, não todas as fraudes Pix; o contrato tem nomenclatura que exige validação antes de publicar indicador |
| `PixUsuariosCadastradosDICT` | Mês; estoques de usuários PF, PJ e total | Estoque no último dia do mês | Usuário cadastrado não equivale a usuário ativo; não usar como taxa de adoção sem denominador e definição adicionais |

Evidência operacional: uma chamada de `TransacoesPixPorMunicipio` solicitando `202608` com `$top=3` retornou três linhas marcadas como `AnoMes=202610`. Uma consulta posterior filtrada para Cuiabá retornou corretamente `202608`; uma solicitação de um mês antigo (`202401`) devolveu `202512` em vez de erro. Depois de uma sequência curta de chamadas, o serviço passou a responder HTTP 500 inclusive em consulta isolada. A amostra inesperada continha, por exemplo, Santa Inês/PR (`Municipio_Ibge=4123600`), com `VL_PagadorPF=415371,82` e `QT_PagadorPF=1944`, mas ela não deve sustentar análise porque o mês retornado divergiu do solicitado.

Consequência para qualquer opção: validar `AnoMes` contra o parâmetro, rejeitar resposta divergente, manter retry com espera e não interpretar HTTP 500 como ausência de dados. Nenhuma amostra foi adicionada ao Git.

### IBGE

A [API de localidades](https://servicodados.ibge.gov.br/api/docs/localidades) versão 1.0 fornece o código oficial e a hierarquia territorial corrente. A [API de dados agregados](https://servicodados.ibge.gov.br/api/docs/agregados?versao=3) versão 3 alimenta o SIDRA.

- A tabela 6579 tem grão ano × localidade, variável `9324` em pessoas, periodicidade anual e níveis Brasil, região, UF e município. Os períodos disponíveis vão de 2001 a 2026, com ausências em 2007, 2010, 2022 e 2023; o uso precisa considerar revisões e mudanças territoriais.
- A chave é compatível: `Municipio_Ibge=5103403` no BCB corresponde a Cuiabá na API de localidades. A amostra da tabela 6579 retornou 691.875 pessoas para Cuiabá em 2025.
- A página oficial das estimativas define 1º de julho como data de referência e divulgação anual. A documentação das APIs consultadas não nomeia uma licença específica; o IBGE as publica no contexto de dados abertos, mas a atribuição e os termos exatos devem ser confirmados antes de uma entrega derivada.

Não presumir que MED tem detalhe municipal ou que dados agregados permitem identificar fraude individual. Eventos sintéticos não estão aprovados e, se adotados, devem ter proveniência separada.

## Acesso local e ao workspace

Verificação em 2026-10-02, sem criar recursos:

- disponíveis: Git `2.51.2.windows.1` e uv `0.12.22`;
- ausentes do `PATH`: `python`, `codex` e `databricks`; o launcher `py` também não encontrou Python instalado;
- a listagem de Python pelo uv foi bloqueada pelo acesso ao cache do usuário fora do sandbox;
- por falta da Databricks CLI, não foi possível executar `databricks auth profiles`, `databricks aitools list --scope global` nem `databricks current-user me --profile PULSO_PIX`;
- 29 skills oficiais Databricks estão presentes no diretório global do Codex, incluindo as centrais para CLI, DABs, descoberta, SQL, Jobs, Pipelines e Unity Catalog. Não há cópia global da skill `vidal-data-engineering`.

A documentação oficial atual descreve a Free Edition como serverless, sujeita a quotas e com internet de saída restrita a domínios confiáveis. Depois da instalação oficial da CLI, ainda será necessário validar autenticação, permissões, catálogo, serverless e acesso de saída ao BCB/IBGE no workspace real.

## Opções de V0

| Opção | Pergunta e recorte | Vantagens | Custos e riscos |
| --- | --- | --- | --- |
| 1 — Uso do Pix por segmento (recomendada) | Como quantidade e valor variaram ao longo de 2025 por natureza, regiões e forma de iniciação? Fonte `EstatisticasTransacoesPix`, grão bruto integral e recorte de 12 meses fechados | Uma fonte, série mais longa, pergunta clara e boa demonstração de modelagem dimensional | Muitas combinações por mês; exige evitar dupla contagem ao agregar e explicitar a exclusão de liquidações internas |
| 2 — Intensidade municipal | Como o uso agregado do Pix se distribui entre municípios em 2026, e o que muda quando normalizado pela estimativa populacional? BCB municipal + IBGE | Chave oficial pronta, resultado territorial intuitivo e duas fontes rastreáveis | Cobertura municipal curta/incerta, API instável, revisão do denominador anual e risco de confundir transações por residente com adoção |
| 3 — Efetividade observada do MED | Como contestações, valores aceitos e devoluções pelo MED evoluem mês a mês? | Conjunto pequeno e tema relevante de risco | Não representa toda fraude, tem defasagem mínima de 30 dias e exige resolver ambiguidades do contrato antes de definir taxas |

A recomendação é a opção 1: ela entrega entendimento útil com menos premissas e permite validar ingestão, preservação do bruto, qualidade e modelagem antes de adicionar junção municipal ou métricas de risco. O recorte proposto é o ano civil de 2025; ampliar a série histórica seria uma etapa posterior, não requisito da V0.

## Próxima decisão e entrega

Vidal deve escolher a opção 1, 2 ou 3 do ADR 002. Depois da escolha e da instalação da CLI, verificar o workspace sem criar dados; em seguida, apresentar separadamente as opções de isolamento de `dev` e `portfolio` antes da primeira persistência. Criar somente a implementação escolhida.

## Evidências e limites

Foram validados metadados oficiais, contratos de campos, uma chave de junção IBGE e pequenas respostas das APIs. A instabilidade do endpoint BCB e a ausência da CLI impedem classificar a fonte ou o workspace como validados para execução. Ainda não há pipeline, tabela, benchmark, teste Databricks ou deploy.

Depois de uma entrega, registrar aqui: pergunta → decisão → implementação → evidência → limite, com links para código e ADR quando necessários.
