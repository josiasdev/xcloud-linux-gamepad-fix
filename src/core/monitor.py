"""Event monitor – reads raw evdev events in a background thread and dispatches
axis/button updates via caller-supplied callbacks (GLib.idle_add friendly)."""
import threading
from typing import Callable, Optional

try:
    import evdev
    _EVDEV_AVAILABLE = True
except ImportError:
    _EVDEV_AVAILABLE = False


AxisCallback = Callable[[int, int], None]    # (code, value)
ButtonCallback = Callable[[int, bool], None]  # (code, is_pressed)


class EventMonitor:
    """Non-blocking evdev reader.

    Usage::

        monitor = EventMonitor("/dev/input/event20")
        monitor.on_axis   = lambda code, val: GLib.idle_add(update_axis, code, val)
        monitor.on_button = lambda code, val: GLib.idle_add(update_btn,  code, val)
        monitor.start()
        ...
        monitor.stop()
    """

    def __init__(self, event_path: str):
        self._path = event_path
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        self.on_axis:   Optional[AxisCallback]   = None
        self.on_button: Optional[ButtonCallback] = None

    # ------------------------------------------------------------------

    @property
    def is_available(self) -> bool:
        return _EVDEV_AVAILABLE

    def start(self) -> None:
        if not _EVDEV_AVAILABLE:
            raise RuntimeError("python-evdev is not installed.")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    # ------------------------------------------------------------------

    def _run(self) -> None:
        try:
            device = evdev.InputDevice(self._path)
            device.grab()
        except Exception:
            return

        try:
            for event in device.read_loop():
                if self._stop_event.is_set():
                    break

                if event.type == evdev.ecodes.EV_ABS and self.on_axis:
                    self.on_axis(event.code, event.value)

                elif event.type == evdev.ecodes.EV_KEY and self.on_button:
                    self.on_button(event.code, bool(event.value))
        except Exception:
            pass
        finally:
            try:
                device.ungrab()
            except Exception:
                pass
