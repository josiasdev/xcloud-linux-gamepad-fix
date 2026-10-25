"""Tests for EmulationService – managing subprocess lifecycle."""

import subprocess
from unittest.mock import MagicMock

import pytest

from src.core.emulation import EmulationService
from src.models.profile import InputDevice, Profile


@pytest.fixture
def emulation_service():
    return EmulationService()


def test_start_calls_correct_args(emulation_service, monkeypatch):
    mock_popen = MagicMock()
    monkeypatch.setattr("subprocess.Popen", mock_popen)
    device = InputDevice(name="Test", event_path="/dev/input/event0")
    profile = Profile(name="P1", absmap="abs", keymap="key")

    emulation_service.start(device, profile)

    args, _ = mock_popen.call_args
    cmd = args[0]
    assert "xboxdrv" in cmd
    assert "/dev/input/event0" in cmd
    assert "--evdev-absmap" in cmd


def test_stop_handles_zombie_process(emulation_service, monkeypatch):
    mock_process = MagicMock()
    mock_process.wait.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=3)
    emulation_service._process = mock_process
    monkeypatch.setattr("subprocess.run", MagicMock())

    emulation_service.stop()

    assert mock_process.terminate.called
    assert mock_process.kill.called
    assert emulation_service._process is None
