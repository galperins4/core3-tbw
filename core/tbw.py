#!/usr/bin/env python
from config.configure import Configure
from network.network import Network
from modules.allocate import Allocate
from modules.blocks import Blocks
from modules.initialize import Initialize
from modules.payments import Payments
from modules.stage import Stage
from modules.voters import Voters


if __name__ == '__main__':
    print("Start Processing")

    # get configuration
    config = Configure()
    print(config.atomic)
    print(config.network)
    print(config.delegate)
    
    #load network
    network = Network(config.network)
    print(network.epoch)
    print(network.version)
    print(network.wif)
    print(network.api)
    print(network.database)
    print(network.user)
    print(network.password)
    
    
    # check if initialized
    
    
    
    # process blocks
    
    
    
    # allocate block rewards
    
    
    
    # process payments
    print("End Processing")
