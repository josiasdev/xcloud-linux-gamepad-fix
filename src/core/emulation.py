"""Manages the xboxdrv subprocess lifecycle – fully decoupled from GTK."""
import shutil
import subprocess
from typing import Optional

from src.core.logger import get_logger
from src.models.profile import InputDevice, Profile

log = get_logger(__name__)


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
        log.info("Starting xboxdrv: device=%s profile='%s'", device.event_path, profile.name)
        log.debug("Command: %s", cmd)
        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

    def stop(self) -> None:
        """Terminate xboxdrv and kill any stray processes."""
        log.info("Stopping xboxdrv")
        if self._process is not None:
            self._process.terminate()
            try:
                self._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                log.warning("xboxdrv did not exit cleanly – killing")
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
