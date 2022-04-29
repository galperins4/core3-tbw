#!/usr/bin/env python
from config.configure import Configure
from network.network import Network
from modules.exchange import Exchange
from modules.payments import Payments
from utility.dynamic import Dynamic
from utility.sql import Sql
from utility.utility import Utility
import time


def chunks(l, n):
    # For item i in a range that is a length of l
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


def process_multi_payments(payment, unprocessed, dynamic, config, exchange, sql):
    print("Multi Payment")
    signed_tx = []
    check = {} 
    request_limit = dynamic.get_tx_request_limit()
    multi_limit = dynamic.get_multipay_limit()
   
    if len(unprocessed) == 1:
        process_standard_payments(payments, unprocessed, dynamic, config, exchange, sql)
    else:
        temp_multi_chunk = list(chunks(unprocessed, multi_limit))
        # remove any items over request_tx_limit
        multi_chunk = temp_multi_chunk[:request_limit]
        nonce = payment.get_nonce() + 1
        
        for i in multi_chunk:
            if len(i) > 1:
                unique_rowid = [y[0] for y in i]
                tx = payment.build_multi_transaction(i, str(nonce))
                check[tx['id']] = unique_rowid
                signed_tx.append(tx)
                nonce += 1        
        
        accepted = payment.broadcast_multi(signed_tx)
        
        #check for accepted and non-accepted transactions
        for k, v in check.items():
            if k in accepted:
                # mark all accepted records complete
                sql.open_connection()
                sql.process_staged_payment(v)
                sql.close_connection()
            else:
                # delete all transaction records with relevant multipay txid
                print("Transaction ID Not Accepted")
                sql.open_connection()
                sql.delete_transaction_record(k)
                sql.close_connection()

        # payment run complete
        print('Payment Run Completed!')
    

def process_standard_payments(payment, unprocessed, dynamic, config, exchange, sql):
    print("Standard Payment")
    signed_tx = []
    check = {}

    # process unpaid transactions
    unique_rowid = [y[0] for y in unprocessed]

    temp_nonce = payment.get_nonce()+1
    transaction_fee = dynamic.get_dynamic_fee()
        
    for i in unprocessed:
        # exchange processing
        if i[1] in config.convert_address and config.exchange == "Y":
            index = config.convert_address.index(i[1])
            pay_in = exchange.exchange_select(index, i[1], i[2], config.provider[index])
            tx = payment.build_transfer_transaction(pay_in, (i[2]), i[3], transaction_fee, str(temp_nonce))
        # standard tx processing
        else:           
            tx = payment.build_transfer_transaction(i[1], (i[2]), i[3], transaction_fee, str(temp_nonce))
        check[tx['id']] = i[0]
        signed_tx.append(tx)
        temp_nonce += 1    
                     
    accepted = payment.broadcast_standard(signed_tx)
    for_removal = payment.non_accept_check(check, accepted)
            
    # remove non-accepted transactions from being marked as completed
    if len(for_removal) > 0:
        for i in for_removal:
            print("Removing RowId: ", i)
            unique_rowid.remove(i)
                    
    sql.open_connection()
    sql.process_staged_payment(unique_rowid)
    sql.close_connection()

    # payment run complete
    print('Payment Run Completed!')


if __name__ == '__main__':    
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
    while True:
        sql.open_connection()
        check = sql.unprocessed_staged_payments()
        sql.close_connection()
    
        if check > 0:
            # staged payments detected
            print("Staged Payments Detected.......Begin Payment Processing")
            payments = Payments(config, sql, dynamic, utility, exchange)
        
            sql.open_connection()
            if config.multi == "Y":
                unprocessed = sql.get_staged_payment(multi=config.multi).fetchall()
                sql.close_connection()
                process_multi_payments(payments, unprocessed, dynamic, config, exchange, sql)
            else:
                unprocessed = sql.get_staged_payment(dynamic.get_tx_request_limit()).fetchall()
                sql.close_connection()
                process_standard_payments(payments, unprocessed, dynamic, config, exchange, sql)
 
        print("End Script - Looping")
        time.sleep(1200)
