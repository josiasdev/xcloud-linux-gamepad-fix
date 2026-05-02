# XCloud Linux Gamepad Fix

Script em Bash para fazer controles USB genéricos funcionarem perfeitamente no Xbox Cloud Gaming (XCloud) no Linux de forma automática.

## O Problema
O XCloud acessado pelo navegador no Linux espera receber comandos no padrão XInput. Controles genéricos utilizam o padrão DirectInput, o que causa falha no reconhecimento por parte do navegador, além de inversão matemática de eixos analógicos e botões trocados.

## A Solução
O projeto utiliza o `xboxdrv` para emular um controle de Xbox 360 em nível de sistema. Através de regras do `udev` e um serviço do `systemd`, o script varre o arquivo de dispositivos de entrada do kernel de forma dinâmica, corrige os eixos cruzados e faz o mapeamento do protocolo assim que o controle é conectado à porta USB, sem necessidade de abrir o terminal.

## Pré-requisitos
Instale a dependência de emulação no seu sistema base (Debian/Ubuntu/Linux Mint):
```bash
sudo apt update
sudo apt install xboxdrv
```

## Como Instalar (Modo Automático)
Esta é a maneira recomendada. O controle será configurado silenciosamente em segundo plano toda vez que for plugado.

1. Clone o repositório:
```bash
git clone https://github.com/SEU-USUARIO/xcloud-linux-gamepad-fix.git
cd xcloud-linux-gamepad-fix
```

3. Dê permissão aos scripts:
```bash
chmod +x install.sh
chmod +x uninstall.sh
chmod +x xcloud-gamepad.sh
```

4. Execute o instalador como root:
```bash
sudo ./install.sh
```

Após isso, basta conectar o controle e jogar. O serviço iniciará e encerrará automaticamente junto com o hardware.

## Como Desinstalar

Caso tenha utilizado a instalação automática e queira remover o projeto do sistema:

Execute o script de desinstalação como root:
```bash
sudo ./uninstall.sh
```

Isso removerá o serviço do systemd, a regra do udev e o executável local, limpando completamente as alterações feitas no sistema operacional.

## Como Usar (Modo Manual)
Caso não queira criar um serviço no sistema e prefira rodar apenas quando for jogar:
1. Dê permissão de execução:
```bash
chmod +x xcloud-gamepad.sh
```

2. Conecte o controle e execute:
```bash
./xcloud-gamepad.sh
```

Mantenha o terminal aberto enquanto joga. Pressione Ctrl + C para encerrar a emulação.

## Licença

Este projeto está sob a licença MIT. Consulte o arquivo LICENSE para obter os termos detalhados.

