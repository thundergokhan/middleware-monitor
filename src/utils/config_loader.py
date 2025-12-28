import yaml
import os
from .logger import get_logger

class ConfigLoader:
    """
    Responsible for loading and validating the services configuration.
    """
    
    def __init__(self, config_path):
        self.config_path = config_path
        self.logger = get_logger("ConfigLoader")

    def load_config(self):
        """
        Parses the YAML configuration file.
        Returns:
            dict: The configuration dictionary.
        Raises:
            FileNotFoundError: If the config file is missing.
            yaml.YAMLError: If the YAML is invalid.
        """
        if not os.path.exists(self.config_path):
            self.logger.error(f"Configuration file not found at: {self.config_path}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            self.validate_config(config)
            self.logger.info(f"Successfully loaded configuration from {self.config_path}")
            return config
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML configuration: {e}")
            raise

    def validate_config(self, config):
        """
        Basic validation of the configuration structure.
        """
        if not config or 'services' not in config:
            self.logger.error("Invalid configuration: 'services' list is missing.")
            raise ValueError("Invalid configuration: 'services' section is required.")

        for idx, service in enumerate(config['services']):
            if 'name' not in service or 'type' not in service:
                self.logger.error(f"Service at index {idx} missing 'name' or 'type'.")
                raise ValueError(f"Service at index {idx} is malformed. 'name' and 'type' are required.")
