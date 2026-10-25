# Contexto Arquitetural para IAs (AGENTS.md)

## Visão Geral
Este é um projeto de correção de Gamepad para Linux que utiliza `xboxdrv` (backend de emulação) e `evdev` (captura de entrada), gerenciado por uma interface gráfica GTK 3 (PyGObject).

## Regras Arquiteturais
- **SOLID & Clean Arch:** Mantenha a separação rígida:
  - `src/ui/`: Apenas componentes GTK, layouts e gerenciamento de sinais.
  - `src/core/`: Lógica de negócio, subprocessos (`xboxdrv`), parsing de `/proc/bus/input/devices` e monitoramento `evdev`.
  - `src/models/`: Estruturas de dados (`dataclasses`).
  - `src/config/`: Persistência de dados (JSON).
- **Concorrência (Crítico):** **Nunca** bloqueie o Main Loop do GTK.
  - Leituras de hardware (`evdev`) devem ser feitas em threads separadas.
  - Atualizações da UI a partir de threads devem ser feitas estritamente via `GLib.idle_add()`.
- **Qualidade de Código:**
  - Todo novo código deve incluir **Type Hints** (`typing`).
  - Todo novo código funcional deve vir acompanhado de testes unitários em `tests/`.
  - O código deve passar em `make lint` (Ruff + Mypy).
