from configparser import ConfigParser

parser = ConfigParser()
parser.read('admin/config.ini')

def get_config_value(section, key):
    return parser.get(section, key)