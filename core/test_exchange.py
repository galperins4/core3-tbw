from config.configure import Configure
from network.network import Network
from modules.exchange import Exchange
from utility.sql import Sql
from utility.utility import Utility
import logging
import sys

if __name__ == '__main__':      
    # get configuration
    config = Configure()

    # set logging
    logger = logging.getLogger()
    logger.setLevel(config.loglevel)
    outlog = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(config.formatter)
    outlog.setFormatter(formatter)
    logger.addHandler(outlog)

    # start
    logger.info("Start Exchange Script")

    # load network
    network = Network(config.network)
    
    # load utility
    utility = Utility(network)
   
    # connect to tbw script database and exchange module
    sql = Sql()
    exchange = Exchange(sql, config)
    
    addresses = [i for i in config.convert_address]
    
    for i in addresses:
        amount = 50000000000
        if i in config.convert_address:
            index = config.convert_address.index(i)
            pay_in = exchange.exchange_select(index, i, amount, config.provider[index])
            
            # delete exchange record
            new_amount = exchange.truncate(amount/config.atomic,4)
            sql.open_connection()
            sql.delete_test_exchange(i,pay_in,new_amount)
            sql.close_connection()
