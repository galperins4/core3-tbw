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
        self.network = c.get('static', 'network')
        self.username = c.get('static', 'username')
        self.block_check = int(c.get('static', 'block_check'))
        self.start_block = int(c.get('static', 'start_block'))
    
    
    def delegate(self, c):
        self.delegate = c.get('delegate', 'delegate')
        self.message = c.get('delegate', 'message')
        self.voter_share = c.get('delegate', 'voter_share')
        self.voter_cap = c.get('delegate', 'voter_cap')
        self.voter_min = c.get('delegate', 'voter_min')
        self.fixed = c.get('delegate', 'fixed')
        self.whitelist = c.get('delegate', 'whitelist')
        self.whitelist_address = c.get('delegate', 'whitelist_address')
        self.blacklist = c.get('delegate', 'blacklist')
        self.blacklist_address = c.get('delegate', 'blacklist_address')
    
    
    def payment(self, c):
        self.interval = c.get('payment', 'interval')
    
    
    def experimental(self, c):
        pass
