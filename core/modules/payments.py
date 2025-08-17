from crypto.transactions.builder.transfer_builder import TransferBuilder
from crypto.transactions.builder.multipayment_builder import MultipaymentBuilder
from crypto.utils.unit_converter import UnitConverter
import time

class Payments:
    def __init__(self, config, sql, dynamic, utility, exchange):
        self.config = config
        self.sql = sql
        self.dynamic = dynamic
        self.utility = utility
        self.exchange = exchange
        self.client = self.utility.get_client()
        self.pool_client = self.utility.get_pool_client()

    
    def non_accept_check(self, c, a):
        removal_check = []
        for k, v in c.items():
            if k not in a:
                print("Transaction ID Not Accepted")
                removal_check.append(v)
                self.sql.open_connection()
                self.sql.delete_transaction_record(k)
                self.sql.close_connection()
        return removal_check
    
    
    def get_nonce(self):
        n = self.client.wallets.get(self.config.delegate)
        return n['data']['nonce']

    
    def build_transfer_transaction(self, address, amount, vendor, fee, nonce):
        transaction = TransferBuilder.new()
        transaction.to(address)
        transaction.value(amount)
        transaction.nonce(int(nonce))
        transaction.gas_price(fee['gas_price'])
        transaction.gas_limit(fee['gas_limit'])
        transaction.sign(self.config.passphrase)

        sp = self.config.secondphrase
        if sp == 'None':
            sp = None
        if sp is not None:
            transaction.legacy_second_sign(sp)

        transaction_dict = transaction.to_dict()
        transaction_hex = transaction.transaction.serialize().hex()

        return transaction_dict, transaction_hex


    def build_multi_transaction(self, payments, nonce):
        fee = self.dynamic.get_dynamic_fee_multi(len(payments))
        transaction = MultipaymentBuilder.new()
        print(fee)

        for i in payments:
            # exchange processing
            if i[1] in self.config.convert_address and self.config.exchange == "Y":
                index = self.config.convert_address.index(i[1])
                pay_in = self.exchange.exchange_select(index, i[1], i[2], self.config.provider[index])
                transaction.pay(pay_in, i[2])
            else:
                transaction.pay(i[1], i[2])
        
        transaction.gas_price(fee['gas_price'])
        transaction.gas_limit(fee['gas_limit'])
        transaction.nonce(nonce)
        transaction.sign(self.config.passphrase)
        
        sp = self.config.secondphrase
        if sp == 'None':
            sp = None
        if sp is not None:
            transaction.legacy_second_sign(sp)
    
        transaction_dict = transaction.to_dict()
        transaction_hex = transaction.transaction.serialize().hex()
        return transaction_dict, transaction_hex
    
    
    def broadcast_standard(self, tx, tx_dict):
        # broadcast to relay
        try:
            transaction = self.pool_client.transactions.create(tx)
            print(transaction)
            records = [[j['to'], j['value'], j['hash']] for j in tx_dict]
            time.sleep(1)
        except BaseException as e:
            # error
            print("Something went wrong", e)
            quit()

        self.sql.open_connection()
        self.sql.store_transactions(records)
        self.sql.close_connection()
    
        return transaction['data']['accept']
    
    # DOES NOT WORK
    def broadcast_multi(self, tx, tx_dict):    
        # broadcast to relay
        try:
            transaction = self.pool_client.transactions.create(tx)
            print(transaction)
            print(tx_dict['pay'])
            #for i in tx:
            #    records = []
            #    id = i['hash']
            #    records = [[j['to'], j['value'], id] for j in tx_dict]
            #    # snekdb.storeTransactions(records)
            #time.sleep(1)
        except BaseException as e:
            # error
            print("Something went wrong", e)
            quit()
    
        self.sql.open_connection()
        #self.sql.store_transactions(records)
        self.sql.close_connection()
        
        return transaction['data']['accept']
