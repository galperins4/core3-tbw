#!/usr/bin/env python
from config.configure import Configure
from network.network import Network
from modules.exchange import Exchange
from modules.payments import Payments
from utility.dynamic import Dynamic
from utility.sql import Sql
from utility.utility import Utility
import time


def process_multi_payments(payment, unprocessed, dynamic):
    print("Multi Payment")
    print(unprocessed)
    
    signed_tx = []
    check = {}       
   
      
    # set max multipayment
    max_tx = dynamic.get_multipay_limit()
    # hard code multipay for test
    #max_tx = 6
    unprocessed_pay = snekdb.stagedArkPayment(multi=data.multi).fetchall()
    if len(unprocessed_pay) == 1:
        share()
    elif unprocessed_pay:
        temp_multi_chunk = list(chunks(unprocessed_pay, max_tx))
        # remove any items over tax_tx_limit
        multi_chunk = temp_multi_chunk[:max_tx_limit]
        nonce = int(get_nonce() + 1)
        for i in multi_chunk:
            if len(i) > 1:
                unique_rowid = [y[0] for y in i]
                tx = build_multi_transaction(i, str(nonce))
                check[tx['id']] = unique_rowid
                signed_tx.append(tx)
                nonce += 1        
        accepted = broadcast_multi(signed_tx)
        #check for accepted and non-accepted transactions
        for k,v in check.items():
            if k in accepted:
                # mark all accepted records complete
                snekdb.processStagedPayment(v)
            else:
                #delete all transaction records with relevant multipay txid
                snekdb.deleteTransactionRecord(k) 

        # payment run complete
        print('Payment Run Completed!')
        # sleep 3 minutes between tx blasts
        time.sleep(300)
    else:
        time.sleep(300)
    

def process_standard_payments(payment, unprocessed, dynamic, config, exchange):
    print("Standard Payment")
    signed_tx = []

    # process unpaid transactions
    unique_rowid = [y[0] for y in unprocessed]
    check = {}
    temp_nonce = payment.get_nonce()+1
    transaction_fee = dynamic.get_dynamic_fee()
        
    for i in unprocessed:
        # exchange processing
        if i[1] in config.convert_address and config.exchange == "Y":
            index = config.convert_address.index(i[1])
            pay_in = exchange.exchange_select(index, i[1], i[2], config.provider[index])
            tx = payment.build_transfer_transaction(pay_in, (i[2]), i[3], transaction_fee, config.passphrase, config.secondphrase, str(temp_nonce))
        # standard tx processing
        else:           
            tx = payment.build_transfer_transaction(i[1], (i[2]), i[3], transaction_fee, config.passphrase, config.secondphrase, str(temp_nonce))
        check[tx['id']] = i[0]
        signed_tx.append(tx)
        temp_nonce += 1
        # time.sleep(0.25)
                     
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
        payments = Payments(config, sql, dynamic, utility, exchange)
        
        sql.open_connection()
        if config.multi == "Y":
            unprocessed = sql.get_staged_payment(multi=config.multi).fetchall()
            sql.close_connection()
            process_multi_payments(payments, unprocessed, dynamic)
        else:
            unprocessed = sql.get_staged_payment(dynamic.get_tx_request_limit()).fetchall()
            sql.close_connection()
            process_standard_payments(payments, unprocessed, dynamic, config, exchange)
 
    print("End Script - Looping")
    time.sleep(600)
