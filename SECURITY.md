# Segurança

## Credenciais

O projeto não aceita credenciais, tokens, arquivos `.env`, perfis Databricks ou respostas
brutas no Git. A automação de deploy usa um segredo restrito ao GitHub Environment `dev`;
workflows de pull request não recebem acesso ao workspace.

Se uma credencial for exposta, revogue-a antes de remover o conteúdo do histórico e registre
o incidente sem reproduzir o valor sensível.

## Relato de vulnerabilidade

Não publique tokens, dados pessoais ou detalhes exploráveis em uma issue. Use a opção
**Report a vulnerability** na aba **Security** do repositório. Se ela não estiver disponível,
avise o mantenedor pelo perfil do GitHub sem incluir o segredo ou a prova de exploração.

## Desenvolvimento assistido

Alterações produzidas com apoio do Codex seguem as mesmas revisões, testes e proteções das
demais contribuições. O agente não recebe credenciais persistentes no código ou em prompts e
decisões de arquitetura permanecem humanas e registradas nos ADRs.
