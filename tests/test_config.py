from __future__ import annotations

import json

from virtualbox_rpc.config import DEFAULT_CLIENT_ID, Config


def test_config_defaults():
    cfg = Config()
    assert cfg.client_id == DEFAULT_CLIENT_ID
    assert cfg.polling_interval == 3
    assert cfg.vboxmanage_path is None
    assert cfg.show_hardware_specs is True
    assert cfg.log_level == "INFO"


def test_config_load_from_json(tmp_path):
    config_file = tmp_path / "custom_config.json"
    data = {
        "client_id": "999888777",
        "polling_interval": 10,
        "show_hardware_specs": False,
        "log_level": "DEBUG",
    }
    config_file.write_text(json.dumps(data), encoding="utf-8")

    cfg = Config.load(config_file)
    assert cfg.client_id == "999888777"
    assert cfg.polling_interval == 10
    assert cfg.show_hardware_specs is False
    assert cfg.log_level == "DEBUG"


def test_config_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("VBOX_RPC_CLIENT_ID", "1234567890")
    cfg = Config.load(tmp_path / "nonexistent.json")
    assert cfg.client_id == "1234567890"


def test_config_invalid_json(tmp_path):
    corrupt_file = tmp_path / "corrupt.json"
    corrupt_file.write_text("{invalid json", encoding="utf-8")

    cfg = Config.load(corrupt_file)
    assert cfg.client_id == DEFAULT_CLIENT_ID
