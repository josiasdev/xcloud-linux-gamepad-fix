"""Centralised logging configuration for XCloud Gamepad Fixer.

All modules should obtain their loggers via::

    from src.core.logger import get_logger
    log = get_logger(__name__)

Logs are written to:
  - stderr (WARNING+)
  - ~/.local/state/xcloud-gamepad/app.log (DEBUG+, rotating)
"""

import logging
import logging.handlers
from pathlib import Path

_LOG_DIR = Path.home() / ".local" / "state" / "xcloud-gamepad"
_LOG_FILE = _LOG_DIR / "app.log"

_configured = False


def _configure() -> None:
    global _configured
    if _configured:
        return

    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("xcloud_gamepad")
    root.setLevel(logging.DEBUG)

    # ── Rotating file handler (10 MB × 3 backups) ────────────────────
    fh = logging.handlers.RotatingFileHandler(_LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter(
            "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # ── Console handler (WARNING+) ────────────────────────────────────
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter("%(levelname)s  %(message)s"))

    root.addHandler(fh)
    root.addHandler(ch)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the 'xcloud_gamepad' hierarchy."""
    _configure()
    # Strip the 'src.' prefix for cleaner log lines
    clean = name.replace("src.", "")
    return logging.getLogger(f"xcloud_gamepad.{clean}")
