# 001 — Método de desenvolvimento

Status: aceito
Data e hora: 2026-10-02T11:08:47-04:00

## Contexto

Vidal quer um portfólio com participação real nas decisões, dados úteis e capacidade de apresentar cases. Automatizar todas as escolhas reduziria sua participação; exigir aprovação para cada detalhe tornaria a execução lenta. A estrutura anterior tinha mais pastas do que a entrega inicial exige.

## Decisão

Escolha de Vidal: perguntar antes de decisões arquiteturais, mostrar alternativas e trade-offs, documentar escolhas em ADRs e executar detalhes rotineiros autonomamente. Manter um mapa central enxuto, português nos artefatos de domínio, contexto próximo e testes de transformação, contratos e casos críticos. Usar tecnologias apenas com necessidade real, Medallion como referência e ML opcional.

Adotar `dev` e `portfolio` como targets com isolamento lógico no mesmo workspace Free Edition. Verificar suporte real e consultar Vidal se um recurso não estiver disponível. O scaffold prepara caminhos separados de bundle; a estratégia de isolamento de dados precisa de decisão antes da primeira escrita.

## Consequências

Positivas: escolhas rastreáveis, autoria das decisões preservada, menos ruído e melhores condições para explicar o projeto.

Negativas: decisões importantes dependem da disponibilidade de Vidal; menos fragmentação requer atenção ao tamanho dos módulos; a Free Edition limita a fidelidade de uma operação de produção. Cobertura de certificação não será usada para justificar tecnologia sem necessidade.

Este ADR consolida preferências confirmadas. Não aprova fontes, pipeline, autenticação de CI/CD ou caso de ML.
