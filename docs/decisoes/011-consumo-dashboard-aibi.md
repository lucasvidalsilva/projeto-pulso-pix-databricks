# 011 — Consumo da Gold em dashboard AI/BI

Status: aceito
Data e hora: 2026-10-05T12:52:09-04:00

## Contexto

A Gold `workspace.gold.uso_pix_mensal` está validada e precisa de uma primeira forma de consumo. Foram apresentadas três opções:

1. consultas SQL versionadas, com menor custo e validação direta das perguntas;
2. notebook analítico, com narrativa exploratória e maior acoplamento à interface;
3. dashboard AI/BI, com melhor apresentação e filtros interativos, ao custo de adicionar um recurso gerenciado e depender de SQL warehouse.

## Decisão

Vidal escolheu a opção 3: um dashboard AI/BI versionado no bundle e implantado somente em `dev`.

O dashboard apresenta totais anuais, cobertura temporal, tendências mensais de valor e quantidade, segmentos por natureza e forma de iniciação e fluxo regional. Usa filtros globais para as quatro dimensões aprovadas. Para legibilidade, os gráficos de segmentos exibem as quatro categorias principais e agrupam a cauda como `Outras`; os filtros preservam as categorias originais.

## Consequências

A entrega cria uma superfície gerenciada, somente leitura e reproduzível pelo bundle, ligada ao SQL warehouse existente. O dashboard não cria novas métricas de negócio nem altera a Gold. A atualização do dashboard exige validar a consulta no warehouse, validar o JSON e publicar nova revisão.

O target `prod` continua sem recursos. A validação automatizada e a API confirmam a publicação, mas a inspeção visual ficou pendente porque esta sessão não expôs navegador autenticado para automação.
