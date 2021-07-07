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
from utility.sql import Sql
from utility.utility import Utility


if __name__ == '__main__':
    print("Start Script")

    # get configuration
    config = Configure()
    
    #load network
    network = Network(config.network)
    
    #load utility
    utility = Utility(network)
    
    # connect to ark and tbw database
    database = Database(config, network)
    sql = Sql()
    
    # check if initialized
    Initialize(config, database, sql)
    
    # process blocks
    Blocks(config, database, sql)
    
    # allocate block rewards
    Allocate(config, sql)
    
    # stage payments
    Stage(config, sql)
    
    # process payment
    Payments(config, sql)
    
    
    print("End Script")
