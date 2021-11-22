from crypto.identity.address import address_from_public_key


class Allocate:
    def __init__(self, database, config, sql):
        self.database = database
        self.config = config
        self.sql = sql

        
    def get_vote_transactions(self, timestamp):
        self.database.open_connection()
        vote, unvote = self.database.get_votes(timestamp)
        self.database.close_connection()
        return vote, unvote    

    
    def create_voter_roll(self, v, u):
        #create dictionary of unvotes
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
            self.sql.store_voters(roll)
            self.sql.close_connection()

        return roll
    
       
    def get_block_allocations(self, block, voters):
        rewards_check = 0
        voter_check = 0
        delegate_check = 0

        # get total votes
        total_delegate_vote_balance = sum(voters.values())

        # get block reward
        block_reward = block[2]
        fee_reward = block[3]
        total_reward = block_reward+fee_reward

        delegate_share = 0.25
        voter_share = 0.75

        voter_block_share = block_reward * voter_share
        delegate_block_reward = int((block_reward * delegate_share) + fee_reward)
        delegate_check += delegate_block_reward

        print("Delegate {} reward: {}".format(delegate_block_reward)) 
        for k, v in voters.items():
            share_weight = v / total_delegate_vote_balance
            single_voter_reward = int(share_weight * voter_block_share)
            voter_check += 1
            rewards_check += single_voter_reward
            print("Voter {} with balance of {} reward: {}".format(k, v, single_voter_reward))


        print(f"""\nProcessed Block: {block[4]}\n
        Voters processed: {voter_check}
        Total Approval: {total_delegate_vote_balance}
        Voters Rewards: {rewards_check}
        Delegate Reward: {delegate_check}
        Voter + Delegate Rewards: {rewards_check + delegate_check}
        Total Block Rewards: {total_reward}""")

    
    


    def get_voter_balance(self, block):
        vote_balance = {}
        block_timestamp = block[1]
        vote_tx, unvote_tx = get_votes(delegate, block_timestamp)
        voter_roll = create_voter_roll(vote_tx, unvote_tx)
    
        print("Current Voters: ", len(voter_roll))
        print("As of block id: ", block[0])
        print("Delegate public key: ", delegate)

        for i in voter_roll:
            # print(i)
            debit = get_sum_outbound(i[1], block_timestamp)
            credit = get_sum_inbound(i[0], block_timestamp)
            balance = credit - debit
            vote_balance[i[0]] = balance

        print("Block Reward: ", block[2])
        print("Block Fees: ", block[3])
        print("Total Allocation: ", block[2]+block[3])
        print("Total Voter Balances: ", sum(vote_balance.values()), "\n")
        return vote_balance
