from crypto.identity.address import address_from_public_key
import logging

class Allocate:
    def __init__(self, database, config, sql):
        self.logger = logging.getLogger(__name__)
        self.database = database
        self.config = config
        self.sql = sql
        self.atomic = self.config.atomic

        
    def get_vote_transactions(self, timestamp):
        self.database.open_connection()
        vote, unvote = self.database.get_votes(timestamp)
        self.database.close_connection()
        return vote, unvote    

    
    def create_voter_roll(self, v, u):
        # create dictionary of unvotes
        unvotes = {i[0]:i[1] for i in u}

        roll = []

        for i in v:
            address = i[0]
            val = [address_from_public_key(address), address]
            if address in unvotes.keys():
                vote_ts = i[1]
                unvote_ts =  unvotes[address]

                # check to see if unvote is prior to vote
                if vote_ts > unvote_ts:
                    roll.append(val)
            else:
                roll.append(val)
                
        # add voters to database
        self.sql.open_connection()
        self.sql.store_voters(roll, self.config.voter_share)
        self.sql.close_connection()

        return roll
    
       
    def get_voter_balance(self, block, voter_roll):
        vote_balance = {}
        block_timestamp = block[1]

        self.database.open_connection()
        self.sql.open_connection()
        for i in voter_roll:
            voter_balance_checkpoint = self.sql.get_voter_balance_checkpoint(i[0]).fetchall()
            if voter_balance_checkpoint:
                # Already voter
                # Recheck transactions between chkpoint_ts and current block_timestamp
                # Get checkpoint balance and add it to the transactions
                chkpoint_ts = voter_balance_checkpoint[0][2]
                chkpoint_balance = voter_balance_checkpoint[0][1]
            else:
                # New voter, recheck all previous transactions
                chkpoint_ts = 0
                chkpoint_balance = 0
            debit = self.database.get_sum_outbound(i[1], block_timestamp, chkpoint_ts)
            credit = self.database.get_sum_inbound(i[0], block_timestamp, chkpoint_ts)
            block_reward = self.database.get_sum_block_rewards(i[1], block_timestamp, chkpoint_ts)
            balance = chkpoint_balance + credit + block_reward - debit
            vote_balance[i[0]] = balance

        # Store voter balance with given block_timestamp
        self.sql.update_voter_balance_checkpoint(vote_balance, block_timestamp)

        self.database.close_connection()
        self.sql.close_connection()

        return vote_balance

        
    def block_allocations(self, block, voters):
        self.logger.info("")
        rewards_check = 0
        voter_check = 0
        delegate_check = 0
        delegate_unpaid = {}
        voter_unpaid = {}

        # get total votes
        total_delegate_vote_balance = sum(voters.values())

        # get block reward
        block_reward = block[2] - block[7]
        fee_reward = block[3] - block[5]
        total_reward = block_reward+fee_reward
        
        # process delegate reward
        for count, i in enumerate(self.config.delegate_fee):
            # check if count is 0 for reserve account
            if count == 0:
                rate = float(i) / 100
                reward = int((rate * block_reward) + fee_reward)
                delegate_check += reward
                delegate_unpaid[self.config.delegate_fee_address[count]] = reward
            else:
                rate = float(i) / 100
                reward = int(rate * block_reward)
                delegate_check += reward
                delegate_unpaid[self.config.delegate_fee_address[count]] = reward
        
        # process voter reward
        config_voter_share = self.config.voter_share
        self.sql.open_connection()
        for k, v in voters.items():
            # check to make sure to skip 0 balances
            if v > 0:
                # get voter_weight
                share_weight = v / total_delegate_vote_balance
                # get voter share
                db_share = self.sql.get_voter_share(k).fetchall()[0][0]
                if db_share == config_voter_share:
                    # standard share rate
                    voter_block_share = (db_share / 100) * block_reward
                    single_voter_reward = int(share_weight * voter_block_share)        
                else:
                    # custom share rate
                    custom_block_share = (db_share / 100) * block_reward
                    standard_voter_share = (config_voter_share / 100) * block_reward
                    single_voter_reward = int(share_weight * custom_block_share)
                    remainder = int(share_weight * standard_voter_share) - single_voter_reward
                    delegate_check += remainder
                    delegate_unpaid[self.config.delegate_fee_address[0]] += remainder
            else:
                single_voter_reward = 0
           
            voter_check += 1
            rewards_check += single_voter_reward
            self.logger.debug("Voter {} with balance of {} reward: {}".format(k, (v / self.atomic), (single_voter_reward / self.atomic)))
            voter_unpaid[k] = single_voter_reward
        
        for k , v in delegate_unpaid.items():
            self.logger.debug("Delegate {} account reward: {}".format(k, (v / self.atomic)))
        
        # get original voter approval balance (without dilution adjustment)
        res = self.sql.get_all_voters_balance_checkpoint().fetchall()
        og_voter_approval = sum(i[0] for i in res)
        self.sql.close_connection()
        
                          
        self.logger.info(f"Processed Block: {block[4]}")
        self.logger.info(f"\tVoters processed: {voter_check}")
        self.logger.info(f"\tTotal Approval Original: {og_voter_approval / self.atomic}")
        self.logger.info(f"\tTotal Approval (Dilution Adjusted): {total_delegate_vote_balance / self.atomic}")
        self.logger.info(f"\tVoters Rewards: {rewards_check / self.atomic}")
        self.logger.info(f"\tDelegate Reward: {delegate_check / self.atomic}")
        self.logger.info(f"\tVoter + Delegate Rewards: {(rewards_check + delegate_check) / self.atomic}")
        self.logger.info(f"\tTotal Block Rewards: {total_reward / self.atomic}")
        # store delegate/voter rewards and mark block as processed mark block as processed
        self.sql.open_connection()
        self.sql.update_delegate_balance(delegate_unpaid)
        self.sql.update_voter_balance(voter_unpaid)
        self.sql.mark_processed(block[4])
        self.sql.close_connection()
