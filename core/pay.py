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


def process_multi_payments(payment):
    print("Multi Payment")


def process_standard_payments(payment):
     print("Standard Payment")


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
      
    # connect to tbw script database and exchange module
    sql = Sql()
    exchange = Exchange(sql, config)
    
    # MAIN FUNCTION LOOP SHOULD START HERE
    
    sql.open_connection()
    check = sql.unprocessed_staged_payments()
    sql.close_connection()
    
    if check > 0:
        # staged payments detected
        print("Staged Payments Detected.......Begin Payment Processing")
        payments = Payments(config, sql, dynamic, utility)
        
        if config.multi == "Y":
            process_multi_payments(payments)
        else:
            process_standard_payments(payments)
 
    print("End Script - Looping")
    time.sleep(600)
