# Mapa do Pulso Pix

## Propósito

Entender comportamento e crescimento do Pix com dados públicos rastreáveis. Investigar risco somente quando os dados e o grão sustentarem a análise. Construir escolhas e evidências que Vidal consiga explicar em entrevista.

## Funcionamento atual

Scaffold e regras de trabalho disponíveis. Vidal escolheu a V0 de uso do Pix por segmento, baseada em `EstatisticasTransacoesPix` e limitada ao ano civil de 2025, com uma unidade batch parametrizada por mês. O contrato, o adaptador e uma `python_wheel_task` ponta a ponta estão implementados localmente; nenhum dado foi persistido, nenhum recurso Databricks foi criado e nenhum deploy foi executado.

A sequência abaixo registra o ciclo da V0; as etapas 1–4 têm implementação local e a etapa 5 depende da execução no Databricks:

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

Verificação em 2026-10-03, sem criar recursos:

- disponíveis: Git `2.51.2.windows.1`, uv `0.12.22` e Databricks CLI `v1.19.0` instalada pelo WinGet;
- `python` e `codex` continuam ausentes do `PATH` deste processo; o launcher `py` também não encontrou Python instalado, embora o ambiente gerenciado pelo uv funcione;
- `uv sync --group dev` concluiu e preparou o ambiente local do projeto; a execução do Python desse ambiente exige acesso ao runtime instalado fora do workspace;
- Vidal confirmou o uso do perfil `PULSO_PIX`; `current-user me` validou a identidade ativa e a participação nos grupos `admins` e `users`;
- o workspace é serverless: há um SQL warehouse `2X-Small` parado, nenhum cluster clássico e nenhum Job existente;
- os únicos catálogos visíveis são `workspace`, `system` e `samples`; `workspace` é gerenciado e contém apenas `default` e `information_schema`, sem tabelas ou Volumes em `default`;
- os privilégios visíveis do metastore não incluem `CREATE CATALOG`; a documentação oficial exige esse privilégio para criar os catálogos separados planejados e orienta a Free Edition a usar `workspace.default`;
- `databricks bundle validate --strict` passou nos targets `dev` e `prod`; nenhum deploy foi executado;
- não havia navegador ou sessão Databricks aberta disponível para inspeção somente leitura pela interface;
- 29 skills oficiais Databricks estão presentes no diretório global do Codex, incluindo as centrais para CLI, DABs, descoberta, SQL, Jobs, Pipelines e Unity Catalog. Não há cópia global da skill `vidal-data-engineering`.

A documentação oficial atual descreve a Free Edition como serverless, sujeita a quotas e com internet de saída restrita a domínios confiáveis. Autenticação, catálogo e compute foram inspecionados; permissões de criação e acesso de saída ao BCB/IBGE só poderão ser comprovados por uma execução posterior à decisão de isolamento.

## Opções de V0

| Opção | Pergunta e recorte | Vantagens | Custos e riscos |
| --- | --- | --- | --- |
| 1 — Uso do Pix por segmento (recomendada) | Como quantidade e valor variaram ao longo de 2025 por natureza, regiões e forma de iniciação? Fonte `EstatisticasTransacoesPix`, grão bruto integral e recorte de 12 meses fechados | Uma fonte, série mais longa, pergunta clara e boa demonstração de modelagem dimensional | Muitas combinações por mês; exige evitar dupla contagem ao agregar e explicitar a exclusão de liquidações internas |
| 2 — Intensidade municipal | Como o uso agregado do Pix se distribui entre municípios em 2026, e o que muda quando normalizado pela estimativa populacional? BCB municipal + IBGE | Chave oficial pronta, resultado territorial intuitivo e duas fontes rastreáveis | Cobertura municipal curta/incerta, API instável, revisão do denominador anual e risco de confundir transações por residente com adoção |
| 3 — Efetividade observada do MED | Como contestações, valores aceitos e devoluções pelo MED evoluem mês a mês? | Conjunto pequeno e tema relevante de risco | Não representa toda fraude, tem defasagem mínima de 30 dias e exige resolver ambiguidades do contrato antes de definir taxas |

A opção 1 foi escolhida por Vidal. Ela entrega entendimento útil com menos premissas e permite validar ingestão, preservação do bruto, qualidade e modelagem antes de adicionar junção municipal ou métricas de risco. O recorte é o ano civil de 2025; ampliar a série histórica será uma decisão posterior, não requisito da V0.

## Implementação local da V0

Vidal escolheu executar dados reais somente em `dev`, usando `workspace.bronze`, `workspace.silver` e `workspace.gold`. O target `prod` permanece para validação de configuração, sem recursos de dados implantáveis. A CLI confirmou que recursos podem ser definidos sob `targets.dev.resources`, mantendo a restrição estrutural no bundle.

A resposta bruta imutável e o overwrite seletivo de `ano_mes` na Silver foram aceitos. Vidal escolheu preservar os bytes originais em um Volume gerenciado `bronze.respostas_pix`. O fluxo prepara UUID de extração, instante UTC, URL, SHA-256, tamanho e o caminho `estatisticas_transacoes/ano_mes=.../extracao_id=.../resposta.json`; grava os bytes e um `metadados.json` com criação exclusiva antes de validar a resposta. Assim, uma resposta inválida continua disponível para investigação sem chegar à Silver.

Vidal escolheu um **Lakeflow Job batch**, parametrizado por `ano_mes`, como único recurso de orquestração da V0, e uma única `python_wheel_task` ponta a ponta. O wheel executa ingestão e qualidade em Python, carrega a transformação declarativa de um SQL empacotado e grava `workspace.silver.estatisticas_transacoes` em Delta. O grão continua sendo mês × PF/PJ pagador × PF/PJ recebedor × regiões × faixas etárias × forma de iniciação × natureza × finalidade; `replaceWhere` limita o overwrite à competência solicitada.

O bundle declara apenas no target `dev` os schemas `workspace.bronze` e `workspace.silver`, o Volume gerenciado e o Job serverless. O modo automático `development` não é usado porque a CLI atual prefixaria nomes e violaria os schemas exatos escolhidos; o isolamento continua explícito pelo target, caminho de estado e nome `[dev]` do Job. O target `prod` mantém `mode: production`, mas resolve zero recursos implantáveis.

Spark Declarative Pipeline, streaming, Auto Loader, CDC, simulador, ML e Gold não entram nesta entrega. A próxima etapa operacional é um deploy controlado em `dev` e uma execução de `202501`; isso exige autorização de execução e poderá comprovar permissões de criação, saída serverless para o BCB, persistência no Volume e comportamento Delta real.

## Evidências e limites

Foram validados metadados oficiais, contrato de campos, primeiro mês da fonte escolhida, semântica do filtro mensal, uma chave de junção IBGE e pequenas respostas das APIs. O contrato, a persistência bruta, a preparação tipada, o SQL e o overwrite seletivo passaram por 48 testes unitários, lint e verificação de formatação; uma verificação de integração somente leitura baixou uma linha de `202501` pelo adaptador e passou no validador. O wheel foi construído e contém o entrypoint e o SQL. A CLI validou estritamente `dev` com os nomes `workspace.bronze`, `workspace.silver` e `/Volumes/workspace/bronze/respostas_pix`; também confirmou que `prod` resolve sem recursos.

A fonte não declara paginação na especificação consultada; por segurança, o contrato rejeita qualquer resposta com `nextLink` em vez de publicar mês incompleto. Ainda não foram comprovados no serverless a saída de rede para o BCB, as permissões de criação/gravação nem o `replaceWhere` no Delta real. Não há Volume, Job ou tabela criados, benchmark, teste Databricks ou deploy.

Depois de uma entrega, registrar aqui: pergunta → decisão → implementação → evidência → limite, com links para código e ADR quando necessários.
