# XCloud Linux Gamepad Fix

[![CI](https://github.com/josiasdev/xcloud-linux-gamepad-fix/actions/workflows/release.yml/badge.svg)](https://github.com/josiasdev/xcloud-linux-gamepad-fix/actions/workflows/release.yml)
[![Version](https://img.shields.io/github/v/release/josiasdev/xcloud-linux-gamepad-fix)](https://github.com/josiasdev/xcloud-linux-gamepad-fix/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

Uma solução robusta para mapeamento de controles (Sony DualShock 4, DualSense, Genéricos) no **Xbox Cloud Gaming** para Linux, garantindo reconhecimento via padrão XInput (Xbox 360).

## Por que este projeto?
O XCloud acessado via navegador no Linux exige comandos no padrão XInput. Muitos controles utilizam DirectInput ou drivers com eixos invertidos, causando falha no reconhecimento, botões trocados ou analógicos travados. Este projeto resolve isso emulando um controle de Xbox 360 no nível do kernel (via `xboxdrv` e `uinput`).

## Arquitetura e Tecnologias
- **Backend**: `xboxdrv` para emulação real de hardware.
- **Core**: Arquitetura SOLID, persistência JSON (`~/.config/xcloud-gamepad/profiles.json`) e monitoramento de eventos `evdev` em thread separada.
- **UI**: Interface GTK 3 (PyGObject) com bandeja do sistema transparente (AppIndicator).
- **Concorrência**: GLib idle callbacks para garantir a responsividade da UI enquanto o backend roda.

## Instalação

### Debian / Ubuntu / Linux Mint
Baixe o arquivo `.deb` mais recente na página de [Releases](https://github.com/josiasdev/xcloud-linux-gamepad-fix/releases) e instale:
```bash
sudo apt install ./xcloud-gamepad-fix_1.0.0_all.deb
```

### Arch Linux / CachyOS (AUR)
```bash
yay -S xcloud-gamepad-fix
```

## Desenvolvimento

Requisitos: `make`, `python3`.

```bash
make install-deps
make run      # Executa a aplicação
make lint     # Ruff + Mypy
make test     # Pytest
```
