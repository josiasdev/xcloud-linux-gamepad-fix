"""Profile manager tab – lists profiles and allows add / edit / delete."""

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from src.config.profile_repository import ProfileRepository
from src.models.profile import Profile
from src.ui.profile_editor import ProfileEditorDialog


class ProfilesTab(Gtk.Box):
    """VBox containing the profile list and CRUD toolbar."""

    def __init__(self, repo: ProfileRepository) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_border_width(10)
        self._repo = repo

        # ── Toolbar ───────────────────────────────────────────────────
        toolbar = Gtk.Box(spacing=6)
        self.pack_start(toolbar, False, False, 0)

        btn_add = Gtk.Button(label="Adicionar")
        btn_add.connect("clicked", self._on_add)
        toolbar.pack_start(btn_add, False, False, 0)

        btn_edit = Gtk.Button(label="Editar")
        btn_edit.connect("clicked", self._on_edit)
        toolbar.pack_start(btn_edit, False, False, 0)

        btn_del = Gtk.Button(label="Remover")
        btn_del.connect("clicked", self._on_delete)
        toolbar.pack_start(btn_del, False, False, 0)

        # ── List store & TreeView ─────────────────────────────────────
        self._store = Gtk.ListStore(str, str, str, str)  # name, absmap, keymap, axismap
        self._tree = Gtk.TreeView(model=self._store)

        for idx, title in enumerate(["Nome", "Axes (absmap)", "Botões (keymap)", "Inversão"]):
            col = Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=idx)
            col.set_resizable(True)
            col.set_min_width(80)
            self._tree.append_column(col)

        sw = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        sw.add(self._tree)
        self.pack_start(sw, True, True, 0)

        self._refresh()

    # ------------------------------------------------------------------
    # Public helper – return currently selected Profile (or None)
    # ------------------------------------------------------------------

    def selected_profile(self) -> Profile | None:
        model, it = self._tree.get_selection().get_selected()
        if it is None:
            return None
        row = model[it]
        return Profile(name=row[0], absmap=row[1], keymap=row[2], axismap=row[3])

    def selected_index(self) -> int | None:
        model, it = self._tree.get_selection().get_selected()
        if it is None:
            return None
        path = model.get_path(it)
        return path.get_indices()[0]

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_add(self, _btn: Gtk.Button) -> None:
        parent = self.get_toplevel()
        dlg = ProfileEditorDialog(parent, profile=None)
        if dlg.run() == Gtk.ResponseType.OK:
            profile = dlg.get_profile()
            if profile.name:
                self._repo.add(profile)
                self._refresh()
        dlg.destroy()

    def _on_edit(self, _btn: Gtk.Button) -> None:
        idx = self.selected_index()
        if idx is None:
            return
        profile = self.selected_profile()
        parent = self.get_toplevel()
        dlg = ProfileEditorDialog(parent, profile=profile)
        if dlg.run() == Gtk.ResponseType.OK:
            updated = dlg.get_profile()
            if updated.name:
                self._repo.update(idx, updated)
                self._refresh()
        dlg.destroy()

    def _on_delete(self, _btn: Gtk.Button) -> None:
        idx = self.selected_index()
        if idx is None:
            return
        parent = self.get_toplevel()
        confirm = Gtk.MessageDialog(
            transient_for=parent,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Remover este perfil?",
        )
        if confirm.run() == Gtk.ResponseType.YES:
            self._repo.remove(idx)
            self._refresh()
        confirm.destroy()

    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        self._store.clear()
        for p in self._repo.all():
            self._store.append([p.name, p.absmap, p.keymap, p.axismap])
