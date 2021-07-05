import configparser

class Configure:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        print(config.options('delegate'))
