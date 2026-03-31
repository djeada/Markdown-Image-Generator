import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, Optional, Set, Type

from src.utils.exceptions import ConfigValidationError

logger = logging.getLogger(__name__)

# Required top-level sections and their mandatory keys
_REQUIRED_SECTIONS: Dict[str, Set[str]] = {
    "PATHS": {"FONT"},
    "PAGE_LAYOUT": {"TOP_MARGIN", "BOTTOM_MARGIN", "RIGHT_MARGIN", "IMAGE_WIDTH", "IMAGE_HEIGHT"},
    "COLORS": {"TEXT", "HIGHLIGHT"},
    "CODE_BLOCK": {"SCALE_FACTOR", "BACKGROUND", "RADIUS", "TOP_PADDING"},
    "TABLE": {"SCALE_FACTOR", "FOREGROUND", "BACKGROUND", "HIGHLIGHT",
              "HEADER_BG_COLOR", "HEADER_FG_COLOR", "HEIGHT"},
}


def singleton(cls: Type) -> Callable[..., Any]:
    instances: Dict[Type, Any] = {}

    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class Config:
    _config_file: Path = Path("config.json")
    # Default configuration values
    _default_values: Dict[str, Any] = {
        "PATHS": {
            "DEFAULT_PAGE": "../resources/page.png",
            "TITLE_PAGE": "../resources/intro.png",
            "FINAL_PAGE": "../resources/final.png",
            "QUESTION_PAGE": "../resources/challenge.png",
            "FONT": "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
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

    def __init__(self) -> None:
        self._config_data: Dict[str, Any] = {}
        self.init_config()

    def init_config(self, path: Optional[Path] = None) -> None:
        self._config_file = path if path is not None else Path("config.json")
        if not self._config_file.exists():
            self._save_defaults()
        self._load_config()

    def _load_config(self) -> None:
        try:
            with self._config_file.open("r") as file:
                self._config_data = json.load(file)
        except json.JSONDecodeError as e:
            logger.error("Configuration file contains invalid JSON: %s", e)
            self._config_data = {}
        except OSError as e:
            logger.error("Could not read configuration file: %s", e)
            self._config_data = {}

    def validate(self) -> None:
        """Validate that all required configuration sections and keys exist.

        Raises:
            ConfigValidationError: If required sections or keys are missing.
        """
        missing = []
        for section, keys in _REQUIRED_SECTIONS.items():
            if section not in self._config_data:
                missing.append(f"section '{section}'")
            else:
                for key in keys:
                    if key not in self._config_data[section]:
                        missing.append(f"key '{section}.{key}'")
        if missing:
            raise ConfigValidationError(
                f"Configuration is missing required entries: {', '.join(missing)}"
            )

    def _save_defaults(self) -> None:
        with self._config_file.open("w") as file:
            json.dump(self._default_values, file, indent=4)

    def _save_config(self) -> None:
        with self._config_file.open("w") as file:
            json.dump(self._config_data, file, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        return self._config_data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._config_data[key] = value
        self._save_config()

    def __getitem__(self, key: str) -> Any:
        try:
            return self._config_data[key]
        except KeyError:
            raise KeyError(f"Key '{key}' not found in configuration data.")

    def __setitem__(self, key: str, value: Any) -> None:
        self._config_data[key] = value
        self._save_config()

    def __contains__(self, key: object) -> bool:
        return key in self._config_data

    def __delitem__(self, key: str) -> None:
        del self._config_data[key]
        self._save_config()

    def __iter__(self) -> Iterator[str]:
        return iter(self._config_data)
