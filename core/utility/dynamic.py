class Dynamic:
    def __init__(self, utility, config):
        self.client = utility.get_client()
        self.config = config
        
    
    def get_dynamic_fee(self):        
        try:
            node_configs = self.client.node.configuration()['data']
            fees = {"gas_price": node_configs['constants']['gas']['minimumGasPrice'],
                    "gas_limit": node_configs['constants']['gas']['minimumGasLimit']}

            fees["tx_fee"] = int((fees['gas_price'] * fees['gas_limit']) / self.config.offset)
        except:
            # HARD CODED
            fees = {"gas_price": 5000000000, "gas_limit": 21000, "tx_fee": 10500}

        return fees
    

    def get_dynamic_fee_multi(self, numtx):
        try:
            node_configs = self.client.node.configuration()['data']
            fees = {"gas_price": node_configs['constants']['gas']['minimumGasPrice'],
                    "gas_limit": (node_configs['constants']['gas']['minimumGasLimit'] * numtx)}

            fees["tx_fee"] = int((fees['gas_price'] * node_configs['constants']['gas']['minimumGasLimit'] * numtx) / self.config.offset)

        except:
            # HARD CODED
            fees = {"gas_price": 5000000000, "gas_limit": 21000, "tx_fee": (10500 * numtx)} 

        return fees
    
    #UNUSED
    def calculate_dynamic_fee(self, t, s, c):
        return int((t+s)*c)

    #UNUSED
    def calculate_dynamic_multifee(self, t, s, c):
         fee = int((t + (round(s/2) + 1)) * c)
         return fee
    
    #API ENDPOINT DOES NOT WORK
    def get_multipay_limit(self):
        try:
            limit = int(self.client.node.configuration()['data']['constants']['multiPaymentLimit'])
        except:
            limit = 40
        return limit
    
    # API ENDPOINT DOES NOT WORK 
    def get_tx_request_limit(self):
        try:
            limit = self.client.node.configuration()['data']['transactionPool']['maxTransactionsPerRequest']
        except:
            limit = 40
        return limit
    
