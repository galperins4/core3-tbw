class Stage:
    def __init__(self, config, dynamic, sql, voters, delegate):
        self.config = config
        self.dynamic = dynamic
        self.sql = sql
        self.voters = voters
        self.delegate = delegate
        
        # get transactions
        fees = self.get_transaction_fees()
        print(fees)
        quit()
        
        # stage delegate payments
        
        # stage voter paymnets
        
        
    def get_transaction_fees(self):
        delegate_tx = len([v for v in self.delegate.values() if v >= 0])
        voter_tx = len([v for v in self.voters.values() if v > 0])
        total_tx = voter_tx + delegate_tx
        print(total_tx)
        
        # check if multipayments
        if self.config.multi == "Y":
            multi_limit = self.dynamic.get_multipay_limit()
            if total_tx % multi_limit == 0:
                transactions = round(total_tx / multi_limit)
                transaction_fees = int(transactions * (self.config.multi_fee * self.config.atomic))
            elif total_tx % multi_limit == 1:
                multi_transactions = round(total_tx / multi_limit)
                transaction_fees = int(((multi_transactions * (self.config.multi_fee * self.config.atomic)) + self.dynamic.get_dynamic_fee()))
            else:
                transactions = round(total_tx // multi_limit) + 1
                transaction_fees = int(transactions * (self.config.multi_fee * self.config.atomic))
        else:
            transaction_fees = int(total_tx * self.dynamic.get_dynamic_fee())
        return transaction_fees
        
    
    def stage_delegate_payments(self):
        pass
    
    
    def stage_voter_payments(self):
        pass
