#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
  echo "Por favor, execute o instalador como administrador: sudo ./install.sh"
  exit 1
fi

INSTALL_DIR="/opt/xcloud-gamepad-fix"

echo "Copiando aplicação para $INSTALL_DIR..."
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp -r src/ "$INSTALL_DIR/src"

echo "Copiando script de linha de comando para /usr/local/bin..."
cp xcloud-gamepad.sh /usr/local/bin/xcloud-gamepad
chmod +x /usr/local/bin/xcloud-gamepad

echo "Criando launcher executável para a interface gráfica..."
cat <<EOF > /usr/local/bin/xcloud-gamepad-gui
#!/bin/bash
exec python3 $INSTALL_DIR/src/main.py "\$@"
EOF
chmod +x /usr/local/bin/xcloud-gamepad-gui

echo "Instalando atalho no menu de aplicativos..."
cp xcloud-gamepad-gui.desktop /usr/share/applications/
chmod 644 /usr/share/applications/xcloud-gamepad-gui.desktop

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
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="054c", ATTR{idProduct}=="05c4", TAG+="systemd", ENV{SYSTEMD_WANTS}="xcloud-gamepad.service"
EOF

echo "Recarregando daemons do sistema..."
systemctl daemon-reload
udevadm control --reload-rules
udevadm trigger

echo ""
echo "Instalação concluída com sucesso!"
echo "Interface gráfica: xcloud-gamepad-gui"
echo "Linha de comando:  sudo xcloud-gamepad"
echo "A partir de agora, o serviço inicia automaticamente ao conectar o controle via USB."