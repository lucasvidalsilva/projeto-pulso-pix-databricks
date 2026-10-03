# Mapa do Pulso Pix

## Propósito

Entender comportamento e crescimento do Pix com dados públicos rastreáveis. Investigar risco somente quando os dados e o grão sustentarem a análise. Construir escolhas e evidências que Vidal consiga explicar em entrevista.

## Funcionamento atual

Scaffold e regras de trabalho disponíveis. Vidal escolheu a V0 de uso do Pix por segmento, baseada em `EstatisticasTransacoesPix` e limitada ao ano civil de 2025, com uma unidade batch parametrizada por mês. O contrato e o adaptador local da fonte estão implementados; nenhum dado foi persistido e nenhum recurso Databricks foi criado.

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
| Dados | Medallion como referência; bruto em `bronze.respostas_pix`; qualidade por impacto |
| Catálogos | `pulso_pix_dev` e `pulso_pix_prod`; sujeitos à validação no workspace |
| Ambientes | `dev` e `prod` no mesmo workspace; isolamento por catálogo |
| Documentação | Este mapa + ADRs curtos + README de entrada |
| Entrega | Branch + PR, commits automáticos; checks relevantes |

Detalhes operacionais estão no [AGENTS.md](../AGENTS.md). Método reutilizável está na skill Vidal, instalada no projeto pelo scaffold.

## Evolução e decisões

- [001 — Método de desenvolvimento](decisoes/001-metodo-de-desenvolvimento.md): aceito por Vidal.
- [002 — Primeira entrega de dados Pix](decisoes/002-primeira-entrega-pix.md): opção 1 aceita por Vidal em 2026-10-03.
- [003 — Estratégia de carga da V0](decisoes/003-estrategia-de-carga-v0.md): batch mensal parametrizado aceito por Vidal em 2026-10-03.
- [004 — Isolamento de dados por target](decisoes/004-isolamento-dados-target.md): catálogos separados e nomenclatura `dev`/`prod` aceitos por Vidal em 2026-10-03.
- [005 — Reexecução e histórico mensal](decisoes/005-reexecucao-historico-mensal.md): bruto imutável e overwrite mensal da Silver aceitos por Vidal em 2026-10-03.
- [006 — Armazenamento da resposta bruta](decisoes/006-armazenamento-bruto.md): Volume gerenciado `bronze.respostas_pix` aceito por Vidal em 2026-10-03.
- [007 — Orquestração da V0](decisoes/007-orquestracao-v0.md): proposta; aguarda escolha de Vidal.

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

- disponíveis: Git `2.51.2.windows.1` e uv `0.12.22`;
- ausentes do `PATH`: `python`, `codex` e `databricks`; o launcher `py` também não encontrou Python instalado;
- `uv sync --group dev` concluiu e preparou o ambiente local do projeto; a execução do Python desse ambiente exige acesso ao runtime instalado fora do workspace;
- por falta da Databricks CLI, não foi possível executar `databricks auth profiles`, `databricks aitools list --scope global` nem `databricks current-user me --profile PULSO_PIX`;
- não havia navegador ou sessão Databricks aberta disponível para inspeção somente leitura pela interface;
- 29 skills oficiais Databricks estão presentes no diretório global do Codex, incluindo as centrais para CLI, DABs, descoberta, SQL, Jobs, Pipelines e Unity Catalog. Não há cópia global da skill `vidal-data-engineering`.

A documentação oficial atual descreve a Free Edition como serverless, sujeita a quotas e com internet de saída restrita a domínios confiáveis. Depois da instalação oficial da CLI, ainda será necessário validar autenticação, permissões, catálogo, serverless e acesso de saída ao BCB/IBGE no workspace real.

## Opções de V0

| Opção | Pergunta e recorte | Vantagens | Custos e riscos |
| --- | --- | --- | --- |
| 1 — Uso do Pix por segmento (recomendada) | Como quantidade e valor variaram ao longo de 2025 por natureza, regiões e forma de iniciação? Fonte `EstatisticasTransacoesPix`, grão bruto integral e recorte de 12 meses fechados | Uma fonte, série mais longa, pergunta clara e boa demonstração de modelagem dimensional | Muitas combinações por mês; exige evitar dupla contagem ao agregar e explicitar a exclusão de liquidações internas |
| 2 — Intensidade municipal | Como o uso agregado do Pix se distribui entre municípios em 2026, e o que muda quando normalizado pela estimativa populacional? BCB municipal + IBGE | Chave oficial pronta, resultado territorial intuitivo e duas fontes rastreáveis | Cobertura municipal curta/incerta, API instável, revisão do denominador anual e risco de confundir transações por residente com adoção |
| 3 — Efetividade observada do MED | Como contestações, valores aceitos e devoluções pelo MED evoluem mês a mês? | Conjunto pequeno e tema relevante de risco | Não representa toda fraude, tem defasagem mínima de 30 dias e exige resolver ambiguidades do contrato antes de definir taxas |

A opção 1 foi escolhida por Vidal. Ela entrega entendimento útil com menos premissas e permite validar ingestão, preservação do bruto, qualidade e modelagem antes de adicionar junção municipal ou métricas de risco. O recorte é o ano civil de 2025; ampliar a série histórica será uma decisão posterior, não requisito da V0.

## Próxima decisão e entrega

O isolamento por catálogos foi aceito e parametrizado localmente: `dev` aponta para `pulso_pix_dev`; `prod`, para `pulso_pix_prod`. A configuração ainda não foi validada pela Databricks CLI nem aplicada no workspace.

A resposta bruta imutável e o overwrite seletivo de `ano_mes` na Silver foram aceitos. Vidal escolheu preservar os bytes originais em um Volume gerenciado `bronze.respostas_pix`. O contrato local prepara UUID de extração, instante UTC, URL, SHA-256, tamanho e o caminho `estatisticas_transacoes/ano_mes=.../extracao_id=.../resposta.json`; a gravação ainda não foi implementada nem executada.

A próxima decisão é a orquestração:

1. **Lakeflow Job com tarefas batch (recomendado):** recebe `ano_mes`, coordena ingestão Python e publicação Silver, com dependências, retries e histórico de execução em um único recurso. A transformação pode permanecer em SQL. É a menor solução para a V0, mas os checks e o overwrite seletivo ficam explícitos no código.
2. **Lakeflow Job + Spark Declarative Pipeline:** o Job preserva o bruto e aciona um Pipeline batch para a Silver. Acrescenta expectativas e linhagem administradas à transformação, ao custo de dois recursos e maior complexidade operacional para uma única fonte.

Pipeline isolado não resolve sozinho os efeitos da chamada HTTP e da escrita imutável. Streaming e Auto Loader permanecem fora do escopo. A verificação real do workspace, do Volume e de qualquer recurso escolhido depende da instalação da Databricks CLI atual.

## Evidências e limites

Foram validados metadados oficiais, contrato de campos, primeiro mês da fonte escolhida, semântica do filtro mensal, uma chave de junção IBGE e pequenas respostas das APIs. O contrato, o adaptador mensal e o preparo do artefato bruto passaram por 40 testes unitários, lint e verificação de formatação; uma verificação de integração somente leitura baixou uma linha de `202501` pelo adaptador e passou no validador. A resposta bruta continua disponível em bytes para persistência futura, sem transformação silenciosa. A instabilidade transitória do endpoint e a ausência da CLI impedem classificar a fonte ou o workspace como validados para execução produtiva. Ainda não há Volume criado, pipeline, tabela, benchmark, teste Databricks ou deploy.

Depois de uma entrega, registrar aqui: pergunta → decisão → implementação → evidência → limite, com links para código e ADR quando necessários.
