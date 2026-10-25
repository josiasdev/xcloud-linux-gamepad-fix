"""Hardware detection – scans /proc/bus/input/devices for joystick devices."""

import os
import re

from src.core.logger import get_logger
from src.models.profile import InputDevice

log = get_logger(__name__)

_PROC_DEVICES = "/proc/bus/input/devices"
_IGNORED_SUFFIXES = ("Motion Sensors", "Touchpad")


def list_controllers() -> list[InputDevice]:
    """Return all joystick-capable input devices, excluding noise nodes."""
    if not os.path.exists(_PROC_DEVICES):
        return []

    devices: list[InputDevice] = []
    current: dict[str, str] = {}
    log.debug("Scanning %s for joystick devices", _PROC_DEVICES)

    with open(_PROC_DEVICES) as f:
        for raw in f:
            line = raw.strip()

            if line.startswith("I:"):
                current = {
                    "vendor": _parse_field(line, "Vendor"),
                    "product": _parse_field(line, "Product"),
                }
            elif line.startswith("N: Name="):
                current["name"] = line.split('"')[1]
            elif line.startswith("H: Handlers="):
                handlers = line.split("=")[1].split()
                has_js = any(h.startswith("js") for h in handlers)
                ev = next((h for h in handlers if h.startswith("event")), None)
                name = current.get("name")
                if name and has_js and ev and not any(name.endswith(s) for s in _IGNORED_SUFFIXES):
                    devices.append(
                        InputDevice(
                            name=name,
                            event_path=f"/dev/input/{ev}",
                            vendor_id=current.get("vendor", ""),
                            product_id=current.get("product", ""),
                        )
                    )
                elif has_js and ev:
                    log.warning("Skipping device with unexpected format: %s", name)
            elif not line:
                current = {}

    return devices


def _parse_field(line: str, field: str) -> str:
    m = re.search(rf"{field}=([0-9a-fA-F]{{4}})", line)
    return m.group(1) if m else ""
