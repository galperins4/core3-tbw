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
