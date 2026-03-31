"""Tests for the Config class including validation."""

import json
import pytest
from pathlib import Path

from src.utils.config import Config, singleton
from src.utils.exceptions import ConfigValidationError


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the Config singleton between tests."""
    # Clear the singleton cache so each test gets a fresh Config
    if hasattr(singleton, '__wrapped__'):
        pass
    # Access the closure variable to clear cached instances
    yield
    # Force re-creation on next call by clearing internal state
    Config()._config_data = {}


@pytest.fixture
def valid_config_file(tmp_path):
    """Create a valid config JSON file."""
    config = {
        "PATHS": {
            "DEFAULT_PAGE": "../resources/page.png",
            "TITLE_PAGE": "../resources/intro.png",
            "FINAL_PAGE": "../resources/final.png",
            "QUESTION_PAGE": "../resources/challenge.png",
            "FONT": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        },
        "PAGE_LAYOUT": {
            "TOP_MARGIN": 250,
            "BOTTOM_MARGIN": 250,
            "RIGHT_MARGIN": 80,
            "IMAGE_WIDTH": 1080,
            "IMAGE_HEIGHT": 1080,
            "CHAR_WIDTH": 15,
            "DEFAULT_LINE_HEIGHT": 30,
            "LIST_LINE_HEIGHT": 20,
            "START_INDEX": 0,
        },
        "COLORS": {
            "PAGE_NUMBER_FONT": "#292929",
            "TEXT": "#FFFFFF",
            "BACKGROUND": "#000000",
            "HIGHLIGHT": "#ffab00",
        },
        "CODE_BLOCK": {
            "SCALE_FACTOR": 2,
            "BACKGROUND": "#000000",
            "RADIUS": 20,
            "TOP_PADDING": 50,
        },
        "TABLE": {
            "SCALE_FACTOR": 1,
            "FOREGROUND": "#FFFFFF",
            "BACKGROUND": "#292929",
            "HIGHLIGHT": "#ffab00",
            "HEADER_BG_COLOR": "#8c52ff",
            "HEADER_FG_COLOR": "#000000",
            "HEIGHT": 8,
        },
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    return path


def test_config_load_valid(valid_config_file):
    config = Config()
    config.init_config(path=valid_config_file)
    assert config["PAGE_LAYOUT"]["IMAGE_WIDTH"] == 1080
    assert config["COLORS"]["TEXT"] == "#FFFFFF"


def test_config_validate_valid(valid_config_file):
    config = Config()
    config.init_config(path=valid_config_file)
    # Should not raise
    config.validate()


def test_config_validate_missing_section(tmp_path):
    incomplete = {"PATHS": {"FONT": "/some/font.ttf"}}
    path = tmp_path / "config.json"
    path.write_text(json.dumps(incomplete))

    config = Config()
    config.init_config(path=path)
    with pytest.raises(ConfigValidationError, match="section 'PAGE_LAYOUT'"):
        config.validate()


def test_config_validate_missing_key(tmp_path):
    # Has all sections but missing FONT key in PATHS
    incomplete = {
        "PATHS": {},
        "PAGE_LAYOUT": {"TOP_MARGIN": 1, "BOTTOM_MARGIN": 1, "RIGHT_MARGIN": 1, "IMAGE_WIDTH": 1, "IMAGE_HEIGHT": 1},
        "COLORS": {"TEXT": "#FFF", "HIGHLIGHT": "#FFF"},
        "CODE_BLOCK": {"SCALE_FACTOR": 1, "BACKGROUND": "#000", "RADIUS": 1, "TOP_PADDING": 1},
        "TABLE": {"SCALE_FACTOR": 1, "FOREGROUND": "#FFF", "BACKGROUND": "#000",
                  "HIGHLIGHT": "#FFF", "HEADER_BG_COLOR": "#FFF",
                  "HEADER_FG_COLOR": "#000", "HEIGHT": 1},
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(incomplete))

    config = Config()
    config.init_config(path=path)
    with pytest.raises(ConfigValidationError, match="PATHS.FONT"):
        config.validate()


def test_config_load_invalid_json(tmp_path):
    bad_json = tmp_path / "config.json"
    bad_json.write_text("{invalid json!!!}")

    config = Config()
    config.init_config(path=bad_json)
    # Should have loaded empty config
    assert config.get("PATHS") is None


def test_config_get_with_default():
    config = Config()
    assert config.get("NONEXISTENT", "fallback") == "fallback"


def test_config_getitem_missing_key():
    config = Config()
    config._config_data = {"EXISTS": True}
    with pytest.raises(KeyError, match="not found"):
        _ = config["MISSING"]


def test_config_contains():
    config = Config()
    config._config_data = {"FOO": "bar"}
    assert "FOO" in config
    assert "BAZ" not in config


def test_config_creates_defaults_when_missing(tmp_path):
    config_path = tmp_path / "new_config.json"
    assert not config_path.exists()

    config = Config()
    config.init_config(path=config_path)

    assert config_path.exists()
    data = json.loads(config_path.read_text())
    assert "PATHS" in data
    assert "COLORS" in data
