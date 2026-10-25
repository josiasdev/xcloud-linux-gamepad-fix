#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-1.0.0}"
ARCH="all"
PKG_NAME="xcloud-gamepad-fix"
BUILD_DIR="$(mktemp -d -t ${PKG_NAME}-deb-build.XXXXXX)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUTPUT_DIR="${REPO_ROOT}/dist"

cleanup() {
    rm -rf "${BUILD_DIR}"
}
trap cleanup EXIT

echo "=== Empacotando ${PKG_NAME} v${VERSION} (${ARCH}) ==="

PKG_ROOT="${BUILD_DIR}/${PKG_NAME}_${VERSION}_${ARCH}"
mkdir -p "${PKG_ROOT}/DEBIAN"
mkdir -p "${PKG_ROOT}/opt/xcloud-gamepad-fix"
mkdir -p "${PKG_ROOT}/usr/local/bin"
mkdir -p "${PKG_ROOT}/usr/share/applications"

# 1. Metadados de controle DEBIAN
cat <<EOF > "${PKG_ROOT}/DEBIAN/control"
Package: ${PKG_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: python3, python3-gi, python3-evdev, gir1.2-gtk-3.0, xboxdrv
Recommends: gir1.2-appindicator3-0.1
Maintainer: Josias <josias@users.noreply.github.com>
Description: XCloud Linux Gamepad Fixer and Mapper
 Fixes controller detection, button inversions, and triggers mapping
 for Xbox Cloud Gaming (xCloud) on Linux via xboxdrv and GTK 3 UI.
EOF

# 2. Scripts pós-instalação e pós-remoção
cat <<'EOF' > "${PKG_ROOT}/DEBIAN/postinst"
#!/bin/sh
set -e
update-desktop-database -q /usr/share/applications || true
echo "xcloud-gamepad-fix instalado com sucesso."
exit 0
EOF
chmod 755 "${PKG_ROOT}/DEBIAN/postinst"

cat <<'EOF' > "${PKG_ROOT}/DEBIAN/postrm"
#!/bin/sh
set -e
update-desktop-database -q /usr/share/applications || true
exit 0
EOF
chmod 755 "${PKG_ROOT}/DEBIAN/postrm"

# 3. Copiar código-fonte da aplicação
cp -r "${REPO_ROOT}/src" "${PKG_ROOT}/opt/xcloud-gamepad-fix/"
cp "${REPO_ROOT}/xcloud-gamepad.sh" "${PKG_ROOT}/opt/xcloud-gamepad-fix/"

# 4. Criar launcher executável
cat <<'EOF' > "${PKG_ROOT}/usr/local/bin/xcloud-gamepad-gui"
#!/bin/sh
exec python3 /opt/xcloud-gamepad-fix/src/main.py "$@"
EOF
chmod 755 "${PKG_ROOT}/usr/local/bin/xcloud-gamepad-gui"

# 5. Instalar arquivo de atalho (.desktop)
cat <<'EOF' > "${PKG_ROOT}/usr/share/applications/xcloud-gamepad-gui.desktop"
[Desktop Entry]
Name=XCloud Gamepad Fixer
Comment=Mapear e corrigir controles para Xbox Cloud Gaming no Linux
Exec=/usr/local/bin/xcloud-gamepad-gui
Icon=input-gaming
Terminal=false
Type=Application
Categories=Game;Utility;
Keywords=gamepad;xbox;xcloud;controller;
StartupNotify=true
EOF
chmod 644 "${PKG_ROOT}/usr/share/applications/xcloud-gamepad-gui.desktop"

# 6. Gerar pacote .deb
mkdir -p "${OUTPUT_DIR}"
DEB_FILE="${OUTPUT_DIR}/${PKG_NAME}_${VERSION}_${ARCH}.deb"

echo "Gerando pacote com dpkg-deb..."
dpkg-deb --build --root-owner-group "${PKG_ROOT}" "${DEB_FILE}"

echo "Pacote gerado com sucesso: ${DEB_FILE}"
ls -lh "${DEB_FILE}"
