"""Tests for ProfileRepository – JSON persistence layer."""
import json
import pytest
from unittest.mock import MagicMock
from src.config.profile_repository import ProfileRepository
from src.models.profile import DEFAULT_PROFILES

def test_default_profiles_created_on_first_run(tmp_path):
    repo_path = tmp_path / "profiles.json"
    repo = ProfileRepository(path=repo_path)
    assert repo_path.exists()
    assert len(repo.all()) == len(DEFAULT_PROFILES)

def test_corrupted_json_falls_back_to_defaults(tmp_path):
    repo_path = tmp_path / "profiles.json"
    repo_path.write_text("{{{INVALID JSON", encoding="utf-8")
    repo = ProfileRepository(path=repo_path)
    assert len(repo.all()) == len(DEFAULT_PROFILES)

def test_save_permission_error_handled(tmp_path, monkeypatch):
    repo_path = tmp_path / "profiles.json"
    repo = ProfileRepository(path=repo_path)
    
    # Mock para falhar apenas no salvamento
    original_open = open
    def mock_open(path, *args, **kwargs):
        if str(path) == str(repo_path) and "w" in (args[0] if args else kwargs.get("mode", "")):
            raise PermissionError("Denied")
        return original_open(path, *args, **kwargs)
        
    monkeypatch.setattr("builtins.open", mock_open)
    # Deve logar e não lançar exceção fatal
    repo.add(repo.all()[0])
