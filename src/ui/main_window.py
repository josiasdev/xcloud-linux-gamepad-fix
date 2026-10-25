"""Main application window with three tabs: Emulation, Profiles, Test."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk
from typing import Optional, List, Any

from src.config.profile_repository import ProfileRepository
from src.core.emulation import EmulationService
from src.core.hardware import list_controllers
from src.core.logger import get_logger
from src.models.profile import InputDevice, Profile
from src.ui.profiles_tab import ProfilesTab
from src.ui.test_tab import TestTab
from src.ui.tray import TrayIcon

log = get_logger(__name__)


class MainWindow(Gtk.Window):

    def __init__(self) -> None:
        super().__init__(title="XCloud Gamepad Fixer")
        self.set_default_size(640, 460)
        self.set_resizable(True)  # Permitir redimensionamento
        self.set_border_width(0)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Intercept delete-event to hide-to-tray instead of quitting
        self.connect("delete-event", self._on_delete_event)

        # ── Services ──────────────────────────────────────────────────
        self._repo      = ProfileRepository()
        self._emulation = EmulationService()
        self._devices: List[InputDevice] = []
        
        # Iniciar monitoramento de estado do daemon
        GLib.timeout_add_seconds(2, self._check_emulation_daemon)

        # ── Notebook (tabs) ───────────────────────────────────────────
        notebook = Gtk.Notebook()
        self.add(notebook)

        # Tab 1: Emulação
        emul_box = self._build_emulation_tab()
        notebook.append_page(emul_box, Gtk.Label(label="Emulação"))

        # Tab 2: Perfis
        self._profiles_tab = ProfilesTab(self._repo)
        notebook.append_page(self._profiles_tab, Gtk.Label(label="Perfis"))

        # Tab 3: Teste
        self._test_tab = TestTab()
        notebook.append_page(self._test_tab, Gtk.Label(label="Testar Inputs"))

        # ── Tray icon (created after window so callbacks are ready) ───
        self._tray = TrayIcon(
            on_show=self._show_window,
            on_quit=self._quit,
            get_running=lambda: self._emulation.is_running,
            on_toggle_emulation=self._on_toggle_emulation,
        )

        self._refresh_devices()
        log.info("MainWindow initialised")

    # ==================================================================
    # Emulation tab builder
    # ==================================================================

    def _build_emulation_tab(self) -> Gtk.Box:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(12)

        box.pack_start(
            Gtk.Label(label="<b>Controle Conectado:</b>", use_markup=True, xalign=0),
            False, False, 0,
        )
        self._device_combo = Gtk.ComboBoxText()
        self._device_combo.connect("changed", self._on_device_changed)
        box.pack_start(self._device_combo, False, False, 0)

        box.pack_start(
            Gtk.Label(label="<b>Perfil de Mapeamento (Xbox 360):</b>", use_markup=True, xalign=0),
            False, False, 0,
        )
        self._profile_combo = Gtk.ComboBoxText()
        self._refresh_profile_combo()
        box.pack_start(self._profile_combo, False, False, 0)

        btn_row = Gtk.Box(spacing=8)
        self._refresh_btn = Gtk.Button(label="Atualizar Lista")
        self._refresh_btn.connect("clicked", lambda _: self._refresh_devices())
        btn_row.pack_start(self._refresh_btn, True, True, 0)

        self._toggle_btn = Gtk.Button(label="Iniciar Emulação")
        self._toggle_btn.connect("clicked", lambda _: self._on_toggle_emulation())
        btn_row.pack_start(self._toggle_btn, True, True, 0)
        box.pack_start(btn_row, False, False, 0)

        box.pack_start(
            Gtk.Label(label="<b>Status:</b>", use_markup=True, xalign=0),
            False, False, 0,
        )
        self._status_lbl = Gtk.Label(label="Pronto para iniciar.", xalign=0, wrap=True)
        box.pack_start(self._status_lbl, False, False, 0)

        # Log path hint
        from src.core.logger import _LOG_FILE
        hint = Gtk.Label(
            label=f"<small>Logs salvos em: {_LOG_FILE}</small>",
            use_markup=True,
            xalign=0,
        )
        box.pack_end(hint, False, False, 4)

        return box

    # ==================================================================
    # Device handling
    # ==================================================================

    def _refresh_devices(self) -> None:
        self._device_combo.remove_all()
        self._devices = list_controllers()
        log.debug("Detected %d controller(s)", len(self._devices))
        if not self._devices:
            self._device_combo.append_text("Nenhum controle detectado")
            self._device_combo.set_active(0)
            self._toggle_btn.set_sensitive(False)
            self._status_lbl.set_text("Conecte um controle e clique em 'Atualizar Lista'.")
        else:
            for d in self._devices:
                self._device_combo.append_text(d.display_name)
            self._device_combo.set_active(0)
            self._toggle_btn.set_sensitive(True)
            self._status_lbl.set_text(f"{len(self._devices)} controle(s) detectado(s).")
        self._on_device_changed(self._device_combo)
        self._refresh_profile_combo()

    def _on_device_changed(self, _combo: Gtk.ComboBoxText) -> None:
        self._test_tab.set_device(self._selected_device())

    def _selected_device(self) -> Optional[InputDevice]:
        idx = self._device_combo.get_active()
        if idx < 0 or idx >= len(self._devices):
            return None
        return self._devices[idx]

    # ==================================================================
    # Profile handling
    # ==================================================================

    def _refresh_profile_combo(self) -> None:
        self._profile_combo.remove_all()
        for p in self._repo.all():
            self._profile_combo.append_text(p.name)
        if self._profile_combo.get_model() and len(self._profile_combo.get_model()):
            self._profile_combo.set_active(0)

    def _selected_profile(self) -> Optional[Profile]:
        idx = self._profile_combo.get_active()
        profiles = self._repo.all()
        if idx < 0 or idx >= len(profiles):
            return None
        return profiles[idx]

    # ==================================================================
    # Emulation toggle
    # ==================================================================

    def _check_emulation_daemon(self) -> bool:
        if self._emulation.is_running is False and self._toggle_btn.get_label() == "Parar Emulação":
            self._stop_emulation()
            self._status_lbl.set_text("Erro: O processo de emulação encerrou inesperadamente.")
            self._tray.update_emulation_item()
        return True

    def _on_toggle_emulation(self) -> None:
        if self._emulation.is_running:
            self._stop_emulation()
        else:
            self._start_emulation()
        self._tray.update_emulation_item()

    def _start_emulation(self) -> None:
        device  = self._selected_device()
        profile = self._selected_profile()
        if not device or not profile:
            self._status_lbl.set_text("Selecione um controle e um perfil.")
            return
        try:
            self._emulation.start(device, profile)
            self._toggle_btn.set_label("Parar Emulação")
            self._refresh_btn.set_sensitive(False)
            self._device_combo.set_sensitive(False)
            self._profile_combo.set_sensitive(False)
            self._status_lbl.set_markup(
                "<span foreground='green'><b>Ativo!</b></span>  Controle emulado como Xbox 360."
            )
        except Exception as exc:
            log.error("Failed to start emulation: %s", exc)
            self._status_lbl.set_text(f"Erro: {exc}")

    def _stop_emulation(self) -> None:
        self._emulation.stop()
        self._toggle_btn.set_label("Iniciar Emulação")
        self._refresh_btn.set_sensitive(True)
        self._device_combo.set_sensitive(True)
        self._profile_combo.set_sensitive(True)
        self._status_lbl.set_text("Emulação encerrada.")

    # ==================================================================
    # Window / tray lifecycle
    # ==================================================================

    def _on_delete_event(self, _win: Gtk.Window, _event: Any) -> bool:
        """Hide to tray instead of destroying the window."""
        self.hide()
        log.info("Window hidden to tray")
        return True  # Prevent default destroy

    def _show_window(self) -> None:
        self.present()

    def _quit(self) -> None:
        log.info("Quitting application")
        self._emulation.stop()
        self._test_tab.cleanup()
        Gtk.main_quit()
