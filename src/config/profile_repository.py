"""Profile persistence service – reads/writes ~/.config/xcloud-gamepad/profiles.json."""
import json
import os
from pathlib import Path
from typing import List

from src.core.logger import get_logger
from src.models.profile import DEFAULT_PROFILES, Profile

log = get_logger(__name__)

CONFIG_DIR = Path.home() / ".config" / "xcloud-gamepad"
PROFILES_FILE = CONFIG_DIR / "profiles.json"


class ProfileRepository:
    """Handles loading and saving profiles to disk."""

    def __init__(self, path: Path = PROFILES_FILE):
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._write_defaults()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def all(self) -> List[Profile]:
        """Return all profiles from disk."""
        raw = self._load_raw()
        return [Profile.from_dict(d) for d in raw]

    def save_all(self, profiles: List[Profile]) -> None:
        """Persist the full list of profiles to disk."""
        self._write([p.to_dict() for p in profiles])

    def add(self, profile: Profile) -> None:
        profiles = self.all()
        profiles.append(profile)
        self.save_all(profiles)

    def update(self, index: int, profile: Profile) -> None:
        profiles = self.all()
        profiles[index] = profile
        self.save_all(profiles)

    def remove(self, index: int) -> None:
        profiles = self.all()
        del profiles[index]
        self.save_all(profiles)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_raw(self) -> list:
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("profiles.json must be a list")
            return data
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            log.error(f"Failed to load profiles: {e}. Falling back to defaults.")
            self._write_defaults()
            return list(DEFAULT_PROFILES)

    def _write_defaults(self) -> None:
        log.info("Resetting profiles to defaults.")
        self._write(list(DEFAULT_PROFILES))

    def _write(self, data: list) -> None:
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Failed to save profiles: {e}")
