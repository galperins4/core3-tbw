#!/usr/bin/env python
from __init__ import __version__, __version_info__
from config.configure import Configure
from network.network import Network
from modules.allocate import Allocate
from modules.blocks import Blocks
from modules.initialize import Initialize
from modules.stage import Stage
from modules.voters import Voters
from utility.database import Database
from utility.dynamic import Dynamic
from utility.sql import Sql
from utility.utility import Utility
from threading import Event
import time
import datetime
import logging
import signal
import sys

def update_voter_share(sql, config):
    old_rate = float(input("Enter old share rate in the following format (80): "))
    sql.open_connection()
    voters = sql.all_voters().fetchall()
    
    for i in voters:
        if i[4] == old_rate:
            sql.update_voter_share(i[0], config.voter_share)

    sql.close_connection()
    logger.info("Share rate updated")
    quit()


def update_custom_share(sql):
    address = input("Enter address to update with custom rate: ")
    new_rate = float(input("Enter custom share rate in the following format (80): "))
    sql.open_connection()
    sql.update_voter_share(address, new_rate)
    sql.close_connection()
    logger.info("Address {} updated with custom rate of: {}".format(address, new_rate))
    quit()


def force_manual_pay(config, dynamic, sql):
    # set fake block_count
    block_count = 1
    stage, unpaid_voters, unpaid_delegate = interval_check(block_count, config.interval, config.manual_pay)
        
    # check if true to stage payments
    if stage == True and sum(unpaid_voters.values()) > 0:
        logger.info(" Staging payments")
        s = Stage(config, dynamic, sql, unpaid_voters, unpaid_delegate)
    quit()


def interval_check(block_count, interval, manual = "N"):
    if block_count % interval == 0 or manual == "Y":
        logger.info(" Payout interval reached")
        sql.open_connection()
        voter_balances = sql.voters().fetchall()
        delegate_balances = sql.rewards().fetchall()
        sql.close_connection()
        
        voter_unpaid = {i[0]:i[2] for i in voter_balances}
        delegate_unpaid = {i[0]:i[1] for i in delegate_balances}
        
        # check if there is a positive unpaid balance
        if sum(voter_unpaid.values()) > 0:
            stage = True
        else:
            stage = False
    else:
        stage = False
        voter_unpaid = {}
        delegate_unpaid = {}
    
    return stage, voter_unpaid, delegate_unpaid

# Handler for SIGINT and SIGTERM
def sighandler(signum, frame):
    logger.info("SIGNAL {0} received. Starting graceful shutdown".format(signum))
    killsig.set()
    return

if __name__ == '__main__':
    # get configuration
    config = Configure()
    if (config.error):
        print("FATAL: config file not found! Terminating TBW.", file=sys.stderr)
        sys.exit(1)

    # set logging 
    logger = logging.getLogger()
    logger.setLevel(config.loglevel)
    outlog = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(config.formatter)
    outlog.setFormatter(formatter)
    logger.addHandler(outlog)

    # start
    msg='> Starting TBW script %s @ %s' % (__version__, str(datetime.datetime.now()))
    logger.info(msg)

    # subscribe to signals
    killsig = Event()
    signal.signal(signal.SIGINT, sighandler)
    signal.signal(signal.SIGTERM, sighandler)

    # load network
    network = Network(config.network)

    # load utility and dynamic
    utility = Utility(network)
    dynamic = Dynamic(utility, config)
    
    # connect to core and tbw script database
    database = Database(config, network)
    sql = Sql()
    
    # get multivote activation timestamp for use
    database.open_connection()
    multi_activation_ts = database.get_block_timestamp(network.multi_activation)[0][0]
    database.close_connection()

    # check if initialized
    Initialize(config, database, sql)
    
    # update all voter share
    if config.update_share == "Y":
        update_voter_share(sql, config)
    
    if len(sys.argv) != 1:
        config.manual_pay = "Y"
    
    # check if manual pay flag is set
    if config.manual_pay == "Y":
        force_manual_pay(config, dynamic, sql)

    # check if custom share flag is set
    if config.custom == "Y":
        update_custom_share(sql)
    
    # MAIN FUNCTION LOOP SHOULD START HERE
    while True:
        # get blocks
        block = Blocks(config, database, sql)
    
        # get last block to start
        last_block = block.get_last_block()
        logger.info(f"Last Block Height Retrieved: {last_block[0][1]}")
    
        # use last block timestamp to get all new blocks
        new_blocks = block.get_new_blocks(last_block)
    
        # store all new blocks
        block.store_new_blocks(new_blocks)
    
        # get unprocessed blocks
        unprocessed_blocks = block.return_unprocessed_blocks()
    
        # allocate block rewards
        allocate = Allocate(database, config, sql, multi_activation_ts)
        voter_options = Voters(config, sql)
    
        for unprocessed in unprocessed_blocks:
            logger.info("--- Processing new block...")
            tic_a = time.perf_counter()
            logger.debug(f"Unprocessed Block Information: {unprocessed}")
            block_timestamp = unprocessed[1]
            # get vote and unvote transactions
            vote, unvote = allocate.get_vote_transactions(block_timestamp)
            tic_b = time.perf_counter()
            logger.debug(f"Get all Vote and Unvote transactions in {tic_b - tic_a:0.4f} seconds")
            # create voter_roll
            voter_roll = allocate.create_voter_roll(vote, unvote, block_timestamp)
            tic_c = time.perf_counter()
            logger.debug(f"Create voter rolls in {tic_c - tic_b:0.4f} seconds")
            # get voter_balances
            voter_balances = allocate.get_voter_balance(unprocessed, voter_roll)
            tic_d = time.perf_counter()
            logger.debug(f"Get all voter balances in {tic_d - tic_c:0.4f} seconds")
            logger.debug("")
            logger.debug("original voter_balances")
            for k, v in voter_balances.items():
                logger.debug(f"{k} {v / config.atomic}")
            # run voters through various vote_options
            if config.whitelist == 'Y':
                voter_balances = voter_options.process_whitelist(voter_balances)
            if config.whitelist == 'N' and config.blacklist =='Y':
                voter_balances = voter_options.process_blacklist(voter_balances)
            logger.debug("")
            logger.debug("voter_balances post whitelist or blacklist")
            for k, v in voter_balances.items():
                logger.debug(f"{k} {v / config.atomic}")
            
            voter_balances = voter_options.process_voter_cap(voter_balances)
            logger.debug("")
            logger.debug("voter_balances post voter cap")
            for k, v in voter_balances.items():
                logger.debug(f"{k} {v / config.atomic}")
 
            voter_balances = voter_options.process_voter_min(voter_balances)
            logger.debug("")
            logger.debug("voter_balances post voter min")
            for k, v in voter_balances.items():
                logger.debug(f"{k} {v / config.atomic}")
 
            voter_balances = voter_options.process_anti_dilution(voter_balances)
            logger.debug("")
            logger.debug("voter_balances post anti_dulite")
            for k, v in voter_balances.items():
                logger.debug(f"{k} {v / config.atomic}")
        
            tic_e = time.perf_counter()
            logger.debug(f"Process all voter options in {tic_e - tic_d:0.4f} seconds")
            # allocate block rewards
            allocate.block_allocations(unprocessed, voter_balances)
            tic_f = time.perf_counter()
            logger.debug(f"Allocate block rewards in {tic_f - tic_e:0.4f} seconds")
            # get block count
            block_count = block.block_counter()
            logger.info(f"\n Current block count : {block_count}")
            
            tic_g = time.perf_counter()
            logger.debug(f"Processed block in {tic_g - tic_a:0.4f} seconds")
        
            # check interval for payout
            stage, unpaid_voters, unpaid_delegate = interval_check(block_count, config.interval)
            if config.fix_interval == 'Y':
                stage = False
        
            # check if true to stage payments
            if stage == True and sum(unpaid_voters.values()) > 0:
                logger.info(" Staging payments")
                s = Stage(config, dynamic, sql, unpaid_voters, unpaid_delegate)
        
            # pause betweeen blocks
 
        logger.info("End Script - Looping")
        logger.info("")
        killsig.wait(1200)
        if killsig.is_set():
            logger.debug("Kill switch set. Breaking the main loop.")
            break
    
    logger.info("< Terminating TBW script.")
