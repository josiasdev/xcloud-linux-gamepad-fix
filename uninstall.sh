#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
  echo "Por favor, execute o desinstalador como administrador: sudo ./uninstall.sh"
  exit 1
fi

echo "Parando e removendo o servico do systemd..."
systemctl stop xcloud-gamepad.service 2>/dev/null || true
systemctl disable xcloud-gamepad.service 2>/dev/null || true
rm -f /etc/systemd/system/xcloud-gamepad.service

echo "Removendo a regra do udev..."
rm -f /etc/udev/rules.d/99-xcloud-gamepad.rules

echo "Removendo o executavel..."
rm -f /usr/local/bin/xcloud-gamepad

echo "Recarregando daemons do sistema..."
systemctl daemon-reload
udevadm control --reload-rules

echo "Desinstalacao concluida. O sistema voltou ao estado original."