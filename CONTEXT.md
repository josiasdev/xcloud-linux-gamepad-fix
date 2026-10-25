# Contexto do Projeto: xcloud-linux-gamepad-fix

## Visao Geral
O projeto xcloud-linux-gamepad-fix e uma solucao para Linux desenvolvida para corrigir problemas comuns de compatibilidade, inversao de eixos analogicos e mapeamento de botoes em controles genericos, DualShock 4 e outros joysticks utilizados no Xbox Cloud Gaming (xCloud) atraves de navegadores ou clientes web. A solucao utiliza o xboxdrv para emular um controle oficial de Xbox 360 no nivel do kernel/uinput.

## Arquitetura do Software
O projeto foi refatorado utilizando principios SOLID e Clean Architecture, separando completamente as camadas de dominio, dados, servicos de sistema e interface grafica.

Estrutura de diretorios:

src/
  __init__.py
  main.py: Ponto de entrada da aplicacao GTK 3.
  models/
    profile.py: Dataclasses de Profile (regras de mapeamento do xboxdrv) e InputDevice (metadados de hardware).
  config/
    profile_repository.py: Persistencia em ~/.config/xcloud-gamepad/profiles.json com tratamento de erro e criacao automatica de perfis padrao.
  core/
    emulation.py: Gerenciamento do ciclo de vida do processo xboxdrv via subprocess, pkexec ou sudo.
    hardware.py: Identificacao de joysticks conectados via leitura de /proc/bus/input/devices com filtro de nos de ruido (Touchpad e Motion Sensors).
    monitor.py: Leitor em segundo plano baseado em evdev para captura de eventos crus de botoes e eixos sem bloquear a thread da interface.
    logger.py: Sistema centralizado de logs com gravacao rotativa em ~/.local/state/xcloud-gamepad/app.log (10 MB com ate 3 backups).
  ui/
    main_window.py: Janela principal com navegacao em abas (Emulacao, Perfis e Testes) e integracao com a bandeja.
    profile_editor.py: Dialogo para criacao e edicao de perfis de mapeamento com campos de texto validados.
    profiles_tab.py: Aba para gerenciar, adicionar, editar e excluir perfis salvos.
    test_tab.py: Aba para visualizacao e teste dinamico de entradas em tempo real.
    tray.py: Integracao com a bandeja do sistema (System Tray) via AppIndicator3 com fallback para Gtk.StatusIcon. O fechamento da janela minimiza o app para segundo plano mantendo a sessao do jogo ativa.

packaging/
  build_deb.sh: Script de empacotamento Debian/Ubuntu/Linux Mint com criacao de estrutura DEBIAN/control, scripts de postinst/postrm e geracao via dpkg-deb.
  PKGBUILD: Especificacao de pacote nativo para Arch Linux, Manjaro e CachyOS no padrao do AUR.

.github/workflows/
  release.yml: Pipeline de CI/CD para analise estatica de codigo com flake8, execucao da suite de testes com pytest e build/publicacao automatica de releases com o pacote .deb anexado quando tags de versao sao enviadas.

tests/
  __init__.py
  test_core.py: Suite de testes unitarios cobrindo persistencia JSON, geracao de parametros de linha de comando, recuperacao de arquivos corrompidos e parsing de hardware.

## Tecnologias e Dependencias
Linguagem: Python 3.10+
Interface Grafica: GTK 3 via PyGObject (python3-gi, gir1.2-gtk-3.0)
Bandeja do Sistema: gir1.2-appindicator3-0.1 (com fallback para Gtk.StatusIcon)
Captura de Eventos: python3-evdev
Backend de Emulação: xboxdrv
Testes Automatizados: pytest
Empacotamento: dpkg-deb e pacman/makepkg
Governança e Qualidade: pre-commit, ruff, mypy, commitizen (Conventional Commits)


## Comandos Principais
Executar a interface grafica localmente:
python3 src/main.py

Rodar os testes automatizados:
pytest

Gerar o pacote .deb manualmente:
./packaging/build_deb.sh 1.0.0

Instalacao tradicional no sistema via script bash:
sudo ./install.sh
