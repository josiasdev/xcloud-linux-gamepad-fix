# Contribuindo

Obrigado por se interessar em melhorar este projeto!

## Workflow de Desenvolvimento

1. Faça o Fork do repositório.
2. Crie sua feature branch: `git checkout -b feat/nova-melhoria`.
3. Configure o ambiente local:
   ```bash
   make install-deps
   ```
4. Verifique a qualidade do código:
   ```bash
   make lint
   make test
   ```
5. Envie seu Pull Request.

## Padrões de Código
- Siga as regras do **Ruff** (configuradas no `pyproject.toml`).
- Use **Type Hints** em todos os novos métodos.
- Mantenha a separação entre Core e UI.

## Reportando Problemas
Use os templates de Issue no GitHub para relatar bugs ou sugerir novas funcionalidades.
