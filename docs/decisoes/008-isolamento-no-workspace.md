# 008 — Isolamento no catálogo do workspace

Status: proposto
Data e hora: 2026-10-03T11:59:22-04:00

## Contexto

A [decisão 004](004-isolamento-dados-target.md) separou `dev` e `prod` nos catálogos `pulso_pix_dev` e `pulso_pix_prod`, condicionada à capacidade real da Free Edition. A inspeção somente leitura do perfil `PULSO_PIX` mostrou apenas os catálogos `workspace`, `system` e `samples`. Os privilégios visíveis do metastore não incluem `CREATE CATALOG`; o catálogo gerenciado `workspace` contém somente `default` e `information_schema`.

A documentação oficial informa que criar catálogo exige `CREATE CATALOG` no metastore e orienta usuários da Free Edition a utilizar o catálogo `workspace`, onde possuem privilégios no schema `default`. Portanto, os catálogos separados não podem ser tratados como disponíveis sem uma criação que o workspace atual não demonstrou permitir.

Três alternativas são viáveis:

1. **Schemas por projeto, target e camada no catálogo `workspace` (recomendada).** Usar `pulso_pix_dev_bronze`, `pulso_pix_dev_silver`, `pulso_pix_dev_gold` e equivalentes `prod`. Mantém o isolamento em securables distintos, evita colisão com outros projetos e preserva nomes de entidades como `estatisticas_transacoes`. O custo é ter nomes de schema mais longos e adaptar a convenção original de schema igual apenas à camada.
2. **Um schema por target.** Usar `workspace.pulso_pix_dev` e `workspace.pulso_pix_prod`, levando a camada para os nomes dos objetos, como `bronze_respostas_pix` e `silver_estatisticas_transacoes`. Cria menos schemas, mas mistura camadas sob a mesma fronteira de permissões e repete estágio em objetos.
3. **Somente `dev` na Free Edition.** Usar `workspace.bronze`, `workspace.silver` e `workspace.gold`, mantendo `prod` apenas como configuração não implantável. É a alternativa mais simples, mas elimina a paridade dos targets e não demonstra isolamento lógico entre desenvolvimento e produção.

## Decisão

Aguardando escolha de Vidal.

Recomendação técnica: **schemas por projeto, target e camada no catálogo `workspace`**. Essa opção preserva a intenção da decisão anterior com os recursos realmente observados e mantém a separação verificável por nomes e permissões, sem fingir que a Free Edition oferece catálogos que não estão disponíveis.

Nenhum schema, Volume ou tabela foi criado durante a investigação.

## Consequências

Se a opção recomendada for aceita, o bundle passará a parametrizar catálogo fixo `workspace` e prefixo de schema por target. O bruto de desenvolvimento ficará em `workspace.pulso_pix_dev_bronze.respostas_pix`, e a tabela tratada em `workspace.pulso_pix_dev_silver.estatisticas_transacoes`; `prod` terá objetos equivalentes e separados.

As outras opções reduzem o número de schemas, mas enfraquecem a separação por camada ou removem o ambiente de produção da execução real. A decisão 004 deverá ser marcada como substituída somente depois da escolha de Vidal.
