# Mapa do Pulso Pix

## Propósito

Entender comportamento e crescimento do Pix com dados públicos rastreáveis. Investigar risco somente quando os dados e o grão sustentarem a análise. Construir escolhas e evidências que Vidal consiga explicar em entrevista.

## Funcionamento atual

Vidal escolheu a V0 de uso do Pix por segmento, baseada em `EstatisticasTransacoesPix` e limitada ao ano civil de 2025, com uma unidade batch parametrizada por mês. O contrato, o adaptador e uma `python_wheel_task` ponta a ponta estão implantados em `dev`. As 12 competências de 2025 foram preservadas no Volume e publicadas na Silver, totalizando 163.161 linhas validadas no grão da fonte. A primeira Gold aprovada, `workspace.gold.uso_pix_mensal`, materializa 16.496 combinações mensais reconciliadas com a Silver e alimenta um dashboard AI/BI publicado em `dev`.

A sequência abaixo registra o ciclo da V0; todas as etapas foram executadas para o recorte de 2025:

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
| Dados | Medallion como referência; bruto em `bronze.respostas_pix`; qualidade por impacto |
| Catálogo | `workspace`; dados reais apenas em `dev` |
| Ambientes | `dev` implantável; `prod` apenas para validar configuração |
| Entrega contínua | CI sem credenciais em PR; CD aprovado e restrito ao Environment `dev` |
| Documentação | Este mapa + ADRs curtos + README de entrada |
| Entrega | Branch + PR, commits automáticos; checks relevantes |

Detalhes operacionais estão no [AGENTS.md](../AGENTS.md). Método reutilizável está na skill Vidal, instalada no projeto pelo scaffold.

## Evolução e decisões

- [001 — Método de desenvolvimento](decisoes/001-metodo-de-desenvolvimento.md): aceito por Vidal.
- [002 — Primeira entrega de dados Pix](decisoes/002-primeira-entrega-pix.md): opção 1 aceita por Vidal em 2026-10-03.
- [003 — Estratégia de carga da V0](decisoes/003-estrategia-de-carga-v0.md): batch mensal parametrizado aceito por Vidal em 2026-10-03.
- [004 — Isolamento de dados por target](decisoes/004-isolamento-dados-target.md): substituída pela decisão 008 após validação do workspace.
- [005 — Reexecução e histórico mensal](decisoes/005-reexecucao-historico-mensal.md): bruto imutável e overwrite mensal da Silver aceitos por Vidal em 2026-10-03.
- [006 — Armazenamento da resposta bruta](decisoes/006-armazenamento-bruto.md): Volume gerenciado `bronze.respostas_pix` aceito por Vidal em 2026-10-03.
- [007 — Orquestração da V0](decisoes/007-orquestracao-v0.md): Lakeflow Job batch parametrizado aceito por Vidal em 2026-10-03.
- [008 — Isolamento no catálogo do workspace](decisoes/008-isolamento-no-workspace.md): somente `dev` no catálogo `workspace` aceito por Vidal em 2026-10-03.
- [009 — Execução das tarefas do Job](decisoes/009-execucao-tarefas-job.md): uma `python_wheel_task` ponta a ponta aceita por Vidal em 2026-10-03.
- [010 — Primeiro consumo analítico da V0](decisoes/010-primeiro-consumo-gold.md): Gold combinada aceita por Vidal em 2026-10-04.
- [011 — Consumo da Gold em dashboard AI/BI](decisoes/011-consumo-dashboard-aibi.md): dashboard gerenciado aceito por Vidal em 2026-10-05.
- [012 — CD na Free Edition](decisoes/012-cd-na-free-edition.md): deploy em `dev` com PAT temporário e GitHub Environment aceito por Vidal em 2026-10-05.

## Fontes investigadas

### Banco Central do Brasil

O [conjunto Estatísticas do Pix](https://dadosabertos.bcb.gov.br/pt_BR/dataset/pix) tem licença ODbL, periodicidade mensal e início geral informado em novembro de 2020. A especificação Swagger consultada em 2026-10-02 expõe JSON, XML, CSV, texto e HTML, com `$filter`, `$orderby` e `$top`; exige `$top` maior que zero, mas não declara teto nem limite de requisições.

| Recurso | Grão e medidas | Cobertura e atualização | Limites de interpretação |
| --- | --- | --- | --- |
| `EstatisticasTransacoesPix` | Mês × PF/PJ pagador × PF/PJ recebedor × regiões × faixas etárias × forma de iniciação × natureza × finalidade; valor em R$ e quantidade | Primeiro mês `202011` confirmado; atualização mensal; V0 fechada em `202501`–`202512` | Exclui transações liquidadas nos livros do próprio participante e não representa eventos individuais |
| `TransacoesPixPorMunicipio` | Mês × código IBGE do município; valor, quantidade e pessoas pagadoras/recebedoras, separados por PF/PJ | Recurso publicado em 2026-01; uma consulta válida confirmou 2026-08, mas o primeiro mês ainda não foi comprovado | Agregado municipal; não mede adoção individual e também exige filtro explícito para selecionar um mês exato |
| `EstatisticasFraudesPix` | Aparentemente uma linha mensal com contestações, devoluções, valores e bloqueios cautelares do MED | Mensal, publicado 30 dias após o fim do mês; início específico ainda não confirmado | Mede registros do MED, não todas as fraudes Pix; o contrato tem nomenclatura que exige validação antes de publicar indicador |
| `PixUsuariosCadastradosDICT` | Mês; estoques de usuários PF, PJ e total | Estoque no último dia do mês | Usuário cadastrado não equivale a usuário ativo; não usar como taxa de adoção sem denominador e definição adicionais |

Evidência operacional da fonte escolhida: `@Database='202501'` define o início da consulta, não um mês exclusivo. A consulta mensal correta também aplica `$filter=AnoMes eq 202501`. Sem esse filtro, o serviço pode retornar meses posteriores; isso explica a divergência observada anteriormente e não constitui, por si só, corrupção da fonte. Uma consulta ordenada desde `202001` confirmou `202011` como primeiro mês disponível. O serviço ficou lento e respondeu HTTP 500 após uma sequência curta de chamadas, sem publicar teto ou limite de requisições na especificação consultada.

Amostra exata de `202501`, mantida apenas como evidência documental:

| pagador | recebedor | região pagador | região recebedor | iniciação | natureza | valor (R$) | quantidade |
| --- | --- | --- | --- | --- | --- | ---: | ---: |
| PF | PF | SUL | SUL | QRES | P2P | 12.709.601,53 | 81.721 |
| PJ | PJ | SUL | CENTRO-OESTE | QRES | B2B | 15.521.902,07 | 16.482 |
| PF | PF | SUDESTE | SUL | MANU | P2P | 10.970.832,96 | 25.569 |

Dimensões podem ser nulas ou trazer categorias como `Nao informado`. A fronteira de ingestão deve validar campos obrigatórios, mês exato, tipos, não negatividade das medidas e unicidade do grão; também deve tratar HTTP 500 como falha transitória, não como ausência de dados. Nenhuma resposta bruta foi adicionada ao Git.

### IBGE

A [API de localidades](https://servicodados.ibge.gov.br/api/docs/localidades) versão 1.0 fornece o código oficial e a hierarquia territorial corrente. A [API de dados agregados](https://servicodados.ibge.gov.br/api/docs/agregados?versao=3) versão 3 alimenta o SIDRA.

- A tabela 6579 tem grão ano × localidade, variável `9324` em pessoas, periodicidade anual e níveis Brasil, região, UF e município. Os períodos disponíveis vão de 2001 a 2026, com ausências em 2007, 2010, 2022 e 2023; o uso precisa considerar revisões e mudanças territoriais.
- A chave é compatível: `Municipio_Ibge=5103403` no BCB corresponde a Cuiabá na API de localidades. A amostra da tabela 6579 retornou 691.875 pessoas para Cuiabá em 2025.
- A página oficial das estimativas define 1º de julho como data de referência e divulgação anual. A documentação das APIs consultadas não nomeia uma licença específica; o IBGE as publica no contexto de dados abertos, mas a atribuição e os termos exatos devem ser confirmados antes de uma entrega derivada.

Não presumir que MED tem detalhe municipal ou que dados agregados permitem identificar fraude individual. Eventos sintéticos não estão aprovados e, se adotados, devem ter proveniência separada.

## Acesso local e ao workspace

Levantamento inicial em 2026-10-03, antes do deploy:

- disponíveis: Git `2.51.2.windows.1`, uv `0.12.22` e Databricks CLI `v1.19.0` instalada pelo WinGet;
- `python` e `codex` continuam ausentes do `PATH` deste processo; o launcher `py` também não encontrou Python instalado, embora o ambiente gerenciado pelo uv funcione;
- `uv sync --group dev` concluiu e preparou o ambiente local do projeto; a execução do Python desse ambiente exige acesso ao runtime instalado fora do workspace;
- Vidal confirmou o uso do perfil `PULSO_PIX`; `current-user me` validou a identidade ativa e a participação nos grupos `admins` e `users`;
- o workspace é serverless: havia um SQL warehouse `2X-Small` parado, nenhum cluster clássico e nenhum Job existente;
- os únicos catálogos visíveis são `workspace`, `system` e `samples`; `workspace` é gerenciado e contém apenas `default` e `information_schema`, sem tabelas ou Volumes em `default`;
- os privilégios visíveis do metastore não incluem `CREATE CATALOG`; a documentação oficial exige esse privilégio para criar os catálogos separados planejados e orienta a Free Edition a usar `workspace.default`;
- `databricks bundle validate --strict` passou nos targets `dev` e `prod`;
- não havia navegador ou sessão Databricks aberta disponível para inspeção somente leitura pela interface;
- 29 skills oficiais Databricks estão presentes no diretório global do Codex, incluindo as centrais para CLI, DABs, descoberta, SQL, Jobs, Pipelines e Unity Catalog. Não há cópia global da skill `vidal-data-engineering`.

A documentação oficial atual descreve a Free Edition como serverless, sujeita a quotas e com internet de saída restrita a domínios confiáveis. A execução real comprovou acesso de saída ao endpoint do BCB e permissão para criar e gravar nos recursos aprovados.

Validação real no mesmo dia:

- o bundle criou `workspace.bronze`, `workspace.silver`, o Volume gerenciado `workspace.bronze.respostas_pix` e o Job `875157504022557`; `prod` permaneceu sem recursos;
- o primeiro deploy criou os schemas e o Volume, mas a API rejeitou o Job porque serverless não aceita wheel em `task.libraries`; mover o wheel para `environments[].spec.dependencies` resolveu a causa sem mudar a arquitetura;
- a tarefa serverless acessou o BCB, persistiu os bytes originais e publicou a tabela Delta gerenciada `workspace.silver.estatisticas_transacoes`;
- `202501` foi executado duas vezes: a Silver manteve 11.322 linhas e um único `extracao_id`, enquanto o Volume preservou as duas extrações com UUIDs distintos e o mesmo SHA-256;
- as competências `202502`–`202512` foram executadas sequencialmente e concluíram com sucesso.

## Opções de V0

| Opção | Pergunta e recorte | Vantagens | Custos e riscos |
| --- | --- | --- | --- |
| 1 — Uso do Pix por segmento (recomendada) | Como quantidade e valor variaram ao longo de 2025 por natureza, regiões e forma de iniciação? Fonte `EstatisticasTransacoesPix`, grão bruto integral e recorte de 12 meses fechados | Uma fonte, série mais longa, pergunta clara e boa demonstração de modelagem dimensional | Muitas combinações por mês; exige evitar dupla contagem ao agregar e explicitar a exclusão de liquidações internas |
| 2 — Intensidade municipal | Como o uso agregado do Pix se distribui entre municípios em 2026, e o que muda quando normalizado pela estimativa populacional? BCB municipal + IBGE | Chave oficial pronta, resultado territorial intuitivo e duas fontes rastreáveis | Cobertura municipal curta/incerta, API instável, revisão do denominador anual e risco de confundir transações por residente com adoção |
| 3 — Efetividade observada do MED | Como contestações, valores aceitos e devoluções pelo MED evoluem mês a mês? | Conjunto pequeno e tema relevante de risco | Não representa toda fraude, tem defasagem mínima de 30 dias e exige resolver ambiguidades do contrato antes de definir taxas |

A opção 1 foi escolhida por Vidal. Ela entrega entendimento útil com menos premissas e permite validar ingestão, preservação do bruto, qualidade e modelagem antes de adicionar junção municipal ou métricas de risco. O recorte é o ano civil de 2025; ampliar a série histórica será uma decisão posterior, não requisito da V0.

## Implementação e validação da V0

Vidal escolheu executar dados reais somente em `dev`, usando `workspace.bronze`, `workspace.silver` e, após a decisão 010, `workspace.gold`. O target `prod` permanece para validação de configuração, sem recursos de dados implantáveis. Os recursos estão definidos sob `targets.dev.resources`, mantendo a restrição estrutural no bundle.

A resposta bruta imutável e o overwrite seletivo de `ano_mes` na Silver foram aceitos. Vidal escolheu preservar os bytes originais em um Volume gerenciado `bronze.respostas_pix`. O fluxo prepara UUID de extração, instante UTC, URL, SHA-256, tamanho e o caminho `estatisticas_transacoes/ano_mes=.../extracao_id=.../resposta.json`; grava os bytes e um `metadados.json` com criação exclusiva antes de validar a resposta. Assim, uma resposta inválida continua disponível para investigação sem chegar à Silver.

Vidal escolheu um **Lakeflow Job batch**, parametrizado por `ano_mes`, como único recurso de orquestração da V0, e uma única `python_wheel_task` ponta a ponta. O wheel executa ingestão e qualidade em Python, carrega transformações declarativas de SQLs empacotados e grava tabelas Delta. A Silver `workspace.silver.estatisticas_transacoes` mantém o grão mês × PF/PJ pagador × PF/PJ recebedor × regiões × faixas etárias × forma de iniciação × natureza × finalidade.

A Gold `workspace.gold.uso_pix_mensal` responde à pergunta aprovada no grão mês × natureza × forma de iniciação × região pagadora × região recebedora, com `valor_total` e `quantidade_total`. A mesma tarefa publica primeiro a Silver e depois a Gold; ambas usam `replaceWhere` limitado à competência solicitada. Não há transação entre as duas tabelas: uma falha parcial deixa o Job com falha, e a reexecução mensal idempotente é o mecanismo de reparo.

O bundle declara apenas no target `dev` os schemas `workspace.bronze`, `workspace.silver` e `workspace.gold`, o Volume gerenciado, o Job serverless e o dashboard AI/BI. O modo automático `development` não é usado porque a CLI atual prefixaria nomes e violaria os schemas exatos escolhidos; o isolamento continua explícito pelo target, caminho de estado e nomes `[dev]`. O target `prod` mantém `mode: production`, mas resolve zero recursos implantáveis.

Vidal escolheu um dashboard AI/BI como primeiro consumo da Gold. O recurso `[dev] Pulso Pix - uso em 2025` usa o warehouse serverless existente e uma única consulta portável, com catálogo e schema parametrizados pelo bundle. A página principal apresenta KPIs de valor, quantidade e cobertura, tendências mensais, segmentos e fluxo regional; uma página global oferece filtros por natureza, iniciação e regiões pagadora e recebedora. Os gráficos exibem as quatro categorias principais de natureza e iniciação e agrupam a cauda em `Outras`, sem alterar os valores originais disponíveis nos filtros.

O dashboard está [publicado no workspace](https://dbc-6f6e2ab0-1349.cloud.databricks.com/dashboardsv3/01f1c0dca5481bbc9007062a6b7297b7/published?w=7474650652244145). Spark Declarative Pipeline, streaming, Auto Loader, CDC, simulador e ML não entram nesta entrega.

## CI/CD seguro

O CI de pull request não recebe credenciais e executa instalação bloqueada pelo `uv.lock`,
Ruff, formatação, 53 testes, cobertura mínima de 85% e inspeção do wheel. As GitHub Actions de
terceiros estão fixadas por commit completo. Concorrência e timeout impedem execuções locais
obsoletas ou indefinidas.

O workflow de CD só é elegível depois de um CI aprovado em `main` ou por disparo manual. O
GitHub Environment `dev` deve exigir aprovação e conter `DATABRICKS_HOST` como variável e
`DATABRICKS_TOKEN` como segredo temporário. O token é disponibilizado somente às etapas que
chamam a CLI Databricks. O deploy recebe o SHA do commit como `versao_implantacao`, gravado nas
tags do Job para relacionar código e recurso implantado.

O caminho automático valida estritamente `dev` e `prod`, implanta apenas `dev` e registra o
resumo do bundle. O smoke end-to-end de `202501` é manual: ele comprova ingestão e publicação
reais quando necessário; por não rodar em cada merge, evita acumular uma nova extração bruta
e consumir quota a cada mudança.
O target `prod` continua sem recursos porque o workspace gratuito não oferece isolamento
adequado para chamá-lo de produção.

## Evidências e limites

Foram validados metadados oficiais, contrato de campos, primeiro mês da fonte escolhida, semântica do filtro mensal, uma chave de junção IBGE e pequenas respostas das APIs. O contrato, a persistência bruta, a preparação tipada, os SQLs, o overwrite seletivo e a estrutura do dashboard passaram por 53 testes unitários, lint e verificação de formatação. A cobertura local medida após a decisão 012 foi de 89,76%. O wheel contém o entrypoint e os SQLs de Silver e Gold; a CLI validou estritamente `dev` e `prod`.

Resultado estrutural da Silver atual:

| Competência | Linhas | Competência | Linhas |
| --- | ---: | --- | ---: |
| `202501` | 11.322 | `202507` | 14.739 |
| `202502` | 11.301 | `202508` | 15.451 |
| `202503` | 11.428 | `202509` | 15.386 |
| `202504` | 11.477 | `202510` | 15.468 |
| `202505` | 11.510 | `202511` | 17.285 |
| `202506` | 11.662 | `202512` | 16.132 |

Na versão atual, `202501`–`202512` somam 163.161 linhas e 163.161 grupos no grão completo, com zero grupos duplicados, maior multiplicidade igual a 1, zero medidas negativas e zero nulos nos campos críticos de medida e rastreabilidade. Há 12 `extracao_id` na Silver, um por competência corrente, e 12 diretórios mensais no Volume. Após a retrocarga da Gold, o Volume preserva 25 versões brutas: três para janeiro e duas para cada outro mês.

O histórico Delta da Silver comprova 25 operações `WRITE`, todas com `mode=Overwrite` e predicado `ano_mes = AAAAMM`. O runtime serverless também executou nove operações automáticas `OPTIMIZE`; elas são comportamento observado da plataforma, não um recurso configurado pelo projeto.

Resultado estrutural da Gold validada em 2026-10-04:

| Competência | Linhas | Competência | Linhas |
| --- | ---: | --- | ---: |
| `202501` | 1.265 | `202507` | 1.382 |
| `202502` | 1.271 | `202508` | 1.437 |
| `202503` | 1.274 | `202509` | 1.456 |
| `202504` | 1.292 | `202510` | 1.440 |
| `202505` | 1.301 | `202511` | 1.497 |
| `202506` | 1.346 | `202512` | 1.535 |

As 16.496 linhas correspondem a 16.496 grupos no grão escolhido, com zero duplicidades, maior multiplicidade igual a 1, zero medidas nulas ou negativas e mínimos observados de R$ 0,01 e uma transação. A reconciliação por mês encontrou 12 meses comparados, nenhum ausente e diferença máxima zero para valor e quantidade. O histórico Delta da Gold registra 12 `WRITE`, um por competência, todos com overwrite seletivo mensal. As 12 execuções da retrocarga terminaram com `SUCCESS` no Job `875157504022557`.

A consulta do dashboard foi executada no warehouse `845f16074a5f97c8` antes do deploy e retornou as 16.496 linhas, 12 meses e cinco grupos visuais por segmentação. O bundle criou e publicou o dashboard `01f1c0dca5481bbc9007062a6b7297b7`; a API confirmou estado ativo, revisão publicada, catálogo `workspace`, schema `gold`, warehouse correto e credenciais não incorporadas. A inspeção visual automatizada não foi executada porque nenhuma superfície de navegador estava disponível nesta sessão; isso permanece como limite de validação, não como evidência de falha do recurso.

A fonte não declara paginação na especificação consultada; por segurança, o contrato rejeita qualquer resposta com `nextLink` em vez de publicar mês incompleto. As contagens mensais acima são evidências estruturais, não explicam causas para aumento ou queda do uso do Pix. Não há benchmark de custo ou desempenho, SLA, dados em `prod` ou inferência sobre transações individuais.

O novo workflow de CD está implementado e validado localmente, mas ainda precisa da criação do
GitHub Environment, do PAT temporário e de uma execução remota bem-sucedida antes de ser
classificado como validado.

O material de divulgação está implementado como uma capa vetorial própria e um texto para o
LinkedIn. A peça usa os nomes OpenAI Codex e Databricks apenas para identificar as tecnologias,
sem reproduzir ou fundir seus logos e sem sugerir parceria. O texto permanece marcado como
rascunho até a primeira validação remota do CD em `dev`.

Depois de uma entrega, registrar aqui: pergunta → decisão → implementação → evidência → limite, com links para código e ADR quando necessários.
