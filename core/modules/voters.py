from utility.utility import Utility

class Voters():
    def __init__(self, config, sql):
        self.config = config
        self.sql = sql

    def process_whitelist(self, voter_balances):
        adjusted_voters = {}
        for k, v in voter_balances.items():
            if k in self.config.whitelist_address:
                adjusted_voters[k] = v
        
        return adjusted_voters

    
    def process_blacklist(self, voter_balances):
        adjusted_voters = {}
        for k, v in voter_balances.items():
            if k not in self.config.blacklist_address:
                adjusted_voters[k] = v
        
        return adjusted_voters
    
    
    def process_voter_cap(self, voter_balances):
        adjusted_voters = {}
        
        # no voter cap
        if self.config.voter_cap == 0:
            adjusted_voters = voter_balances
        else:
            # get max cap
            max_votes = int(self.config.voter_cap * self.config.atomic)
            for k, v in voter_balances.items():
                if v > max_votes:
                    adjusted_voters[k] = max_votes
                else:
                    adjusted_voters[k] = v
        
        return adjusted_voters
    
    
    def process_voter_min(self, voter_balances):
        adjusted_voters = {}
        
        # no minimum
        if self.config.voter_min == 0:
            adjusted_voters = voter_balances
        else:
            # get max cap
            min_votes = int(self.config.voter_min * self.config.atomic)
            for k, v in voter_balances.items():
                if v > min_votes:
                    adjusted_voters[k] = v
                else:
                    adjusted_voters[k] = 0
        
        return adjusted_voters
    
    
    def process_anti_dilution(self, voter_balances):
        adjusted_voters = {}
        
        self.sql.open_connection()
        dilute = self.sql.all_voters().fetchall()
        self.sql.close_connection()
        
        unpaid = {i[0]:i[2] for i in dilute}
        
        for k, v in voter_balances.items():
            adjusted_voters[k] = (v + unpaid[k])
        
        return adjusted_voters
