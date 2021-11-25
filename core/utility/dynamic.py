#import os.path
#import json
#from .util import Util
#atomic = 100000000


class Dynamic:
    def __init__(self, utility, config):
        self.client = utility.get_client()
        
        #self.username = u
        #self.msg = msg
        #self.network = network
        #self.port = port
        #self.u = Util(self.network)
        #self.client = self.u.get_client(self.port)
        
    
    def get_dynamic_fee(self):        
        try:
            node_configs = self.client.node.configuration()['data']['transactionPool']['dynamicFees']
            if node_configs['enabled'] is "False":
                transaction_fee = int(0.1 * self.config.atomic)
            else:
                dynamic_offset = node_configs['addonBytes']['transfer']
                fee_multiplier = node_configs['minFeePool']
                standard_tx = 230
                v_msg = len(self.config.message) 
                tx_size = standard_tx + v_msg
                #calculate transaction fee
                transaction_fee = self.calculate_dynamic_fee(dynamic_offset, tx_size, fee_multiplier)
        except:
            transaction_fee = int(0.1 * self.config.atomic)

        return transaction_fee
    
    
    def calculate_dynamic_fee(self, t, s, c):
        return int((t+s)*c)

    
    def get_multipay_limit(self):
        try:
            limit = int(self.client.node.configuration()['data']['constants']['multiPaymentLimit'])
        except:
            limit = 20
        return limit
    
