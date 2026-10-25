## 🚀 Descrição das Mudanças
<!-- Explique o que foi alterado nesta PR -->

## 🔗 Issue Relacionada
Fixes # (obrigatório: o número da Issue correspondente)

## ✅ Checklist de Governança
- [ ] A branch segue o padrão de nomeação (`feature/`, `bugfix/`, `hotfix/`).
- [ ] Os commits seguem o padrão *Conventional Commits* (`feat:`, `fix:`, `refactor:`, etc).
- [ ] A arquitetura foi respeitada (separação clara entre `src/ui` e `src/core`).
- [ ] Nenhuma operação bloqueante foi adicionada ao Main Loop do GTK (uso de Threads/`GLib.idle_add` implementado).
- [ ] Tipagem estática (`Type Hints`) foi adicionada ou atualizada em todo o código.
- [ ] Testes foram adicionados ou atualizados e a suíte completa (`make test`) está passando.
- [ ] Executei `make lint` e não há erros de Ruff/Mypy.
