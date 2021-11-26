from crypto.transactions.builder.transfer import Transfer
from crypto.transactions.builder.multi_payment import MultiPayment

class Payments:
    def __init__(self, config, sql, dynamic, utility):
        self.config = config
        self.sql = sql
        self.dynamic = dynamic
        self.utility = utility

        
    def get_nonce(self):
        client = self.utility.get_client()
        n = client.wallets.get(self.config.delegate)
        return int(n['data']['nonce'])

    
    def build_transfer_transaction(address, amount, vendor, fee, pp, sp, nonce):
        # python3 crypto version    
        transaction = Transfer(recipientId=address, amount=amount, vendorField=vendor, fee=fee)
        transaction.set_nonce(int(nonce))
        transaction.schnorr_sign(pp)

        if sp == 'None':
            sp = None
        if sp is not None:
            transaction.second_sign(sp)

        transaction_dict = transaction.to_dict()
        return transaction_dict
