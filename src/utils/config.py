import json
from pathlib import Path
from typing import Any, Dict


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class Config:
    _config_file = Path("config.json")
    # Default configuration values
    _default_values = {
        "PATHS": {
            "DEFAULT_PAGE": "../resources/page.png",
            "TITLE_PAGE": "../resources/intro.png",
            "FINAL_PAGE": "../resources/final.png",
            "QUESTION_PAGE": "../resources/challenge.png",
        },
        "PAGE_LAYOUT": {
            "TOP_MARGIN": 250,
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
        },
    }

    def __init__(self):
        self._config_data: Dict[str, Any] = {}
        self.init_config()

    def init_config(self, path: Path = None) -> None:
        self._config_file = path if path is not None else Path("config.json")
        if not self._config_file.exists():
            self._save_defaults()
        self._load_config()

    def _load_config(self) -> None:
        try:
            with self._config_file.open("r") as file:
                self._config_data = json.load(file)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self._config_data = {}

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

    def __getitem__(self, key):
        try:
            return self._config_data[key]
        except KeyError:
            raise KeyError(f"Key '{key}' not found in configuration data.")

    def __setitem__(self, key, value):
        self._config_data[key] = value
        self._save_config()

    def __contains__(self, key):
        return key in self._config_data

    def __delitem__(self, key):
        del self._config_data[key]
        self._save_config()

    def __iter__(self):
        return iter(self._config_data)
