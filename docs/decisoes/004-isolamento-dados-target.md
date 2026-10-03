# 004 — Isolamento de dados por target

Status: aceito
Data e hora: 2026-10-03T08:46:23-04:00

## Contexto

Os targets `dev` e `prod` usarão o mesmo workspace, mas não podem sobrescrever os dados um do outro. O isolamento precisa ser explícito antes da primeira persistência. A Databricks CLI não está disponível e não havia sessão do workspace aberta no navegador, portanto permissões e capacidade de criar múltiplos catálogos ainda não foram verificadas.

Duas opções são viáveis:

1. **Catálogos separados por target.** Usar `pulso_pix_dev` e `pulso_pix_prod`, cada um com schemas `bronze`, `silver` e `gold` criados apenas quando necessários. A fronteira é clara, permissões e caminhos são mais fáceis de explicar e os nomes das camadas permanecem simples. Em contrapartida, exige suporte e permissão para múltiplos catálogos e cria mais objetos de governança.
2. **Catálogo único com schemas por target.** Usar `pulso_pix` com schemas como `dev_bronze`, `dev_silver`, `prod_bronze` e `prod_silver`. É mais provável de funcionar com permissões restritas e reduz a quantidade de catálogos. Em contrapartida, multiplica schemas, enfraquece a fronteira de isolamento e exige atenção adicional em nomes parametrizados.

Não foi mantida como opção uma única sequência `bronze`/`silver`/`gold` compartilhada pelos dois targets: ela permitiria colisão e não atende à regra de impedir que `dev` sobrescreva `prod` por padrão.

## Decisão

Vidal escolheu **catálogos separados por target** e definiu a nomenclatura `prod` no lugar de `portfolio`. O bundle usará os targets `dev` e `prod`, parametrizados respectivamente com `pulso_pix_dev` e `pulso_pix_prod`.

A decisão continua condicionada à validação de suporte e permissões no workspace. Se a Free Edition real não permitir os dois catálogos, nenhuma alternativa será aplicada sem nova escolha de Vidal.

Esta decisão não cria catálogos ou schemas e não escolhe a operação de escrita nem a tecnologia de orquestração.

## Consequências

Com catálogos separados, o target determina o catálogo e as tabelas mantêm o mesmo nome lógico entre ambientes. Há melhor contenção de erros, ao custo de depender de permissões ainda não verificadas. A nomenclatura anterior `portfolio`, registrada no ADR 001, foi substituída por `prod` para este projeto.

Com catálogo único, a solução tem maior chance de funcionar sob restrições da Free Edition, mas o isolamento depende da parametrização correta de cada schema e de checks contra referências cruzadas.
