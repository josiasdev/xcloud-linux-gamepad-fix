#!/bin/bash
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if ! command -v xboxdrv &> /dev/null; then
    echo -e "${RED}[ ERRO ]${NC} A dependência 'xboxdrv' não foi encontrada."
    exit 1
fi


if [ "$EUID" -ne 0 ]; then
    SUDO="sudo"
else
    SUDO=""
fi


sleep 1

while IFS= read -r line; do
    if [[ "$line" == I:*Vendor=*Product=* ]]; then
        VENDOR_ID=$(echo "$line" | grep -oP 'Vendor=\K[0-9a-fA-F]{4}')
        PRODUCT_ID=$(echo "$line" | grep -oP 'Product=\K[0-9a-fA-F]{4}')
    elif [[ "$line" == N:* ]]; then
        CONTROLLER_NAME=$(echo "$line" | cut -d'"' -f2)
    elif [[ "$line" == H:*Handlers=*js*event* || "$line" == H:*Handlers=*event*js* ]]; then
        EVENT_NUM=$(echo "$line" | grep -oP 'event[0-9]+')
        break
    elif [[ -z "$line" ]]; then
        VENDOR_ID=""
        PRODUCT_ID=""
        CONTROLLER_NAME=""
        EVENT_NUM=""
    fi
done < /proc/bus/input/devices

if [ -z "$EVENT_NUM" ]; then
    echo -e "${RED}[ ERRO ]${NC} Nenhum controle detectado."
    exit 1
fi

EVENT_PATH="/dev/input/$EVENT_NUM"

echo -e "${BLUE}[ INFO ]${NC} Controle detectado: ${CONTROLLER_NAME} (ID ${VENDOR_ID}:${PRODUCT_ID})"
echo -e "${GREEN}[ OK ]${NC} Caminho: $EVENT_PATH"


$SUDO killall xboxdrv 2>/dev/null || true

$SUDO xboxdrv \
  --evdev "$EVENT_PATH" \
  --evdev-absmap ABS_X=x1,ABS_Y=y1,ABS_RZ=x2,ABS_Z=y2,ABS_HAT0X=dpad_x,ABS_HAT0Y=dpad_y \
  --evdev-keymap BTN_THUMB2=a,BTN_THUMB=b,BTN_TOP=x,BTN_TRIGGER=y,BTN_TOP2=lb,BTN_PINKIE=rb,BTN_BASE=lt,BTN_BASE2=rt,BTN_BASE3=back,BTN_BASE4=start,BTN_BASE5=tl,BTN_BASE6=tr \
  --axismap -y1=y1,-y2=y2 \
  --mimic-xpad \
  --silent
