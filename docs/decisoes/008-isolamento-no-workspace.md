# 008 — Isolamento no catálogo do workspace

Status: aceito
Data e hora: 2026-10-03T16:04:50-04:00

## Contexto

A [decisão 004](004-isolamento-dados-target.md) separou `dev` e `prod` nos catálogos `pulso_pix_dev` e `pulso_pix_prod`, condicionada à capacidade real da Free Edition. A inspeção somente leitura do perfil `PULSO_PIX` mostrou apenas os catálogos `workspace`, `system` e `samples`. Os privilégios visíveis do metastore não incluem `CREATE CATALOG`; o catálogo gerenciado `workspace` contém somente `default` e `information_schema`.

A documentação oficial informa que criar catálogo exige `CREATE CATALOG` no metastore e orienta usuários da Free Edition a utilizar o catálogo `workspace`, onde possuem privilégios no schema `default`. Portanto, os catálogos separados não podem ser tratados como disponíveis sem uma criação que o workspace atual não demonstrou permitir.

Três alternativas são viáveis:

1. **Schemas por projeto, target e camada no catálogo `workspace` (recomendada).** Usar `pulso_pix_dev_bronze`, `pulso_pix_dev_silver`, `pulso_pix_dev_gold` e equivalentes `prod`. Mantém o isolamento em securables distintos, evita colisão com outros projetos e preserva nomes de entidades como `estatisticas_transacoes`. O custo é ter nomes de schema mais longos e adaptar a convenção original de schema igual apenas à camada.
2. **Um schema por target.** Usar `workspace.pulso_pix_dev` e `workspace.pulso_pix_prod`, levando a camada para os nomes dos objetos, como `bronze_respostas_pix` e `silver_estatisticas_transacoes`. Cria menos schemas, mas mistura camadas sob a mesma fronteira de permissões e repete estágio em objetos.
3. **Somente `dev` na Free Edition.** Usar `workspace.bronze`, `workspace.silver` e `workspace.gold`, mantendo `prod` apenas como configuração não implantável. É a alternativa mais simples, mas elimina a paridade dos targets e não demonstra isolamento lógico entre desenvolvimento e produção.

## Decisão

Vidal escolheu **somente `dev` na Free Edition**. Os dados reais usarão `workspace.bronze`, `workspace.silver` e, quando houver consumidor aprovado, `workspace.gold`. O target `prod` permanece no bundle para validar configuração em modo production, mas não receberá recursos de dados nem será implantado neste workspace.

Nenhum schema, Volume ou tabela foi criado durante a investigação.

## Consequências

O bundle passa a parametrizar o catálogo fixo `workspace` e os schemas de camada. O bruto de desenvolvimento ficará em `workspace.bronze.respostas_pix`, e a tabela tratada em `workspace.silver.estatisticas_transacoes`.

Recursos de dados e Jobs serão declarados apenas dentro de `targets.dev.resources`, uma capacidade confirmada no schema da CLI `v1.19.0`. Assim, validar `prod` não adiciona recursos e um deploy acidental desse target não aponta para os objetos de `dev`. O custo é não haver paridade real nem evidência de produção; `mode: production` continuará sendo apenas validação de configuração. A decisão 004 foi marcada como substituída.
