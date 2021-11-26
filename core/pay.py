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


def process_multi_payments(payment, unprocessed):
    print("Multi Payment")
    print(unprocessed)


def process_standard_payments(payment, unprocessed):
     print("Standard Payment")
     print(unprocessed)


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
        
        sql.open_connection()
        if config.multi == "Y":
            unprocessed = sql.get_staged_payment(multi=data.multi).fetchall()
            process_multi_payments(payments, unprocessed)
        else:
            unprocessed = sql.get_staged_payment(dynamic.get_tx_request_limit().fetchall())
            process_standard_payments(payments, unprocessed)
        sql.close_connection()
 
    print("End Script - Looping")
    time.sleep(600)
