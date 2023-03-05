import json
import math
import requests
import time
import logging
from lowercase_booleans import false


class Exchange:
    def __init__(self, sql, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.sql = sql
        
    def truncate(self,f, n):
        return math.floor(f * 10 ** n) / 10 ** n
   

    def exchange_select(self, index, address, amount, provider):
        if provider == "ChangeNow":
            pay = self.process_changenow_exchange(index, address, amount)
        elif provider == "SimpleSwap":
            pay = self.process_simpleswap_exchange(index, address, amount)
        elif provider == "StealthEx":
            pay = self.process_stealth_exchange(index, address, amount)
        else:
            pay = address
        time.sleep(5)
        return pay
    
    def process_simpleswap_exchange(self, index, address, amount):
        fixed = false
        self.logger.info("Processing Exchange")
        amount = self.truncate((amount / self.config.atomic),4)
        self.logger.info(f"Exchange Amount: {amount}")
        url = 'https://t1mi6dwix2.execute-api.us-west-2.amazonaws.com/Test/exchange'
        data_in = {"fixed": fixed,
                   "currency_from": self.config.convert_from[index],
                   "currency_to": self.config.convert_to[index],
                   "address_to": self.config.address_to[index],
                   "amount": str(amount),
                   "user_refund_address":address}
        
        res_bytes={}
        res_bytes['data'] = json.dumps(data_in).encode('utf-8')
        
        try:
            r = requests.get(url, params=res_bytes)
            if r.json()['status'] == "success":
                payin_address = r.json()['payinAddress']
                exchangeid = r.json()['exchangeId']
                self.sql.open_connection()
                self.sql.store_exchange(address, payin_address, self.config.address_to[index], amount, exchangeid)
                self.sql.close_connection()
                self.logger.info("Exchange Success") 
            else:
                payin_address = address
                self.logger.error("Exchange Fail")
        except:
            payin_address = address
            self.logger.error("Exchange Fail")
    
        self.logger.info(f"Pay In Address {payin_address}")
        return payin_address
    
    
    def process_changenow_exchange(self, index, address, amount):
        self.logger.info("Processing Exchange")
        amount = self.truncate((amount / self.config.atomic),4)
        self.logger.info(f"Exchange Amount: {amount}")
        url = 'https://mkcnus24ib.execute-api.us-west-2.amazonaws.com/Test/exchange'
        data_in = {"fromCurrency": self.config.convert_from[index],
                   "toCurrency": self.config.convert_to[index],
                   "toNetwork": self.config.network_to[index],
                   "address": self.config.address_to[index],
                   "fromAmount": str(amount),
                   "refundAddress":address}
        try:
            r = requests.get(url, params=data_in)
            if r.json()['status'] == "success":
                payin_address = r.json()['payinAddress']
                exchangeid = r.json()['exchangeId']
                self.sql.open_connection()
                self.sql.store_exchange(address, payin_address, self.config.address_to[index], amount, exchangeid)
                self.sql.close_connection()
                self.logger.info("Exchange Success") 
            else:
                payin_address = address
                self.logger.error("Exchange Fail")
        except:
            payin_address = address
            self.logger.error("Exchange Fail")
    
        return payin_address
    
    
    def process_stealth_exchange(self, index, address, amount):
        self.logger.info("Processing Exchange")
        amount = self.truncate((amount / self.config.atomic),4)
        self.logger.info(f"Exchange Amount: {amount}")
        url = 'https://4kb3mxdi2b.execute-api.us-west-2.amazonaws.com/Test/exchange'
        data_in = {"currency_from": self.config.convert_from[index],
                   "currency_to": self.config.convert_to[index],
                   "address_to": self.config.address_to[index],
                   "amount_from": str(amount),
                   "refund_address":address}
        
        res_bytes={}
        res_bytes['data'] = json.dumps(data_in).encode('utf-8')
        
        try:
            r = requests.get(url, params=res_bytes)
            if r.json()['status'] == "success":
                payin_address = r.json()['payinAddress']
                exchangeid = r.json()['exchangeId']
                self.sql.open_connection()
                self.sql.store_exchange(address, payin_address, self.config.address_to[index], amount, exchangeid)
                self.sql.close_connection()
                self.logger.info("Exchange Success") 
            else:
                payin_address = address
                self.logger.error("Exchange Fail")
        except:
            payin_address = address
            self.logger.error("Exchange Fail")
    
        self.logger.info(f"Pay In Address {payin_address}")
        return payin_address
