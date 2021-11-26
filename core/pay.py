#!/usr/bin/env python
from config.configure import Configure
from network.network import Network
from modules.exchange import Exchange
from modules.payments import Payments
from utility.dynamic import Dynamic
from utility.sql import Sql
from utility.utility import Utility
import time


def process_multi_payments(payment, unprocessed):
    print("Multi Payment")
    print(unprocessed)
    

def process_standard_payments(payment, unprocessed, dynamic, config, exchange):
    print("Standard Payment")
    print(unprocessed)
    signed_tx = []

    # process unpaid transactions
    unique_rowid = [y[0] for y in unprocessed]
    check = {}
    temp_nonce = payment.get_nonce()+1
    transaction_fee = dynamic.get_dynamic_fee()
        
    for i in unprocessed_pay:
        # exchange processing
        if i[1] in config.convert_address and config.exchange == "Y":
            index = config.convert_address.index(i[1])
            pay_in = exchange.exchange_select(index, i[1], i[2], config.provider[index])
            tx = build_transfer_transaction(pay_in, (i[2]), i[3], transaction_fee, config.passphrase, config.secondphrase, str(temp_nonce))
        # standard tx processing
        else:           
            tx = build_transfer_transaction(i[1], (i[2]), i[3], transaction_fee, config.passphrase, config.secondphrase, str(temp_nonce))
        check[tx['id']] = i[0]
        signed_tx.append(tx)
        temp_nonce+=1
        time.sleep(0.25)
                     
    print(signed_tx)
    quit()
    accepted = broadcast(signed_tx)
    for_removal = non_accept_check(check, accepted)
            
    # remove non-accepted transactions from being marked as completed
    if len(for_removal) > 0:
        for i in for_removal:
            print("Removing RowId: ", i)
            unique_rowid.remove(i)
                    
    snekdb.processStagedPayment(unique_rowid)

    # payment run complete
    print('Payment Run Completed!')


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
            unprocessed = sql.get_staged_payment(multi=config.multi).fetchall()
            process_multi_payments(payments, unprocessed)
        else:
            unprocessed = sql.get_staged_payment(dynamic.get_tx_request_limit()).fetchall()
            process_standard_payments(payments, unprocessed, dynamic, config, exchange)
        sql.close_connection()
 
    print("End Script - Looping")
    time.sleep(600)
