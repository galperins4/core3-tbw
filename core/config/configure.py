import configparser

class Configure:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('~\core3-tbw\core\config\config.ini')
        print(config.sections())
