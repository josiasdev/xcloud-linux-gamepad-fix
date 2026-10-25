"""Tests for EventMonitor – handling hardware failures."""
import pytest
from unittest.mock import MagicMock
from src.core.monitor import EventMonitor

def test_unplug_disconnect_signals_ui(monkeypatch):
    # Mock evdev
    mock_evdev = MagicMock()
    mock_device = MagicMock()
    mock_device.read_loop.side_effect = OSError("No such device")
    mock_evdev.InputDevice.return_value = mock_device
    
    monkeypatch.setattr("src.core.monitor.evdev", mock_evdev)
    monkeypatch.setattr("src.core.monitor._EVDEV_AVAILABLE", True)
    
    mock_idle_add = MagicMock()
    monkeypatch.setattr("gi.repository.GLib.idle_add", mock_idle_add)
    
    monitor = EventMonitor("/dev/input/eventX")
    on_button_called = False
    def on_button_callback(code, val):
        nonlocal on_button_called
        on_button_called = True
        
    monitor.on_button = on_button_callback
    
    monitor._run()
    
    assert mock_device.ungrab.called
    assert on_button_called
