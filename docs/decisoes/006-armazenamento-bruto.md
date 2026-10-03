# 006 — Armazenamento da resposta bruta

Status: aceito
Data e hora: 2026-10-03T09:43:19-04:00

## Contexto

A decisão anterior exige preservar cada resposta JSON original antes de publicar a competência tratada. A [documentação oficial da Databricks](https://docs.databricks.com/aws/en/volumes/volume-files) recomenda Volumes para arquivos JSON de ingestão e tabelas Unity Catalog para dados tabulares. A [Free Edition tem Unity Catalog habilitado por padrão](https://docs.databricks.com/aws/en/getting-started/import-visualize-data), mas as permissões dos catálogos escolhidos ainda precisam ser verificadas no workspace.

Duas opções são viáveis:

1. **Volume gerenciado no schema `bronze`.** Criar o volume `respostas_pix` e organizar os arquivos como `estatisticas_transacoes/ano_mes=202501/extracao_id=<id>/resposta.json`, acompanhado de metadados mínimos e hash. Preserva os bytes da fonte, permite navegação por caminho e usa armazenamento administrado pelo Unity Catalog. Exige privilégios `CREATE VOLUME` e `WRITE VOLUME` e introduz um objeto adicional.
2. **Tabela Delta gerenciada no schema `bronze`.** Manter uma linha por extração com `ano_mes`, `extracao_id`, instante, URL, hash e conteúdo bruto em `BINARY` ou `STRING`. Facilita consultas e controles SQL, mas transforma um envelope JSON não tabular em uma linha grande, mistura metadados com conteúdo e adiciona custo de tabela sem necessidade analítica observada.

My Files e Workspace Files não foram mantidos como opções porque o bruto deve pertencer ao projeto e ser governado junto aos dados. Volume externo também foi excluído porque a Free Edition não oferece localização de armazenamento personalizada.

## Decisão

Vidal escolheu **volume gerenciado `bronze.respostas_pix`**. Ele corresponde ao formato real do artefato, mantém a resposta exata fora da tabela tratada e evita introduzir armazenamento externo ou credenciais de nuvem.

Esta decisão não cria o volume. A capacidade e as permissões serão verificadas antes de qualquer persistência. Não haverá troca automática para uma tabela caso a Free Edition não permita criar ou escrever no Volume; uma alternativa deverá voltar à decisão de Vidal.

## Consequências

Com o volume, a ingestão deverá criar um UUID de extração, calcular SHA-256 e tamanho do conteúdo, registrar instante UTC e URL de origem, gravar sem sobrescrever versões anteriores e só então transformar a resposta validada. O caminho acordado é `estatisticas_transacoes/ano_mes=AAAAMM/extracao_id=<uuid>/resposta.json`. Consultas analíticas continuarão na tabela Silver gerenciada.

Com a tabela Bronze, a auditoria por SQL seria mais direta, mas o conteúdo bruto ficaria acoplado ao modelo tabular e exigiria leitura de linhas grandes para recuperar a resposta original.
