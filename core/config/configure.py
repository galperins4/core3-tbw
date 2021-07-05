import configparser

class Configure:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.static_config()
        self.delegate_config()
        self.payment_config()
        self.experimental_config()
        
        
    def static_config(self):
        self.atomic = config.get('static', 'atomic')
        print(atomic)
    
    
    def delegate_config(self):
        pass
    
    
    def payment_config(self):
        pass
    
    
    def experimental_config(self):
        pass
