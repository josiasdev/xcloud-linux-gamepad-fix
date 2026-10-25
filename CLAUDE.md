# Instruções para Assistentes de IA (Claude, Cursor, Windsurf)

## Padrão de Commits
Você deve seguir o padrão **Conventional Commits**:
- `feat:` Funcionalidades.
- `fix:` Correções de bugs.
- `refactor:` Alterações de código que não mudam comportamento.
- `docs:` Documentação.
- `chore:` Manutenção (Makefile, configs, dependências).

## Git Flow
- **Nunca** faça alterações diretamente na `main`.
- Sempre crie uma branch: `feature/nome-da-feature`, `bugfix/nome-do-bug` ou `hotfix/nome-do-erro`.
- **Aprovação Obrigatória:** Antes de executar qualquer comando `git commit` ou `git push`, você **DEVE** perguntar ao usuário e obter aprovação explícita.

## Governança
- PRs ou alterações não devem ser feitas sem uma Issue aberta e discutida previamente.
- Se o usuário pedir uma mudança, verifique se existe uma Issue associada. Caso contrário, pergunte se o usuário deseja abrir uma primeiro.
