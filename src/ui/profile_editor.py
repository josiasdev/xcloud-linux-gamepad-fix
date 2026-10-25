"""Profile editor dialog – create or edit a Profile with GTK form fields."""

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from src.models.profile import Profile


class ProfileEditorDialog(Gtk.Dialog):
    """Modal dialog for creating/editing a mapping profile.

    Usage::

        dlg = ProfileEditorDialog(parent, profile)  # profile=None → new
        if dlg.run() == Gtk.ResponseType.OK:
            new_profile = dlg.get_profile()
        dlg.destroy()
    """

    def __init__(self, parent: Gtk.Window, profile: Profile = None):
        super().__init__(
            title="Editar Perfil" if profile else "Novo Perfil",
            transient_for=parent,
            modal=True,
        )
        self.set_default_size(520, 320)
        self.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK,
            Gtk.ResponseType.OK,
        )

        box = self.get_content_area()
        box.set_spacing(6)
        box.set_border_width(12)

        grid = Gtk.Grid(column_spacing=10, row_spacing=8)
        box.pack_start(grid, True, True, 0)

        # Name
        grid.attach(Gtk.Label(label="Nome:", xalign=1), 0, 0, 1, 1)
        self._name_entry = Gtk.Entry(hexpand=True, text=profile.name if profile else "")
        grid.attach(self._name_entry, 1, 0, 1, 1)

        # Absmap
        grid.attach(Gtk.Label(label="Axes (--evdev-absmap):", xalign=1), 0, 1, 1, 1)
        self._absmap_entry = Gtk.Entry(hexpand=True, text=profile.absmap if profile else "")
        grid.attach(self._absmap_entry, 1, 1, 1, 1)

        # Keymap
        grid.attach(Gtk.Label(label="Botões (--evdev-keymap):", xalign=1), 0, 2, 1, 1)
        self._keymap_entry = Gtk.Entry(hexpand=True, text=profile.keymap if profile else "")
        grid.attach(self._keymap_entry, 1, 2, 1, 1)

        # Axismap
        grid.attach(Gtk.Label(label="Inversão (--axismap):", xalign=1), 0, 3, 1, 1)
        self._axismap_entry = Gtk.Entry(
            hexpand=True,
            text=profile.axismap if profile else "-y1=y1,-y2=y2",
        )
        grid.attach(self._axismap_entry, 1, 3, 1, 1)

        # Help note
        note = Gtk.Label(
            label="<small>Exemplo:  ABS_X=x1,ABS_Y=y1,ABS_RX=x2,ABS_RY=y2,ABS_Z=lt,ABS_RZ=rt</small>",
            use_markup=True,
            wrap=True,
            xalign=0,
        )
        box.pack_start(note, False, False, 0)

        self.show_all()

    def get_profile(self) -> Profile:
        return Profile(
            name=self._name_entry.get_text().strip(),
            absmap=self._absmap_entry.get_text().strip(),
            keymap=self._keymap_entry.get_text().strip(),
            axismap=self._axismap_entry.get_text().strip(),
        )
