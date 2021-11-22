from utility.utility import Utility

class Voters():
    def __init__(self, config, sql):
        pass

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

    return roll


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
