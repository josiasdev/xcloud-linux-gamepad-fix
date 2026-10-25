"""Input test tab – shows live axis/button state from evdev via a background thread."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from src.core.monitor import EventMonitor
from src.models.profile import InputDevice

try:
    import evdev
    _EVDEV_AVAIL = True
except ImportError:
    _EVDEV_AVAIL = False

# Human-readable axis names (evdev codes)
_ABS_NAMES = {
    0: "Analógico Esq. X (ABS_X)",
    1: "Analógico Esq. Y (ABS_Y)",
    2: "Gatilho L2 (ABS_Z)",
    3: "Analógico Dir. X (ABS_RX)",
    4: "Analógico Dir. Y (ABS_RY)",
    5: "Gatilho R2 (ABS_RZ)",
    16: "D-Pad X (HAT0X)",
    17: "D-Pad Y (HAT0Y)",
}


class TestTab(Gtk.Box):
    """GTK widget (a VBox) that displays live controller input state."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_border_width(10)
        self._monitor: EventMonitor | None = None

        # -- Status label ------------------------------------------------
        self._status_lbl = Gtk.Label(
            label="Selecione um controle na aba principal e clique em 'Iniciar Teste'.",
            xalign=0,
            wrap=True,
        )
        self.pack_start(self._status_lbl, False, False, 0)

        # -- Start / Stop button ----------------------------------------
        self._toggle_btn = Gtk.Button(label="Iniciar Teste")
        self._toggle_btn.connect("clicked", self._on_toggle)
        self.pack_start(self._toggle_btn, False, False, 0)

        # -- Axes section -----------------------------------------------
        sep = Gtk.Separator()
        self.pack_start(sep, False, False, 4)
        self.pack_start(Gtk.Label(label="<b>Eixos</b>", use_markup=True, xalign=0), False, False, 0)

        self._axis_bars: dict[int, Gtk.ProgressBar] = {}
        axes_grid = Gtk.Grid(row_spacing=4, column_spacing=8)
        self.pack_start(axes_grid, False, False, 0)

        for row, (code, label) in enumerate(_ABS_NAMES.items()):
            axes_grid.attach(Gtk.Label(label=label, xalign=1), 0, row, 1, 1)
            bar = Gtk.ProgressBar(hexpand=True)
            bar.set_fraction(0.5)
            axes_grid.attach(bar, 1, row, 1, 1)
            val_lbl = Gtk.Label(label="128", width_chars=6, xalign=0)
            axes_grid.attach(val_lbl, 2, row, 1, 1)
            self._axis_bars[code] = (bar, val_lbl)

        # -- Buttons section --------------------------------------------
        sep2 = Gtk.Separator()
        self.pack_start(sep2, False, False, 4)
        self.pack_start(Gtk.Label(label="<b>Botões</b>", use_markup=True, xalign=0), False, False, 0)

        self._btn_labels: dict[int, Gtk.Label] = {}
        btn_flow = Gtk.FlowBox(max_children_per_line=6, selection_mode=Gtk.SelectionMode.NONE)
        self.pack_start(btn_flow, False, False, 0)

        if _EVDEV_AVAIL:
            for code, name in evdev.ecodes.BTN.items():
                lbl = Gtk.Label(label=name if isinstance(name, str) else str(code))
                lbl.set_name("btn-off")
                lbl.set_margin_start(3)
                lbl.set_margin_end(3)
                lbl.set_margin_top(2)
                lbl.set_margin_bottom(2)
                btn_flow.add(lbl)
                self._btn_labels[code] = lbl

        # CSS for button highlight
        css = Gtk.CssProvider()
        css.load_from_data(b"""
            label#btn-on  { background: #2ecc71; color: #fff; border-radius: 4px; padding: 2px 4px; }
            label#btn-off { background: #444;     color: #aaa; border-radius: 4px; padding: 2px 4px; }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen() if self.get_screen() else self.get_display().get_default_screen(),
            css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self._device: InputDevice | None = None

    # ------------------------------------------------------------------
    # Public API called by MainWindow
    # ------------------------------------------------------------------

    def set_device(self, device: InputDevice | None) -> None:
        self._device = device

    def cleanup(self) -> None:
        self._stop_monitor()

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_toggle(self, _btn):
        if self._monitor is not None:
            self._stop_monitor()
        else:
            self._start_monitor()

    def _start_monitor(self):
        if not self._device:
            self._status_lbl.set_text("Nenhum controle selecionado.")
            return
        if not _EVDEV_AVAIL:
            self._status_lbl.set_text("Erro: python-evdev não está instalado.")
            return

        self._monitor = EventMonitor(self._device.event_path)
        self._monitor.on_axis   = lambda c, v: GLib.idle_add(self._update_axis, c, v)
        self._monitor.on_button = lambda c, v: GLib.idle_add(self._update_button, c, v)

        try:
            self._monitor.start()
            self._toggle_btn.set_label("Parar Teste")
            self._status_lbl.set_markup(
                f"<span foreground='green'><b>Capturando</b></span>  {self._device.name}"
            )
        except Exception as e:
            self._monitor = None
            self._status_lbl.set_text(f"Erro ao iniciar captura: {e}")

    def _stop_monitor(self):
        if self._monitor:
            self._monitor.stop()
            self._monitor = None
        self._toggle_btn.set_label("Iniciar Teste")
        self._status_lbl.set_text("Captura encerrada.")

    # ------------------------------------------------------------------
    # UI update methods (called via GLib.idle_add – runs on GTK thread)
    # ------------------------------------------------------------------

    def _update_axis(self, code: int, value: int) -> bool:
        if code in self._axis_bars:
            bar, lbl = self._axis_bars[code]
            fraction = (value + 32768) / 65535  # normalise to 0–1
            # For small-range axes (HAT, triggers 0-255)
            try:
                import evdev
                info = evdev.InputDevice(self._device.event_path).absinfo(code)
                span = info.max - info.min
                if span > 0:
                    fraction = (value - info.min) / span
            except Exception:
                pass
            bar.set_fraction(max(0.0, min(1.0, fraction)))
            lbl.set_text(str(value))
        return False  # do not repeat

    def _update_button(self, code: int, pressed: bool) -> bool:
        if code in self._btn_labels:
            lbl = self._btn_labels[code]
            lbl.set_name("btn-on" if pressed else "btn-off")
        return False
