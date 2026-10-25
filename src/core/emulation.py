"""Manages the xboxdrv subprocess lifecycle – fully decoupled from GTK."""
import os
import shutil
import subprocess
from typing import Optional

from src.models.profile import InputDevice, Profile


class EmulationService:
    """Starts and stops xboxdrv as a child process."""

    def __init__(self):
        self._process: Optional[subprocess.Popen] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self, device: InputDevice, profile: Profile) -> None:
        """Launch xboxdrv with privilege escalation (pkexec > sudo)."""
        if self.is_running:
            raise RuntimeError("Already running. Call stop() first.")

        auth = self._auth_cmd()
        cmd = auth + ["xboxdrv", "--evdev", device.event_path] + profile.to_xboxdrv_args()
        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def stop(self) -> None:
        """Terminate xboxdrv and kill any stray processes."""
        if self._process is not None:
            self._process.terminate()
            try:
                self._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

        auth = self._auth_cmd()
        subprocess.run(
            auth + ["killall", "xboxdrv"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _auth_cmd():
        if shutil.which("pkexec"):
            return ["pkexec"]
        return ["sudo"]
