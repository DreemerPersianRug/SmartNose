from utils import ConfigurationTool
from utils import Logger
from utils import DataBase

logger = Logger('log', 'logs/log_file.log')

config = ConfigurationTool(logger, 'config/config.yaml')
config.ensure_config()

base = DataBase(logger,'data/data.db')
base.ensure_database()

