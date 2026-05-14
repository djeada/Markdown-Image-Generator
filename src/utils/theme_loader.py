"""Theme loader for the Markdown Image Generator.

Discovers and loads theme JSON files from the themes/ directory, and applies
them to the Config singleton by merging theme values into the active config.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from src.utils.exceptions import ConfigValidationError

logger = logging.getLogger(__name__)

# Default search path relative to the project root
_THEMES_DIR = Path(__file__).resolve().parent.parent.parent / "themes"


def discover_themes(themes_dir: Optional[Path] = None) -> Dict[str, Path]:
    """Return a mapping of theme name → JSON file path.

    Args:
        themes_dir: Directory to search. Defaults to the project ``themes/`` folder.

    Returns:
        Dictionary mapping lowercase theme names to their file paths.
    """
    search_dir = themes_dir or _THEMES_DIR
    themes: Dict[str, Path] = {}
    if not search_dir.is_dir():
        return themes
    for path in sorted(search_dir.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            name = data.get("THEME", {}).get("NAME", path.stem)
            themes[name.lower()] = path
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Skipping invalid theme file %s: %s", path, e)
    return themes


def list_themes(themes_dir: Optional[Path] = None) -> List[str]:
    """Return a sorted list of available theme names.

    Args:
        themes_dir: Directory to search. Defaults to the project ``themes/`` folder.

    Returns:
        Sorted list of theme names.
    """
    return sorted(discover_themes(themes_dir).keys())


def load_theme(name: str, themes_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load and return the raw theme data for the given theme name.

    Args:
        name: Case-insensitive theme name (e.g. ``"dark_modern"``).
        themes_dir: Directory to search. Defaults to the project ``themes/`` folder.

    Returns:
        The parsed JSON data of the theme file.

    Raises:
        ConfigValidationError: If the theme is not found or cannot be loaded.
    """
    themes = discover_themes(themes_dir)
    key = name.lower()
    if key not in themes:
        available = ", ".join(sorted(themes.keys())) or "(none)"
        raise ConfigValidationError(
            f"Theme '{name}' not found. Available themes: {available}"
        )

    path = themes[key]
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise ConfigValidationError(
            f"Failed to load theme '{name}' from {path}: {e}"
        ) from e


def apply_theme(config: Any, theme_name: str, themes_dir: Optional[Path] = None) -> None:
    """Load a theme and merge its values into the Config instance.

    Existing config keys that are also present in the theme will be overwritten.
    Config keys not present in the theme remain unchanged.

    Args:
        config: A Config instance (or dict-like object with ``get``/``set``).
        theme_name: Case-insensitive theme name.
        themes_dir: Directory to search. Defaults to the project ``themes/`` folder.

    Raises:
        ConfigValidationError: If the theme is not found or cannot be loaded.
    """
    theme_data = load_theme(theme_name, themes_dir)
    for section, values in theme_data.items():
        existing = config.get(section, {})
        if isinstance(existing, dict) and isinstance(values, dict):
            existing.update(values)
            config.set(section, existing, persist=False)
        else:
            config.set(section, values, persist=False)
    logger.info("Applied theme '%s'", theme_name)
