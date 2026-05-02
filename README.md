# XCloud Linux Gamepad Fix

Script em Bash para fazer controles USB genéricos funcionarem no Xbox Cloud Gaming (XCloud) no Linux.

## O Problema
O XCloud acessado pelo navegador no Linux espera receber comandos no padrão XInput. Controles genéricos usam DirectInput, o que causa falha no reconhecimento ou inversão de eixos e botões.

## A Solução
O script automatiza o xboxdrv. Ele varre o arquivo de dispositivos de entrada do kernel, detecta automaticamente o primeiro controle conectado, corrige a inversão matemática dos analógicos e mapeia os botões para emular um controle de Xbox 360.

## Pré-requisitos
Instale o xboxdrv no seu sistema:
```bash
sudo apt update
sudo apt install xboxdrv
```

## Como usar
1. Clone o repositório:
```bash
git clone https://github.com/SEU-USUARIO/xcloud-linux-gamepad-fix.git
cd xcloud-linux-gamepad-fix
```

3. Dê permissão de execução:
```bash
chmod +x xcloud-gamepad.sh
```

4. Conecte o controle e execute:
```bash
./xcloud-gamepad.sh
```

O script pedirá a senha de administrador (sudo) para ler os eventos do kernel. Mantenha o terminal aberto enquanto joga. Pressione Ctrl + C para encerrar.
