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
        self.other(config)
        self.donate(config)
        
        
    def static(self, c):
        self.atomic = int(c.get('static', 'atomic'))
        self.network = c.get('static', 'network')
        self.username = c.get('static', 'username')
        self.start_block = int(c.get('static', 'start_block'))
    
    
    def delegate(self, c):
        self.delegate = c.get('delegate', 'delegate')
        self.message = c.get('delegate', 'message')
        self.voter_share = int(c.get('delegate', 'voter_share'))
        self.voter_cap = int(c.get('delegate', 'voter_cap'))
        self.voter_min = int(c.get('delegate', 'voter_min'))
        self.whitelist = c.get('delegate', 'whitelist')
        self.whitelist_address = c.get('delegate', 'whitelist_address').split(',')
        self.blacklist = c.get('delegate', 'blacklist')
        self.blacklist_address = c.get('delegate', 'blacklist_address').split(',')
    
    
    def payment(self, c):
        self.interval = int(c.get('payment', 'interval'))
        self.multi = c.get('payment', 'multi')
        self.passphrase = c.get('payment', 'passphrase')
        self.secondphrase = c.get('payment', 'secondphrase')
        self.delegate_fee = c.get('payment', 'delegate_fee').split(',')
        self.delegate_fee_address = c.get('payment', 'delegate_fee_address').split(',')
    
    
    def experimental(self, c):
        self.exchange = c.get('exchange', 'exchange')
        self.convert_from = c.get('exchange', 'convert_from').split(',')
        self.convert_address = c.get('exchange', 'convert_address').split(',')
        self.convert_to = c.get('exchange', 'convert_to').split(',')
        self.address_to = c.get('exchange', 'address_to').split(',')
        self.network_to = c.get('exchange', 'network_to').split(',')
        self.provider = c.get('exchange', 'provider').split(',')
        
        
    def other(self, c):
        self.custom = c.get('other', 'custom')
        self.manual_pay = c.get('other', 'manual_pay')
        self.update_share = c.get('other', 'update_share')

        
    def donate(self, c):
        self.donate = c.get('donate', 'donate')
        self.donate_address = c.get('donate', 'donate_address')
        self.donate_percent = int(c.get('donate', 'donate_percent'))
