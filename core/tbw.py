#!/usr/bin/env python
from config.configure import Configure
from network.network import Network
from modules.allocate import Allocate
from modules.blocks import Blocks
from modules.initialize import Initialize
from modules.payments import Payments
from modules.stage import Stage
from modules.voters import Voters
from utility.database import Database
#from utility.sql import Sql
#from utility.utility import Utility


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
    
    
    
    # connect to database
    database = ArkDB(network.database, data.database_user, network.database_password, data.public_key)
    
    
    # process blocks
    
    
    
    # allocate block rewards
    
    
    
    # process payments
    print("End Processing")
