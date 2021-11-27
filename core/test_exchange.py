from config.configure import Configure
from network.network import Network
from modules.exchange import Exchange
from utility.sql import Sql
from utility.utility import Utility

if __name__ == '__main__':      
    print("Start Script")
    # get configuration
    config = Configure()
    
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
