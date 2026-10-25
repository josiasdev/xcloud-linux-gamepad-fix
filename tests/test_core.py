"""Tests for ProfileRepository – JSON persistence layer."""
import json
import pytest
from pathlib import Path

from src.models.profile import DEFAULT_PROFILES, Profile
from src.config.profile_repository import ProfileRepository


# ---------------------------------------------------------------------------
# Test 1 – Defaults are seeded on first run
# ---------------------------------------------------------------------------

def test_default_profiles_created_on_first_run(tmp_path):
    """When no JSON file exists, ProfileRepository must create it with defaults."""
    repo_path = tmp_path / "profiles.json"
    repo = ProfileRepository(path=repo_path)

    assert repo_path.exists(), "profiles.json must be created automatically"

    profiles = repo.all()
    assert len(profiles) == len(DEFAULT_PROFILES), (
        f"Expected {len(DEFAULT_PROFILES)} default profiles, got {len(profiles)}"
    )
    assert all(isinstance(p, Profile) for p in profiles)


# ---------------------------------------------------------------------------
# Test 2 – CRUD round-trip
# ---------------------------------------------------------------------------

def test_add_edit_remove_profile(tmp_path):
    """add(), update(), remove() must persist correctly across repository instances."""
    repo_path = tmp_path / "profiles.json"
    repo = ProfileRepository(path=repo_path)

    initial_count = len(repo.all())

    new_profile = Profile(
        name="Meu Controle Custom",
        absmap="ABS_X=x1,ABS_Y=y1",
        keymap="BTN_SOUTH=a",
        axismap="-y1=y1",
    )
    repo.add(new_profile)

    # Reload from disk to prove persistence
    repo2 = ProfileRepository(path=repo_path)
    profiles = repo2.all()
    assert len(profiles) == initial_count + 1

    last = profiles[-1]
    assert last.name == "Meu Controle Custom"
    assert last.absmap == "ABS_X=x1,ABS_Y=y1"

    # Edit
    updated = Profile(name="Controle Editado", absmap="ABS_X=x1", keymap="BTN_A=a", axismap="")
    repo2.update(len(profiles) - 1, updated)

    repo3 = ProfileRepository(path=repo_path)
    assert repo3.all()[-1].name == "Controle Editado"

    # Remove
    repo3.remove(len(repo3.all()) - 1)
    repo4 = ProfileRepository(path=repo_path)
    assert len(repo4.all()) == initial_count


# ---------------------------------------------------------------------------
# Test 3 – Corrupted JSON is recovered gracefully
# ---------------------------------------------------------------------------

def test_corrupted_json_falls_back_to_defaults(tmp_path):
    """If profiles.json contains invalid JSON, defaults are restored without crashing."""
    repo_path = tmp_path / "profiles.json"
    repo_path.parent.mkdir(parents=True, exist_ok=True)
    repo_path.write_text("{{{INVALID JSON", encoding="utf-8")

    repo = ProfileRepository(path=repo_path)
    profiles = repo.all()

    assert len(profiles) == len(DEFAULT_PROFILES), (
        "Corrupted JSON must be recovered to defaults"
    )
    # Verify the file was rewritten with valid JSON
    data = json.loads(repo_path.read_text())
    assert isinstance(data, list)


# ---------------------------------------------------------------------------
# Test 4 – Profile.to_xboxdrv_args produces correct CLI flags
# ---------------------------------------------------------------------------

def test_profile_to_xboxdrv_args():
    """Profile.to_xboxdrv_args must return correctly ordered xboxdrv arguments."""
    p = Profile(
        name="Test",
        absmap="ABS_X=x1",
        keymap="BTN_SOUTH=a",
        axismap="-y1=y1",
    )
    args = p.to_xboxdrv_args()

    assert "--evdev-absmap" in args
    assert "ABS_X=x1" in args
    assert "--evdev-keymap" in args
    assert "BTN_SOUTH=a" in args
    assert "--axismap" in args
    assert "-y1=y1" in args
    assert "--mimic-xpad" in args
    assert "--silent" in args


# ---------------------------------------------------------------------------
# Test 5 – Hardware parser ignores noise nodes
# ---------------------------------------------------------------------------

def test_hardware_parser_ignores_noise_nodes(tmp_path, monkeypatch):
    """list_controllers() must exclude Motion Sensors and Touchpad interfaces."""
    fake_devices = tmp_path / "devices"
    fake_devices.write_text(
        "I: Bus=0003 Vendor=054c Product=05c4 Version=8111\n"
        'N: Name="Sony Computer Entertainment Wireless Controller"\n'
        "H: Handlers=event20 js0 \n"
        "\n"
        "I: Bus=0003 Vendor=054c Product=05c4 Version=8111\n"
        'N: Name="Sony Computer Entertainment Wireless Controller Motion Sensors"\n'
        "H: Handlers=event21 js1 \n"
        "\n"
        "I: Bus=0003 Vendor=054c Product=05c4 Version=8111\n"
        'N: Name="Sony Computer Entertainment Wireless Controller Touchpad"\n'
        "H: Handlers=mouse3 event22 js2 \n"
        "\n",
        encoding="utf-8",
    )

    import src.core.hardware as hw
    monkeypatch.setattr(hw, "_PROC_DEVICES", str(fake_devices))

    from src.core.hardware import list_controllers
    # Force reimport of module-level constant through the monkeypatched attribute
    controllers = list_controllers()

    assert len(controllers) == 1, f"Expected 1 controller, got {len(controllers)}: {controllers}"
    assert controllers[0].name == "Sony Computer Entertainment Wireless Controller"
    assert controllers[0].event_path == "/dev/input/event20"
    assert controllers[0].vendor_id == "054c"
