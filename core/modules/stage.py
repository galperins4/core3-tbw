class Stage:
    def __init__(self, config, utility, sql, voters, delegate):
        self.config = config
        self.utility = utility
        self.sql = sql
        self.voters = voters
        self.delegate = delegate
        
        
    def get_transaction_fees(self):
        delegate_tx = len([v for v in self.delegate.values() if v >= 0])
        voter_tx = len([v for v in self.voters.values() if v > 0])
        total_tx = voter_tx + delegate_tx
        print(total_tx)
        quit()
    
    
    stage_delegate_payments(self):
        pass
    
    
    stage_voter_payments(self):
        pass
