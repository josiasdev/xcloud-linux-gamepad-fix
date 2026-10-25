# XCloud Linux Gamepad Fix

Solução completa com serviço em segundo plano e interface gráfica em GTK 3 para fazer controles USB e Bluetooth (Sony DualShock 4, DualSense e modelos genéricos) funcionarem mapeados como Xbox 360 no Xbox Cloud Gaming (XCloud) no Linux.

## O Problema

O XCloud acessado via navegador no Linux exige comandos no padrão XInput (Xbox 360). Muitos controles utilizam DirectInput ou drivers com eixos invertidos no kernel, causando falha no reconhecimento, botões trocados ou o analógico direito travado/pressionado continuamente.

## A Solução

O projeto utiliza o xboxdrv para criar um controle virtual de Xbox 360 compatível com o navegador. Conta com:
1. Regras do udev e serviço systemd para conexão automática via USB.
2. Interface gráfica em GTK 3 para seleção de perfis (Sony, Genérico USB, Genérico Bluetooth).
3. Mapeamento preciso de eixos analógicos e botões.

## Pré-requisitos

Instale os pacotes necessários no Linux Mint, Ubuntu ou Debian:

```bash
sudo apt update
sudo apt install xboxdrv python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

## Como Instalar

1. Clone o repositório:

```bash
git clone https://github.com/josiasdev/xcloud-linux-gamepad-fix.git
cd xcloud-linux-gamepad-fix
```

2. Dê permissão de execução aos scripts:

```bash
chmod +x install.sh uninstall.sh xcloud-gamepad.sh gui.py
```

3. Execute o instalador como administrador:

```bash
sudo ./install.sh
```

A instalação configura o serviço de conexão automática via udev/systemd, instala a interface gráfica no sistema e cria o atalho no menu de aplicativos.

## Como Usar

### Modo Interface Gráfica

Abra o menu de aplicativos e procure por XCloud Gamepad Fixer, ou execute no terminal:

```bash
xcloud-gamepad-gui
```

Ou diretamente na pasta do projeto:

```bash
./gui.py
```

Na interface:
1. Selecione o controle conectado na lista (USB ou Bluetooth).
2. Escolha o perfil correspondente (Sony DualShock, Genérico USB ou Bluetooth).
3. Clique em Iniciar Emulação.

### Modo Automático em Segundo Plano

Ao plugar o controle USB configurado na regra udev, o serviço systemd inicia a emulação silenciosamente sem necessidade de abrir janelas ou terminal.

### Modo Linha de Comando Manual

Para executar a emulação diretamente pelo terminal:

```bash
sudo ./xcloud-gamepad.sh
```

Pressione Ctrl + C no terminal quando desejar encerrar.

## Como Desinstalar

Para remover completamente as regras do udev, serviços do systemd, atalhos e executáveis instalados:

```bash
sudo ./uninstall.sh
```

## Licença

Este projeto está sob a licença MIT. Consulte o arquivo LICENSE para obter detalhes.
