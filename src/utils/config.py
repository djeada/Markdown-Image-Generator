import json
import os


class Config:
    _instance = None
    _config_file = "config.json"

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

    def __new__(cls, *args, **kwargs):
        # Ensure a single instance (singleton pattern)
        if not isinstance(cls._instance, cls):
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
            cls._instance.init_config()
        return cls._instance

    def init_config(self):
        # If config file doesn't exist, create it with default values
        if not os.path.exists(self._config_file):
            with open(self._config_file, "w") as file:
                json.dump(self._default_values, file)

        # Load the configuration
        with open(self._config_file, "r") as file:
            self._config_data = json.load(file)

        # Ensure all default keys are in the loaded configuration
        for key, value in self._default_values.items():
            if key not in self._config_data:
                self._config_data[key] = value

        # Save back the configuration in case defaults were added
        with open(self._config_file, "w") as file:
            json.dump(self._config_data, file)

    def get(self, key, default=None):
        # Return the value associated with key, if not found, return the default value or None
        return self._config_data.get(key, default)

    def set(self, key, value):
        # Set the value for the key and save to file
        self._config_data[key] = value
        with open(self._config_file, "w") as file:
            json.dump(self._config_data, file)

    @staticmethod
    def get_instance():
        # Returns the singleton instance of Config
        if not Config._instance:
            Config()
        return Config._instance
