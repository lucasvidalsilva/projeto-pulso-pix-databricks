# Pulso Pix — instruções para agentes

## Propósito e estado

Construir um portfólio brasileiro de engenharia e produto de dados com Databricks Free Edition, Git, CLI e Declarative Automation Bundles (DABs). Entregar entendimento sobre o Pix com dados rastreáveis e escolhas que Vidal consiga defender em entrevista. Não implementar recursos apenas para cobrir uma certificação.

Este scaffold define convenções, não uma arquitetura de dados concluída. Consultar `docs/mapa-do-projeto.md` para estado atual, próximos passos e evidências. Fontes BCB/IBGE são candidatas até verificar endpoints, licença, grão, cobertura, periodicidade e limites. Simulador, streaming, CDC e ML não estão aprovados.

## Método e decisões

- Ler `.agents/skills/vidal-data-engineering/SKILL.md` e aplicar seu método. Este arquivo define as regras específicas do Pulso Pix; a skill é reutilizável.
- Quebrar o trabalho em etapas e executar. Em cada etapa, incluir uma subetapa de decisões somente se houver escolha relevante.
- Vidal participa ativamente: antes de decidir arquitetura, apresentar 2–3 opções, trade-offs e recomendação; fazer uma pergunta direta e aguardar a escolha. Isso inclui fontes/grão, batch versus streaming, MERGE versus overwrite, histórico, Jobs versus Pipelines, armazenamento, autenticação de deploy e novas tecnologias.
- Não repetir decisões já aceitas. Detalhes mecânicos, correções triviais e verificações seguem autonomamente. Continuar tarefas independentes enquanto aguarda uma escolha.
- Se perceber premissa frágil ou alternativa melhor, explicar o motivo antes de seguir. Não substituir silenciosamente o pedido.
- Investigar falhas e apresentar causa raiz, ou hipótese claramente identificada, e solução antes de corrigir. Corrigir bugs triviais sozinho; consultar Vidal quando a solução mudar arquitetura ou comportamento acordado.
- Não interromper só para ensinar sintaxe nova nem marcar código como ponto de aprendizado. Em decisões importantes, convidar Vidal a pensar; depois da escolha, implementar.

## Convenções de dados e código

- Usar português em comunicação, documentação e nomes de domínio; usar português sem acentos em identificadores, snake_case em funções/colunas/tabelas e nomes curtos em arquivos. Preservar nomes exigidos por APIs, ferramentas e linguagens: `src`, `tests`, `resources`, `AGENTS.md`, `SKILL.md`, `databricks.yml`, `pyproject.toml`, campos YAML e sintaxe SQL/Python.
- Preferir SQL para transformação declarativa e modelagem. Usar Python/PySpark para ingestão, lógica complexa, qualidade programática e ML quando necessário.
- Preferir menos arquivos, com contexto próximo. Lógica reutilizável deve ser importável; notebooks podem ser produtivos, exploratórios ou analíticos se houver propósito claro. Não duplicar lógica entre notebook e módulo.
- Manter comentários mínimos. Abstrair somente após surgir padrão real.
- Priorizar legibilidade e capacidade de explicar; equilibrar performance, custo e escalabilidade conforme evidência. Correção dos dados é requisito.
- Usar Medallion como referência. Convenção lógica: catálogo `pulso_pix`, schemas `bronze`, `silver`, `gold`, `sandbox`; criar apenas o necessário e verificar catálogo/permissões disponíveis. Schema indica camada; tabela indica entidade, sem repetir estágio no nome.
- Usar grão e chaves explícitos. Definir reexecução e idempotência por ingestão. Preservar bruto, isolar dados inválidos e impedir saída sabidamente incorreta. Checks devem refletir impacto para o consumidor.
- Toda Gold precisa de consumidor ou propósito claro. Exigir pergunta concreta para Analytics/ML e métricas; equilibrar análise e apresentação. ML só entra com necessidade real.
- Começar pequeno e aumentar o volume progressivamente. Não inferir resultados nacionais ou individuais a partir de dados com outro grão. Não misturar MED agregado e eventos sintéticos como se fossem transações reais rotuladas.

## Estrutura e documentação

- `src/pulso_pix/`: lógica produtiva agrupada por contexto; criar módulos conforme a primeira entrega exigir.
- `resources/`: Jobs/Pipelines versionados, adicionados após decisão; incluir seus YAMLs no bundle quando existirem.
- `tests/unitarios/` e `tests/integracao/`: transformações, contratos e casos críticos.
- `notebooks/exploracao/`: ponto inicial para exploração; mover/organizar outros notebooks conforme uso aprovado.
- `contratos/`: contratos que validem fronteiras reais de dados.
- `docs/mapa-do-projeto.md`: documento central navegável com funcionamento, evolução, decisões e resultados. Evitar `architecture.md` duplicado.
- `docs/decisoes/`: ADRs curtos, sequenciais, com Título, Status + data/hora, Contexto, Decisão e Consequências positivas/negativas. Contexto inclui opções/trade-offs; Decisão identifica a escolha de Vidal. Usar data real em America/Cuiaba e ISO 8601 com offset; não inventar data ou aprovação.
- `README.md`: entrada enxuta com propósito, estado, execução e link para o mapa.
- `.agents/skills/vidal-data-engineering/`: skill no caminho descoberto pelo Codex; evitar uma segunda cópia em `agent/skills/`.

Atualizar o mapa com cada entrega relevante. Distinguir proposto, implementado e validado. ADRs registram decisões, não cada edição. Resultados de entrevista devem incluir condições de medição e limites; não inventar números.

## Configurar Codex, CLI e skills

Começar na raiz do repositório. Verificar antes de instalar: `git --version`, `python --version`, `uv --version`, `codex --version`, `databricks version`. O scaffold precisa de Python 3.11+ e Git; configuração completa também precisa de uv, Codex CLI e Databricks CLI atual com `aitools`.

Instalar ferramentas ausentes pela documentação oficial para o sistema operacional. Não instalar o pacote Python legado `databricks-cli` como substituto da CLI atual. Não fixar modelo do Codex nem desativar permissões globalmente. Não editar configurações pessoais fora do escopo sem necessidade.

```bash
uv sync --group dev
databricks aitools install --agents codex --scope project --skills-only
databricks aitools list --scope project
databricks auth login --host https://SEU-WORKSPACE --profile PULSO_PIX
databricks current-user me --profile PULSO_PIX
```

O comando `aitools` instala conhecimento, não autentica o workspace. Conferir `databricks aitools install --help` se a CLI não reconhecer as opções; atualizar pela fonte oficial em vez de inventar comandos alternativos. Carregar a skill oficial central e a skill do recurso usado quando disponíveis. Não presumir que todas as skills listadas anteriormente são estáveis ou instaladas.

Manter a skill Vidal versionada no projeto para reprodução. Não copiar também para o escopo global na mesma máquina, pois skills com o mesmo nome não são mescladas. Para outros projetos, reutilizar o conteúdo, respeitando seu próprio AGENTS.md.

Abrir `codex` na raiz; conferir `/skills` e solicitar que resuma as instruções ativas antes da primeira entrega. O prompt inicial do scaffold pede investigação da primeira fonte e decisão de V0; não autoriza um lakehouse completo sem participação de Vidal.

Referências oficiais de configuração:

- https://developers.openai.com/codex/cli
- https://developers.openai.com/codex/guides/agents-md
- https://developers.openai.com/codex/skills
- https://docs.databricks.com/aws/en/dev-tools/cli/install
- https://docs.databricks.com/aws/en/dev-tools/cli/reference/aitools-commands
- https://docs.databricks.com/aws/en/dev-tools/cli/authentication

## Free Edition, bundle e credenciais

- Usar targets `dev` (development) e `portfolio` (production), no mesmo workspace. `production` é modo do bundle, não prova de infraestrutura produtiva ou SLA. Isolamento é lógico e precisa ser implementado, não presumido.
- O bundle inicial separa caminhos de recursos por target; os schemas de dados ainda dependem da escolha e implementação. Ao criar dados, parametrizar isolamento: propor catálogo por target, se permitido, ou schemas separados, e pedir a escolha de Vidal antes de persistir dados. Não permitir que `dev` sobrescreva `portfolio` por padrão.
- Verificar permissões, serverless, saída de rede, quotas e disponibilidade no workspace real. Se um recurso não existir na Free Edition, perguntar a Vidal antes de escolher alternativa. Não implementar arquitetura paga ou enterprise como substituição automática.
- Nenhuma credencial no código, bundle, notebook, log ou commit. Usar OAuth U2M local; `.env` só local para valores que precisem dele, sem presumir carregamento automático. Config sensível no CI usa GitHub Secrets; Databricks secrets apenas quando disponível.
- CI local pode existir sem credenciais Databricks. Validar autenticação não interativa antes de escolher CD; não levar cache OAuth pessoal ao GitHub Actions. OIDC/service principal ou PAT são alternativas a verificar, não capacidades garantidas da Free Edition.
- Bundle inicial não provisiona recursos. Só executar deploy/run após existir entrega e target configurados; verificar perfil, workspace e target explícitos. Não usar `destroy` para limpeza rotineira.

```bash
databricks bundle validate -t dev --profile PULSO_PIX
databricks bundle validate -t portfolio --profile PULSO_PIX
```

Validar o target pertinente a cada mudança. Deploy futuro, após decisão e autorização de execução:

```bash
databricks bundle deploy -t dev --profile PULSO_PIX
databricks bundle run -t dev --profile PULSO_PIX CHAVE_DO_JOB
```

## Git e ciclo de entrega

- Trabalhar em `main` + branches + PR para `main`. Padrão: `YYYYMMDD-vidal-feat-nome-curto` ou `YYYYMMDD-vidal-fix-nome-curto`; `fix/feat` indica alternativas, não barra literal. Exemplo: `20261002-vidal-feat-ingestao-pix`. Usar data local de Vidal e nome sem acentos.
- Fazer commits automáticos pequenos ao concluir entregas coerentes, após checks pertinentes. Tipos em inglês; descrição em português: `feat: adiciona ingestao historica do pix`, `docs: registra decisao de modelagem`. Não inventar identidade Git nem incluir alterações de terceiros.
- Preparar PR com problema, resultado, decisão e validação. Executar push/criação remota quando houver pedido ou autorização no contexto; a opção por commits automáticos não resolve sozinha publicação remota ou merge.
- Agrupar várias partes quando fazem parte da mesma entrega. Não fazer commits diretamente na main durante desenvolvimento.
- Não armazenar caches, credenciais, dados brutos ou saídas volumosas no Git. Revisar diff e status antes de stage/commit.
- Rodar `uv run ruff check .` e `uv run ruff format --check .`; rodar `uv run pytest tests/unitarios` quando existirem testes aplicáveis; validar bundle quando código/recursos de plataforma mudarem. Rodar integração real quando houver infraestrutura e sentido para a entrega. Gerar/versionar `uv.lock` com uv; CI passa a usar `--locked` depois disso.
- Falha de teste não se resolve removendo assert ou afrouxando contrato para obter verde. Relatar checks bloqueados e não confundir pytest sem testes com validação do pipeline.

## Primeira etapa autorizada

Investigar fontes e acesso ao workspace, propor uma primeira entrega pequena de dados reais e apresentar a decisão de V0 a Vidal. Documentar proposta no mapa/ADR; implementar ingestão, modelagem e recursos somente após as escolhas necessárias. Não criar simulador, streaming, CDC, ML ou dashboard como obrigação do scaffold.
