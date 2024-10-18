import os
import yaml
from . import auxiliary_modules as am

class ConfigurationTool:
    def __init__(self, logger, config_address) -> None:
        self.config_address = config_address
        self.__logger = logger

    def read(self):
        if not am.check_file_in_folder(self.config_address):
            self.__logger.critical(f'Configuration file not found {self.config_address}')
            raise SystemExit(1)
        
        with open(self.config_address, 'r') as file:
            config = yaml.safe_load(file)
        return config

    def write(self, data, append=False):
        """
        Writes the data to the configuration file.
        If append is True, it appends the data to the existing file.
        """
        mode = 'a' if append else 'w'
        with open(self.config_address, mode) as file:
            if append:
                existing_data = self.read() if am.check_file_in_folder(self.config_address) else {}
                existing_data.update(data)
                data = existing_data
            yaml.dump(data, file)

    def default_config(self):
        """
        Returns the default configuration.
        """
        default_config = {
            'first_run': True,
            'measurement_modes': {
                't_0': 40,
                't_1': 60
            },
            'timeout_under_measure': 10
        }
        return default_config

    def ensure_config(self):
        """
        Ensures that the configuration file exists. If not, it creates it with the default configuration.
        """
        if not am.check_file_in_folder(self.config_address):
            self.__logger.warning(f'Configuration file not found {self.config_address}. It will created a new file.')
            self.write(self.default_config())
        elif os.path.getsize(self.config_address) == 0:
            self.__logger.warning(f'Configuration file {self.config_address} is empty. It will be filled with the default configuration.')
            self.write(self.default_config())            