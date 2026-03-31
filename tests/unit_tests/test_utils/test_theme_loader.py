"""Tests for the theme_loader module."""

import json
import pytest
from pathlib import Path

from src.utils.config import Config
from src.utils.exceptions import ConfigValidationError, MarkdownImageGeneratorError
from src.utils.theme_loader import discover_themes, list_themes, load_theme, apply_theme


@pytest.fixture
def themes_dir(tmp_path):
    """Create a temporary themes directory with test themes."""
    theme_a = {
        "THEME": {"NAME": "alpha"},
        "COLORS": {"TEXT": "#111111", "HIGHLIGHT": "#222222"},
    }
    theme_b = {
        "THEME": {"NAME": "beta"},
        "COLORS": {"TEXT": "#333333", "HIGHLIGHT": "#444444"},
    }
    (tmp_path / "alpha.json").write_text(json.dumps(theme_a))
    (tmp_path / "beta.json").write_text(json.dumps(theme_b))
    # Also write an invalid JSON file to test robustness
    (tmp_path / "broken.json").write_text("{invalid json")
    return tmp_path


def test_discover_themes(themes_dir):
    themes = discover_themes(themes_dir)
    assert "alpha" in themes
    assert "beta" in themes
    assert "broken" not in themes


def test_discover_themes_nonexistent_dir(tmp_path):
    themes = discover_themes(tmp_path / "no_such_dir")
    assert themes == {}


def test_list_themes(themes_dir):
    names = list_themes(themes_dir)
    assert names == ["alpha", "beta"]


def test_load_theme(themes_dir):
    data = load_theme("alpha", themes_dir)
    assert data["COLORS"]["TEXT"] == "#111111"


def test_load_theme_case_insensitive(themes_dir):
    data = load_theme("ALPHA", themes_dir)
    assert data["THEME"]["NAME"] == "alpha"


def test_load_theme_not_found(themes_dir):
    with pytest.raises(ConfigValidationError, match="not found"):
        load_theme("nonexistent", themes_dir)


def test_apply_theme_merges(tmp_path, themes_dir):
    """apply_theme should merge theme values into config."""
    config_path = tmp_path / "cfg.json"
    config_path.write_text(json.dumps({
        "COLORS": {"TEXT": "#000000", "HIGHLIGHT": "#ffffff", "EXTRA": "#aaa"},
        "PATHS": {"FONT": "/some/font.ttf"},
    }))
    Config().init_config(path=config_path)
    apply_theme(Config(), "alpha", themes_dir)

    # Theme values override
    assert Config()["COLORS"]["TEXT"] == "#111111"
    assert Config()["COLORS"]["HIGHLIGHT"] == "#222222"
    # Non-theme values preserved
    assert Config()["COLORS"]["EXTRA"] == "#aaa"


def test_exception_hierarchy():
    """All custom exceptions should be subclasses of MarkdownImageGeneratorError."""
    from src.utils.exceptions import (
        ImageGenerationError,
        ImageSaveError,
        MarkdownReadError,
    )
    for exc_cls in (ConfigValidationError, ImageGenerationError, ImageSaveError, MarkdownReadError):
        assert issubclass(exc_cls, MarkdownImageGeneratorError)
        assert issubclass(exc_cls, Exception)


def test_catch_base_exception():
    """Catching MarkdownImageGeneratorError should catch all sub-exceptions."""
    with pytest.raises(MarkdownImageGeneratorError):
        raise ConfigValidationError("test")
