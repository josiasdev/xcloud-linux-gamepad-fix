#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
  echo "Por favor, execute o instalador como administrador: sudo ./install.sh"
  exit 1
fi

echo "Copiando script principal para /usr/local/bin..."
cp xcloud-gamepad.sh /usr/local/bin/xcloud-gamepad
chmod +x /usr/local/bin/xcloud-gamepad

echo "Configurando o serviço do systemd..."
cat <<EOF > /etc/systemd/system/xcloud-gamepad.service
[Unit]
Description=XCloud Generic Gamepad Fixer

[Service]
Type=simple
ExecStart=/usr/local/bin/xcloud-gamepad
Restart=no
EOF

echo "Configurando a regra do udev..."
cat <<EOF > /etc/udev/rules.d/99-xcloud-gamepad.rules
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0810", ATTR{idProduct}=="0001", TAG+="systemd", ENV{SYSTEMD_WANTS}="xcloud-gamepad.service"
EOF

echo "Recarregando daemons do sistema..."
systemctl daemon-reload
udevadm control --reload-rules
udevadm trigger

echo "Instalação concluída com sucesso!"
echo "A partir de agora, o script rodará automaticamente sempre que o controle for conectado."