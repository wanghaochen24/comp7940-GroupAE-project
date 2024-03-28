import configparser
config = configparser.ConfigParser()
config.read('config.ini')
print(config['TELEGRAM']['ACCESS_TOKEN'])