#!/usr/bin/env python
from config.configure import Configure
from network.network import Network
# from modules.allocate import Allocate
# from modules.blocks import Blocks
# from modules.initialize import Initialize
# from modules.stage import Stage
# from modules.voters import Voters
# from utility.database import Database
#### BUILD EXCHANGE MODULE
from modules.exchange import Exchange
from modules.payments import Payments
from utility.dynamic import Dynamic
from utility.sql import Sql
from utility.utility import Utility

import time

if __name__ == '__main__':
    # set sql / config as global variables
    global config, sql, dynamic
    
    print("Start Script")
    # get configuration
    config = Configure()
    
    # load network
    network = Network(config.network)
    
    # load utility and dynamic
    utility = Utility(network)
    dynamic = Dynamic(utility, config)
    
    # connect to core and tbw script database
    sql = Sql()
    
    print(dynamic.get_tx_request_limit())
    quit()
    
    # MAIN FUNCTION LOOP SHOULD START HERE
    
    sql.open_connection()
    check = sql.unprocessed_staged_payments()
    sql.close_connection()
    
    if check > 0:
        # staged payments detected
        print("Staged Payments Detected.......Begin Payment Processing")
        payments = Payments(config, sql, dynamic, utility)
 
    print("End Script - Looping")
    time.sleep(600)
