import configparser

class Configure:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('\config\config.ini')
        self.static(config)
        self.delegate(config)
        self.payment(config)
        self.experimental(config)
        
        
    def static(self, c):
        self.atomic = c.get('static', 'atomic')
        print(self.atomic)
    
    
    def delegate(self, c):
        pass
    
    
    def payment(self, c):
        pass
    
    
    def experimental(self, c):
        pass
