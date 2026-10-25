"""System Tray / AppIndicator integration.

Tries AppIndicator3 first (Ubuntu/Mint with gir1.2-appindicator3-0.1).
Falls back to Gtk.StatusIcon (deprecated but universally available on GTK 3).

Usage::

    tray = TrayIcon(
        on_show=win.present,
        on_quit=Gtk.main_quit,
        get_running=emulation.is_running,
        on_toggle_emulation=...,
    )
"""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from src.core.logger import get_logger

log = get_logger(__name__)

_INDICATOR_AVAILABLE = False
try:
    gi.require_version("AppIndicator3", "0.1")
    from gi.repository import AppIndicator3
    _INDICATOR_AVAILABLE = True
except (ValueError, ImportError):
    pass


class TrayIcon:
    """Unified tray icon abstraction (AppIndicator3 or StatusIcon)."""

    def __init__(
        self,
        on_show,
        on_quit,
        get_running,
        on_toggle_emulation,
    ):
        self._on_show            = on_show
        self._on_quit            = on_quit
        self._get_running        = get_running
        self._on_toggle_emulation = on_toggle_emulation

        self._menu = self._build_menu()

        if _INDICATOR_AVAILABLE:
            log.info("Tray: using AppIndicator3")
            self._impl = AppIndicator3.Indicator.new(
                "xcloud-gamepad-fixer",
                "input-gaming",
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
            )
            self._impl.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self._impl.set_menu(self._menu)
        else:
            log.info("Tray: using Gtk.StatusIcon (fallback)")
            self._impl = Gtk.StatusIcon()
            self._impl.set_from_icon_name("input-gaming")
            self._impl.set_tooltip_text("XCloud Gamepad Fixer")
            self._impl.connect("activate", lambda _: self._on_show())
            self._impl.connect("popup-menu", self._on_status_icon_popup)

    # ------------------------------------------------------------------

    def update_emulation_item(self) -> None:
        """Refresh the emulation toggle label based on current state."""
        running = self._get_running()
        self._emulation_item.set_label(
            "Parar Emulação" if running else "Iniciar Emulação"
        )

    # ------------------------------------------------------------------

    def _build_menu(self) -> Gtk.Menu:
        menu = Gtk.Menu()

        item_open = Gtk.MenuItem(label="Abrir Configurações")
        item_open.connect("activate", lambda _: self._on_show())
        menu.append(item_open)

        menu.append(Gtk.SeparatorMenuItem())

        self._emulation_item = Gtk.MenuItem(label="Iniciar Emulação")
        self._emulation_item.connect("activate", self._toggle_emulation)
        menu.append(self._emulation_item)

        menu.append(Gtk.SeparatorMenuItem())

        item_quit = Gtk.MenuItem(label="Sair")
        item_quit.connect("activate", lambda _: self._on_quit())
        menu.append(item_quit)

        menu.show_all()
        return menu

    def _toggle_emulation(self, _item) -> None:
        self._on_toggle_emulation()
        self.update_emulation_item()

    def _on_status_icon_popup(self, _icon, button, time) -> None:
        self._menu.popup(None, None, Gtk.StatusIcon.position_menu, self._impl, button, time)
