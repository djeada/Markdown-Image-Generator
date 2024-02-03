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
        "PAGE_TOP_MARGIN": 250,
        "PAGE_RIGHT_MARGIN": 80,
        "PAGE_NUMBER_FONT_COLOR": "#292929",
        "TEXT_COLOR": "#FFFFFF",
        "BG_COLOR": "#000000",
        "IMAGE_WIDTH": 1080,
        "IMAGE_HEIGHT": 1080,
        "CHAR_WIDTH": 15,
        "DEFAULT_LINE_HEIGHT": 30,
        "LIST_LINE_HEIGHT": 20,
        "TABLE_SCALE_FACTOR": 1,
        "CODE_BLOCK_SCALE_FACTOR": 2,
        "CODE_BLOCK_BG": "#000000",
        "CODE_BLOCK_RADIUS": 20,
        "CODE_BLOCK_TOP_PADDING": 50,
        "START_INDEX": 0,
        "TABLE_FG_COLOR": "#FFFFFF",
        "TABLE_BG_COLOR": "#292929",
        # Add more default values as needed
    }

    def __init__(self):
        self._config_data: Dict[str, Any] = {}
        self.init_config()

    def init_config(self) -> None:
        if not self._config_file.exists():
            self._save_defaults()
        self._load_config()
        self._ensure_defaults()

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

    def _ensure_defaults(self) -> None:
        defaults_added = False
        for key, value in self._default_values.items():
            if key not in self._config_data:
                self._config_data[key] = value
                defaults_added = True
        if defaults_added:
            self._save_config()

    def _save_config(self) -> None:
        with self._config_file.open("w") as file:
            json.dump(self._config_data, file, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        return self._config_data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._config_data[key] = value
        self._save_config()
