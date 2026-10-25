"""Data classes for gamepad profiles and devices."""
from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class Profile:
    name: str
    absmap: str
    keymap: str
    axismap: str = "-y1=y1,-y2=y2"

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "absmap": self.absmap,
            "keymap": self.keymap,
            "axismap": self.axismap,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Profile":
        return cls(
            name=data["name"],
            absmap=data["absmap"],
            keymap=data["keymap"],
            axismap=data.get("axismap", "-y1=y1,-y2=y2"),
        )

    def to_xboxdrv_args(self) -> List[str]:
        args: List[str] = [
            "--evdev-absmap", self.absmap,
            "--evdev-keymap", self.keymap,
        ]
        if self.axismap:
            args += ["--axismap", self.axismap]
        args += ["--mimic-xpad", "--silent"]
        return args


@dataclass
class InputDevice:
    name: str
    event_path: str
    vendor_id: str = ""
    product_id: str = ""

    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.event_path})"

    @property
    def is_sony(self) -> bool:
        return self.vendor_id.lower() == "054c"


DEFAULT_PROFILES: List[Dict[str, str]] = [
    {
        "name": "Sony DualShock 4 / DualSense (USB/Bluetooth)",
        "absmap": "ABS_X=x1,ABS_Y=y1,ABS_RX=x2,ABS_RY=y2,ABS_Z=lt,ABS_RZ=rt,ABS_HAT0X=dpad_x,ABS_HAT0Y=dpad_y",
        "keymap": "BTN_SOUTH=a,BTN_EAST=b,BTN_WEST=x,BTN_NORTH=y,BTN_TL=lb,BTN_TR=rb,BTN_TL2=lt,BTN_TR2=rt,BTN_SELECT=back,BTN_START=start,BTN_MODE=guide,BTN_THUMBL=tl,BTN_THUMBR=tr",
        "axismap": "-y1=y1,-y2=y2",
    },
    {
        "name": "Genérico USB / Clone PS2 (Twin USB / DragonRise)",
        "absmap": "ABS_X=x1,ABS_Y=y1,ABS_RX=x2,ABS_RY=y2,ABS_RZ=rt,ABS_Z=lt,ABS_HAT0X=dpad_x,ABS_HAT0Y=dpad_y",
        "keymap": "BTN_THUMB2=a,BTN_THUMB=b,BTN_TOP=x,BTN_TRIGGER=y,BTN_TOP2=lb,BTN_PINKIE=rb,BTN_BASE=lt,BTN_BASE2=rt,BTN_BASE3=back,BTN_BASE4=start,BTN_BASE5=tl,BTN_BASE6=tr,BTN_SOUTH=a,BTN_EAST=b,BTN_WEST=x,BTN_NORTH=y,BTN_TL=lb,BTN_TR=rb,BTN_SELECT=back,BTN_START=start,BTN_MODE=guide,BTN_THUMBL=tl,BTN_THUMBR=tr",
        "axismap": "-y1=y1,-y2=y2",
    },
    {
        "name": "Genérico Bluetooth (iPega / Android / D-Input)",
        "absmap": "ABS_X=x1,ABS_Y=y1,ABS_Z=x2,ABS_RZ=y2,ABS_BRAKE=lt,ABS_GAS=rt,ABS_HAT0X=dpad_x,ABS_HAT0Y=dpad_y",
        "keymap": "BTN_A=a,BTN_B=b,BTN_X=x,BTN_Y=y,BTN_TL=lb,BTN_TR=rb,BTN_SELECT=back,BTN_START=start,BTN_MODE=guide,BTN_THUMBL=tl,BTN_THUMBR=tr",
        "axismap": "-y1=y1,-y2=y2",
    },
]
