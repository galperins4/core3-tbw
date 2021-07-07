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
        self.multi = c.get('payment', 'multi')
        self.passphrase = c.get('payment', 'passphrase')
        self.secondphrase = c.get('payment', 'secondphrase')
        self.delegate_fee = c.get('payment', 'delegate_fee')
        self.delegate_fee_address = c.get('payment', 'delegate_fee_address')
    
    
    def experimental(self, c):
        self.exchange = c.get('experimental', 'exchange')
        self.convert_from = c.get('experimental', 'convert_from')
        self.convert_address = c.get('experimental', 'convert_address')
        self.convert_to = c.get('experimental', 'convert_to')
        self.address_to = c.get('experimental', 'address_to')
        self.network_to = c.get('experimental', 'network_to')
        self.provider = c.get('experimental', 'provider')
