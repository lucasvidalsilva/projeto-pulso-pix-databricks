# 009 — Execução das tarefas do Job

Status: aceito
Data e hora: 2026-10-03T16:23:50-04:00

## Contexto

O Job mensal precisa baixar uma resposta, preservá-la no Volume, validar o contrato e substituir apenas a competência correspondente na Silver. O projeto já é um pacote Python importável e a Free Edition oferece somente compute serverless. A fronteira de tarefas deve equilibrar simplicidade, teste local, observabilidade e custo de ativação.

Três opções são viáveis:

1. **Uma `python_wheel_task` ponta a ponta (recomendada).** Um único entrypoint recebe `ano_mes`, executa ingestão, preservação, validação e publicação, chamando SQL versionado para a transformação. Evita estado entre tarefas, usa uma ativação serverless e mantém a lógica reutilizável no pacote. Em contrapartida, retry e observabilidade são do fluxo inteiro.
2. **Duas `python_wheel_task`.** A primeira preserva e valida; a segunda publica a Silver. A dependência torna a fronteira explícita e permite retries separados, mas exige transmitir o UUID/caminho da extração por task values e pode ativar compute duas vezes para uma carga pequena.
3. **Wheel para ingestão e `sql_task` para publicação.** Separa claramente Python e SQL e usa o warehouse existente para a Silver. Porém adiciona uma segunda superfície de compute, parâmetros entre tarefas e dependência do warehouse para uma única tabela mensal.

Notebooks produtivos não foram mantidos como uma opção separada: seriam apenas wrappers do mesmo pacote e não resolvem uma necessidade observada nesta V0.

## Decisão

Vidal escolheu a opção 1: **uma `python_wheel_task` ponta a ponta**. O entrypoint recebe `ano_mes`, baixa e preserva a resposta original, valida o contrato e publica a competência na Silver por SQL versionado. A separação interna entre preservar, validar e publicar continua explícita e testável; uma segunda tarefa só deve entrar se surgir necessidade real de retry ou operação independente.

## Consequências

Com uma tarefa, uma falha impede a publicação e a reexecução repete o fluxo completo, preservando uma nova versão bruta. A publicação mensal continua idempotente pelo overwrite seletivo já aceito. Retry, timeout e observabilidade operacional ficam no nível do fluxo inteiro.

Com duas tarefas, o Job ganha granularidade operacional, mas precisa de contrato de handoff e mais configuração. Com `sql_task`, ganha separação por linguagem ao custo de acoplar o fluxo ao warehouse.
