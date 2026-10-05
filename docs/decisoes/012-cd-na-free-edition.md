# 012 — CD na Free Edition

Status: aceito
Data e hora: 2026-10-05T19:14:05-04:00

## Contexto

A primeira entrega já possuía CI local, bundle implantado manualmente em `dev` e evidências
reais do pipeline, mas não havia deploy acionado pelo GitHub. A Free Edition não oferece
account console nem APIs de conta; por isso, service principal com federação OIDC não foi
tratado como capacidade disponível.

Foram consideradas três opções:

1. manter CI no GitHub e deploy local com OAuth U2M, sem credencial persistente, mas sem CD;
2. implantar em `dev` por GitHub Actions com PAT temporário, GitHub Environment e aprovação;
3. migrar para trial ou conta paga para usar service principal, OIDC e ambientes realmente
   isolados.

## Decisão

Vidal escolheu a opção 2 em 2026-10-05. O CI de pull request permanece sem credenciais. Após
um CI aprovado em `main`, o CD usa o Environment `dev`, valida os targets, implanta o bundle e
registra o resumo. Uma execução end-to-end de `202501` fica disponível somente por disparo
manual para não consumir quota nem depender da API do BCB em cada merge.

O target `prod` continua sem recursos. Não será criado um falso ambiente produtivo dentro do
mesmo catálogo e workspace apenas para demonstrar promoção.

## Consequências

Positivas:

- há uma trilha verificável entre commit, CI e implantação do bundle;
- segredos não são disponibilizados a código de pull request;
- aprovação, concorrência única e expiração do PAT reduzem o risco operacional;
- o smoke manual demonstra a execução real sem tornar todo merge dependente da fonte externa.

Negativas:

- o PAT pertence a um usuário e precisa de expiração, rotação e revogação;
- a implantação continua limitada a `dev` e ao único workspace gratuito;
- não há SLA, isolamento real de produção nem autenticação federada sem segredo persistente.
