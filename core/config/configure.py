import configparser
from pathlib import Path

class Configure:
    def __init__(self):
        self.home = str(Path.home())
        env_path = self.home+'/core3-tbw/core/config/config.ini'
        
        config = configparser.ConfigParser()
        config.read(env_path)
        self.static(config)
        self.delegate(config)
        self.payment(config)
        self.experimental(config)
        
        
    def static(self, c):
        self.atomic = int(c.get('static', 'atomic'))
        print(type(self.atomic))
    
    
    def delegate(self, c):
        pass
    
    
    def payment(self, c):
        pass
    
    
    def experimental(self, c):
        pass
