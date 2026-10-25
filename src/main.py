#!/usr/bin/env python3
"""Entry point for XCloud Gamepad Fixer GUI."""
import sys
import os

# Ensure src/ siblings are importable when run directly from project root.
_BASE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_BASE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from src.ui.main_window import MainWindow


def main() -> None:
    win = MainWindow()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
