# Pulso Pix

Projeto brasileiro de engenharia e produto de dados sobre o Pix, construído com participação ativa de Vidal e apoio do Codex.

**Estado:** fonte, recorte, batch mensal e isolamento por catálogos definidos; contrato e adaptador local validados. Ainda não há persistência, recurso Databricks, dashboard ou resultado analítico.

O projeto prioriza dados úteis, escolhas explicáveis e evidência. Streaming, simulador e ML só entram com problema real que justifique seu uso.

- [Mapa do projeto](docs/mapa-do-projeto.md): funcionamento, evolução e decisões.
- [Instruções de desenvolvimento](AGENTS.md): método, ambiente, Git e Databricks.
- [Decisão inicial](docs/decisoes/001-metodo-de-desenvolvimento.md).

## Ambiente

Python 3.11+, Git, uv, Codex CLI e Databricks CLI atual. Instalar pelo guia oficial do sistema operacional; não usar o pacote legado `databricks-cli` do pip. Configuração completa e links estão no AGENTS.md.

```bash
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
```

Versionar `uv.lock` após a primeira sincronização. O workflow inicial valida Python; testes de dados e validação remota entram quando existirem implementações e autenticação apropriada. Nenhum deploy é disparado pelo CI inicial.

```bash
databricks aitools install --agents codex --scope project --skills-only
databricks auth login --host https://SEU-WORKSPACE --profile PULSO_PIX
databricks current-user me --profile PULSO_PIX
codex
```

No Codex, conferir `/skills` e pedir leitura do AGENTS.md e da skill Vidal. A primeira etapa é verificar fontes e propor uma entrega pequena, com pergunta e trade-offs para escolha de Vidal.

## Ambientes

`dev` e `prod` compartilham o workspace gratuito. O bundle parametriza os catálogos `pulso_pix_dev` e `pulso_pix_prod`; a criação deles ainda depende da validação das permissões no workspace. Não tratar o modo `production` como infraestrutura de produção. O bundle não provisiona recursos.
