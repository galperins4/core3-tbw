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
