class Allocate:
    def __init__(self):
        pass

    
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

    print("Delegate Brohan reward: {}".format(delegate_block_reward)) 
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
