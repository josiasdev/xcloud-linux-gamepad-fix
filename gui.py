#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

PROFILES = {
    "Sony DualShock 4 / DualSense (USB/Bluetooth)": [
        "--evdev-absmap", "ABS_X=x1,ABS_Y=y1,ABS_RX=x2,ABS_RY=y2,ABS_Z=lt,ABS_RZ=rt,ABS_HAT0X=dpad_x,ABS_HAT0Y=dpad_y",
        "--evdev-keymap", "BTN_SOUTH=a,BTN_EAST=b,BTN_WEST=x,BTN_NORTH=y,BTN_TL=lb,BTN_TR=rb,BTN_TL2=lt,BTN_TR2=rt,BTN_SELECT=back,BTN_START=start,BTN_MODE=guide,BTN_THUMBL=tl,BTN_THUMBR=tr",
        "--axismap", "-y1=y1,-y2=y2",
        "--mimic-xpad"
    ],
    "Genérico USB / Clone PS2 (Twin USB / DragonRise)": [
        "--evdev-absmap", "ABS_X=x1,ABS_Y=y1,ABS_RX=x2,ABS_RY=y2,ABS_RZ=rt,ABS_Z=lt,ABS_HAT0X=dpad_x,ABS_HAT0Y=dpad_y",
        "--evdev-keymap", "BTN_THUMB2=a,BTN_THUMB=b,BTN_TOP=x,BTN_TRIGGER=y,BTN_TOP2=lb,BTN_PINKIE=rb,BTN_BASE=lt,BTN_BASE2=rt,BTN_BASE3=back,BTN_BASE4=start,BTN_BASE5=tl,BTN_BASE6=tr,BTN_SOUTH=a,BTN_EAST=b,BTN_WEST=x,BTN_NORTH=y,BTN_TL=lb,BTN_TR=rb,BTN_SELECT=back,BTN_START=start,BTN_MODE=guide,BTN_THUMBL=tl,BTN_THUMBR=tr",
        "--axismap", "-y1=y1,-y2=y2",
        "--mimic-xpad"
    ],
    "Genérico Bluetooth (iPega / Android / D-Input)": [
        "--evdev-absmap", "ABS_X=x1,ABS_Y=y1,ABS_Z=x2,ABS_RZ=y2,ABS_BRAKE=lt,ABS_GAS=rt,ABS_HAT0X=dpad_x,ABS_HAT0Y=dpad_y",
        "--evdev-keymap", "BTN_A=a,BTN_B=b,BTN_X=x,BTN_Y=y,BTN_TL=lb,BTN_TR=rb,BTN_SELECT=back,BTN_START=start,BTN_MODE=guide,BTN_THUMBL=tl,BTN_THUMBR=tr",
        "--mimic-xpad"
    ]
}

def get_connected_controllers():
    controllers = []
    current = {}
    if not os.path.exists("/proc/bus/input/devices"):
        return controllers

    with open("/proc/bus/input/devices", "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("I:"):
                current = {}
            elif line.startswith("N: Name="):
                current["name"] = line.split('"')[1]
            elif line.startswith("H: Handlers="):
                handlers = line.split("=")[1].split()
                has_js = any(h.startswith("js") for h in handlers)
                ev = next((h for h in handlers if h.startswith("event")), None)
                if has_js and ev:
                    name = current.get("name", "")
                    if "Motion Sensors" not in name and "Touchpad" not in name:
                        current["event"] = f"/dev/input/{ev}"
                        controllers.append(current)
            elif not line:
                current = {}
    return controllers

class GamepadFixerWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="XCloud Gamepad Fixer")
        self.set_default_size(480, 320)
        self.set_border_width(12)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.process = None
        self.controllers = []

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(box)

        # Seletor de Controle
        box.pack_start(Gtk.Label(label="<b>Controle Conectado (USB ou Bluetooth):</b>", use_markup=True, xalign=0), False, False, 0)
        self.combo_device = Gtk.ComboBoxText()
        box.pack_start(self.combo_device, False, False, 0)

        # Seletor de Perfil
        box.pack_start(Gtk.Label(label="<b>Perfil de Mapeamento (Xbox 360):</b>", use_markup=True, xalign=0), False, False, 0)
        self.combo_profile = Gtk.ComboBoxText()
        for p in PROFILES.keys():
            self.combo_profile.append_text(p)
        self.combo_profile.set_active(0)
        box.pack_start(self.combo_profile, False, False, 0)

        # Botões de Ação
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.btn_refresh = Gtk.Button(label="Atualizar Lista")
        self.btn_refresh.connect("clicked", self.refresh_devices)
        btn_box.pack_start(self.btn_refresh, True, True, 0)

        self.btn_toggle = Gtk.Button(label="Iniciar Emulação")
        self.btn_toggle.connect("clicked", self.toggle_emulation)
        btn_box.pack_start(self.btn_toggle, True, True, 0)
        box.pack_start(btn_box, False, False, 0)

        # Status
        box.pack_start(Gtk.Label(label="<b>Status:</b>", use_markup=True, xalign=0), False, False, 0)
        self.lbl_status = Gtk.Label(label="Pronto para iniciar.", xalign=0)
        box.pack_start(self.lbl_status, False, False, 0)

        self.connect("destroy", self.on_close)
        self.refresh_devices()

    def refresh_devices(self, widget=None):
        self.combo_device.remove_all()
        self.controllers = get_connected_controllers()
        if not self.controllers:
            self.combo_device.append_text("Nenhum controle detectado")
            self.combo_device.set_active(0)
            self.btn_toggle.set_sensitive(False)
            self.lbl_status.set_text("Nenhum controle encontrado. Conecte um controle e clique em 'Atualizar Lista'.")
        else:
            for c in self.controllers:
                self.combo_device.append_text(f"{c['name']} ({c['event']})")
            self.combo_device.set_active(0)
            self.btn_toggle.set_sensitive(True)
            self.lbl_status.set_text(f"{len(self.controllers)} controle(s) detectado(s).")

    def toggle_emulation(self, widget):
        if self.process is None:
            idx = self.combo_device.get_active()
            if idx < 0 or idx >= len(self.controllers):
                return
            target_device = self.controllers[idx]["event"]
            profile_name = self.combo_profile.get_active_text()
            args = PROFILES[profile_name]

            # Prioriza pkexec se disponível para GUI limpa, ou sudo
            auth_cmd = ["pkexec"] if os.path.exists("/usr/bin/pkexec") else ["sudo"]
            cmd = auth_cmd + ["xboxdrv", "--evdev", target_device] + args + ["--silent"]

            try:
                self.process = subprocess.Popen(cmd)
                self.btn_toggle.set_label("Parar Emulação")
                self.btn_refresh.set_sensitive(False)
                self.combo_device.set_sensitive(False)
                self.combo_profile.set_sensitive(False)
                self.lbl_status.set_markup("<span foreground='green'><b>Ativo!</b> Controle emulado como Xbox 360 no XCloud.</span>")
            except Exception as e:
                self.lbl_status.set_text(f"Erro ao iniciar xboxdrv: {str(e)}")
        else:
            self.stop_emulation()

    def stop_emulation(self):
        if self.process:
            self.process.terminate()
            kill_cmd = ["pkexec", "killall", "xboxdrv"] if os.path.exists("/usr/bin/pkexec") else ["sudo", "killall", "xboxdrv"]
            subprocess.run(kill_cmd, stderr=subprocess.DEVNULL)
            self.process = None
        self.btn_toggle.set_label("Iniciar Emulação")
        self.btn_refresh.set_sensitive(True)
        self.combo_device.set_sensitive(True)
        self.combo_profile.set_sensitive(True)
        self.lbl_status.set_text("Emulação parada.")

    def on_close(self, widget):
        self.stop_emulation()
        Gtk.main_quit()

if __name__ == "__main__":
    win = GamepadFixerWindow()
    win.show_all()
    Gtk.main()
