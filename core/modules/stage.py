class Stage:
    def __init__(self, config, dynamic, sql, voters, delegate):
        self.config = config
        self.dynamic = dynamic
        self.sql = sql
        self.voters = voters
        self.delegate = delegate
        
        # get transactions
        fees = self.get_transaction_fees()
        
        # stage delegate payments
        self.stage_delegate_payments(fees)
        
        # stage voter payments
        self.stage_voter_payments()
        
        
    def get_transaction_fees(self):
        delegate_tx = len([v for v in self.delegate.values() if v >= 0])
        voter_tx = len([v for v in self.voters.values() if v > 0])
        total_tx = voter_tx + delegate_tx
        print("Total Transactions: ", total_tx)
        
        # check if multipayments
        if self.config.multi == "Y":
            multi_limit = self.dynamic.get_multipay_limit()
            print("Multipay Limit", multi_limit)
            if total_tx < multi_limit:
                # only requires a single  multipayment tx
                print("Option A - Total transactions < 1 multipayment")
                transaction_fees = int(self.config.multi_fee * self.config.atomic)
            else:
                # number of transactions fit exactly in x number of multipays
                if total_tx % multi_limit == 0:
                    print("Option B - Total transactions evenly spread into multipayment")
                    transactions = round(total_tx / multi_limit)
                    transaction_fees = int(transactions * (self.config.multi_fee * self.config.atomic))
                # number of transactions is 1 greater than limit which splits last payment into regular transaction
                elif total_tx % multi_limit == 1:
                    print("Option C - One extra payment over multipay limit requiring a single tx")
                    multi_transactions = round(total_tx / multi_limit)
                    transaction_fees = int(((multi_transactions * (self.config.multi_fee * self.config.atomic)) + self.dynamic.get_dynamic_fee()))
                # number of transactions falls into n+1 multipayment
                else:
                    print("Option D - Total transactions fit into n+1 multpayments")
                    transactions = round(total_tx // multi_limit) + 1
                    transaction_fees = int(transactions * (self.config.multi_fee * self.config.atomic))
        else:
            transaction_fees = int(total_tx * self.dynamic.get_dynamic_fee())
        return transaction_fees
        
    
    def stage_delegate_payments(self, f):
        paid_delegate = {}
        count = 1
        for k, v in self.delegate.items():
            # this is the reserve account
            if count == 1:
                # reserve account insuffient to pay fees
                if (v - f) <= 0:
                    print("Not enough to cover transaction fees in reserve")
                    print("Update interval and restart")
                    quit()
                # process donation
                elif self.config.donate == "Y":
                    donate_amt = int((self.config.donate_percent / 100) * v)
                    reserve_amt = v - donate_amt
                    print('Old Reserve Amount', v)
                    print('Donate Amount', donate_amt)
                    print('New Reserve Amount', reserve_amt)
                    quit()
                else:
                    pay_amount = v - f   
            else:
                pay_amount = v
            count += 1
            paid_delegate[k] = pay_amount
        print("Delegate Payments\n", paid_delegate)
        
        self.sql.open_connection()
        self.sql.update_delegate_paid_balance(paid_delegate)
        self.sql.stage_payment(paid_delegate, msg = "Reward")
        self.sql.close_connection()
    
    
    def stage_voter_payments(self):
        print("Voter Payments\n", self.voters)
        self.sql.open_connection()
        self.sql.update_voter_paid_balance(self.voters)
        self.sql.stage_payment(self.voters, msg = self.config.message)
        self.sql.close_connection()
