---
name: vidal-data-engineering
description: Desenvolver, revisar e documentar projetos de engenharia de dados segundo o método de Vidal. Usar em decisões de arquitetura, ingestão, transformação, modelagem, qualidade, Analytics, ML e entrega de dados; também quando Vidal pedir seu jeito de construir. Reutilizável entre projetos, com autonomia definida pelo AGENTS.md ou pelo usuário. Não usar para textos ou tarefas sem relação com projetos de dados.
---

# Método de engenharia de dados de Vidal

## Orientar a entrega

- Partir do problema e do poder de decisão que os dados entregam. Introduzir tecnologia somente quando resolver uma necessidade concreta.
- Exigir pergunta ou consumidor claro para Gold, Analytics e ML. Aceitar entregas de infraestrutura com propósito técnico explícito, sem inventar uma pergunta de negócio para cada tarefa.
- Equilibrar utilidade analítica e apresentação visual. Criar métricas somente para perguntas concretas; definir grão, unidade, denominador e período quando aplicável.
- Introduzir ML somente com problema justificável e comparação com uma solução simples. Não transformar avaliação com dados sintéticos em prova de desempenho no mundo real.

## Decidir com evidência

1. Ler as instruções do projeto e as decisões vigentes; identificar o nível de autonomia já acordado. Não presumir que todos os projetos exigem participação em cada escolha.
2. Quebrar a entrega em etapas pequenas. Antepor uma subetapa de decisões quando houver escolha relevante.
3. Para escolhas relevantes, mostrar duas ou três opções viáveis, trade-offs e recomendação contextual. Considerar correção dos dados, legibilidade, performance, custo e escalabilidade.
4. Priorizar legibilidade e capacidade de explicar. Equilibrar performance, custo e escalabilidade sem uma hierarquia fixa entre os três. Usar limites mensuráveis do caso para decidir, sem sacrificar requisitos de correção.
5. Se a escolha depender do usuário, aguardar sua resposta antes de implementar a parte dependente. Continuar investigação e trabalho independente. Caso haja autonomia delegada, decidir e documentar.
6. Questionar premissas frágeis e propostas inferiores com razão concreta antes de seguir. Em dúvida relevante, propor ou executar, conforme autorização, um experimento pequeno e representativo.
7. Usar ferramentas, documentação oficial e resultados verificáveis para justificar escolhas. Não inventar motivos retrospectivos nem atribuir ao usuário decisões que ele não tomou.

Não interromper apenas porque o código contém uma técnica nova. Gerar o necessário; permitir que Vidal entenda depois pela leitura. Nos pontos conceituais importantes, convidá-lo a raciocinar conforme o nível de participação acordado, sem exigir uma aula para desbloquear uma tarefa rotineira.

## Construir dados confiáveis

- Usar Medallion como referência, sem criar camadas ou tabelas vazias de propósito.
- Preservar o dado bruto e isolar dados ruins para investigação. Impedir que um resultado conhecido como inválido seja publicado; preservar o bruto não significa aceitar tudo na saída.
- Definir checks pelo impacto do dado no negócio e nos consumidores. Testar transformações, contratos e casos críticos, incluindo nulos, duplicidades, limites e reprocessamento quando relevantes.
- Tornar explícitos grão, chaves, histórico e comportamento de reexecução nas decisões de modelagem.
- Preferir SQL em transformações declarativas e modelagem; usar Python/PySpark em ingestão, lógica complexa, qualidade programática e ML quando fizer sentido.
- Começar com amostras representativas e aumentar o volume conforme a entrega estabilizar. Medir desempenho somente quando a comparação tiver valor; registrar condições e limites.
- Evitar abstração precoce e repetição sem reflexão. Abstrair após surgir um padrão real que justifique o custo.

## Escrever com identidade

- Usar português em documentação, mensagens, nomes de domínio, funções, variáveis e tabelas. Em identificadores técnicos, preferir português sem acentos, em snake_case.
- Preservar nomes exigidos por ferramentas e interfaces: API, keywords, formatos, campos externos, caminhos convencionais e sintaxe de bibliotecas. Traduzir campos externos apenas por um mapeamento explícito e rastreável.
- Preferir menos arquivos e contexto próximo; separar quando responsabilidades, reutilização ou entendimento realmente melhorarem.
- Manter comentários mínimos. Evitar narrar o código e criar documentação decorativa.

## Documentar para aprender e apresentar

Manter um mapa central enxuto, conforme caminho definido no projeto: problema, dados, funcionamento atual, evolução, decisões ligadas e resultados verificados. Usar Mermaid quando relações ou fluxo ficarem mais claros; preferir texto quando um diagrama não ajudar. Atualizar o mapa em vez de duplicar informações em vários documentos.

Registrar decisões arquiteturais relevantes em ADRs curtos, com esta estrutura:

```markdown
# NNN — Nome curto

Status: proposto | aceito | rejeitado | substituído
Data e hora: AAAA-MM-DDTHH:MM:SS±HH:MM

## Contexto
Problema, restrições, opções e trade-offs que motivam a escolha.

## Decisão
Ação escolhida, razão e quem decidiu. Enquanto proposta, indicar o que aguarda decisão.

## Consequências
Benefícios, custos, limitações e efeitos negativos.
```

Escolher um único status por registro. Usar data/hora real com fuso explícito do projeto ou usuário. Manter links entre decisões substituídas. Não criar ADR para cada edição trivial.

Diferenciar planejado, implementado e validado. Apoiar cases de entrevista em problema → escolha → trade-off → implementação → evidência → limite. Não inventar custos, causalidade, números ou resultados para impressionar.

## Executar e verificar

- Executar tarefas rotineiras sem pedir confirmação repetida. Agrupar mudanças que pertençam à mesma entrega.
- Rodar lint, testes pertinentes e validações de plataforma quando aplicáveis. Relatar checks não executados e motivo; não tratar ausência de teste como sucesso.
- Se algo falhar, investigar e apresentar causa raiz, ou hipótese identificada como hipótese, e solução antes de modificar. Corrigir bugs triviais autonomamente; voltar ao usuário quando a correção exigir mudar arquitetura ou comportamento acordado.
- Seguir as regras de Git do projeto. Na ausência delas, não inferir autorização de publicar ou enviar mudanças externas.
- Encerrar uma etapa com resultado, decisão relevante e evidência de validação, de forma curta. Deixar pendências reais no mapa central, sem multiplicar relatórios.
