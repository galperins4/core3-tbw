from __init__ import __version__, __version_info__
from config.configure import Configure
from config.pool_config import PoolConfig
from network.network import Network
from utility.sql import Sql
from utility.utility import Utility
from flask import Flask, render_template
from functools import cmp_to_key
from multiprocessing import Process
from threading import Event
import datetime
import logging
import signal
import sys
import time

app = Flask(__name__)


def get_round(height):
    mod = divmod(height,network.delegates)
    return (mod[0] + int(mod[1] > 0))


def get_yield(netw_height, dblocks):
    drounds = dblocks['meta']['count'] #number of forged blocks 

    missed = 0
    forged = 0
    netw_round = get_round(netw_height)
    last_forged_round = get_round(dblocks['data'][0]['height'])

    if netw_round > last_forged_round + 1:
        missed += netw_round - last_forged_round - 1
    else:
        forged += 1

    if drounds > 1:
        for i in range(0, drounds - 1):
            cur_round = get_round(dblocks['data'][i]['height'])
            prev_round = get_round(dblocks['data'][i + 1]['height'])
            if prev_round < cur_round - 1:
                if cur_round - prev_round - 1 > drounds - missed - forged:
                    missed += drounds - missed - forged
                    break
                else:
                    missed += cur_round - prev_round - 1
            else:
                forged += 1

    yield_over_drounds = "{:.2f}".format(round((forged * 100)/(forged + missed)))
    return yield_over_drounds


@app.route('/')
def index():
    stats = {}
    ddata = client.delegates.get(config.delegate)

    stats['forged'] = ddata['data']['blocks']['produced']
    #s['missed'] = dstats['data']['blocks']['missed']
    #s['missed'] = 0 # temp fix
    stats['rank'] = ddata['data']['rank']
    #s['productivity'] = dstats['data']['production']['productivity']
    #s['productivity'] = 100 # temp fix
    stats['handle'] = ddata['data']['username']
    stats['wallet'] = ddata['data']['address']
    stats['votes'] = "{:.2f}".format(int(ddata['data']['votesReceived']['votes'])/config.atomic)
    stats['rewards'] = ddata['data']['forged']['total']
    stats['approval'] = ddata['data']['votesReceived']['percent']

    # get all forged blocks in reverse chronological order, first page, max 100 as default
    dblocks = client.delegates.blocks(config.delegate) 
    stats['lastforged_no'] = dblocks['data'][0]['height']
    stats['lastforged_id'] = dblocks['data'][0]['id']
    stats['lastforged_ts'] = dblocks['data'][0]['timestamp']['human']
    stats['lastforged_unix'] = dblocks['data'][0]['timestamp']['unix']
    age = divmod(int(time.time() - stats['lastforged_unix']), 60)
    stats['lastforged_ago'] = "{0}:{1}".format(age[0],age[1])
    stats['forging'] = 'Forging' if stats['rank'] <= network.delegates else 'Standby'

    sql.open_connection()
    voters = sql.all_voters().fetchall()
    sql.close_connection()

    voter_stats = []
    pend_total = 0
    paid_total = 0
    ld          = dict((addr,(pend,paid)) for addr, pubkey, pend, paid, rate in voters)
    votetotal   = int(ddata['data']['votesReceived']['votes'])
    vdata  = client.delegates.voters(config.delegate)
    for _data in vdata['data']:
        if _data['address'] in ld:
            _sply = "{:.2f}".format(int(_data['balance'])*100/votetotal) if votetotal > 0 else "-"
            _addr = _data['address']
            voter_stats.append([_addr,ld[_addr][0], ld[_addr][1], _sply])
            pend_total += ld[_addr][0]
            paid_total += ld[_addr][1]

    reverse_key = cmp_to_key(lambda a, b: (a < b) - (a > b))
    voter_stats.sort(key=lambda rows: (reverse_key(rows[3]),rows[0]))
    voter_stats.insert(0,["Total",pend_total, paid_total, "100"])

    stats['voters'] = vdata['meta']['totalCount']

    node_sync_data = client.node.syncing()
    stats['synced'] = 'Syncing' if node_sync_data['data']['syncing'] else 'Synced'
    stats['behind'] = node_sync_data['data']['blocks']
    stats['height'] = node_sync_data['data']['height']

    stats['yield'] = get_yield(stats['height'], dblocks)

    return render_template(poolconfig.pool_template + '_index.html', node=stats, voter=voter_stats, tags=tags)


@app.route('/payments')
def payments():
    sql.open_connection()
    xactions = sql.transactions().fetchall()
    sql.close_connection()

    tx_data = []
    for i in xactions:
        data_list = [i[0], int(i[1]), i[2], i[3]]
        tx_data.append(data_list)

    return render_template(poolconfig.pool_template + '_payments.html', tx_data=tx_data, tags=tags)


# Handler for SIGINT and SIGTERM
def sighandler(signum, frame):
    global server
    logger.info("SIGNAL {0} received. Starting graceful shutdown".format(signum))
    server.kill()
    logger.info("< Terminating POOL...")
    return


if __name__ == '__main__':    
    # get configuration
    config = Configure()
    if (config.error):
        print("FATAL: config.ini not found! Terminating POOL.", file=sys.stderr)
        sys.exit(1)

    poolconfig = PoolConfig()
    if (poolconfig.error):
        print("FATAL: pool_config.ini not found! Terminating POOL.", file=sys.stderr)
        sys.exit(1)

    # set logging
    logger = logging.getLogger()
    logger.setLevel(config.loglevel)
    outlog = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(config.formatter)
    outlog.setFormatter(formatter)
    logger.addHandler(outlog)

    # start script
    msg='> Starting POOL script %s @ %s' % (__version__, str(datetime.datetime.now()))
    logger.info(msg)

    # subscribe to signals
    killsig = Event()
    signal.signal(signal.SIGINT, sighandler)
    signal.signal(signal.SIGTERM, sighandler)

    # load network
    network = Network(config.network)
    
    # load utility and client
    utility = Utility(network)
    client = utility.get_client()

    # connect to tbw script database
    sql = Sql()

    tags = {
       'dname': config.delegate,
       'proposal1': poolconfig.proposal1,
       'proposal2': poolconfig.proposal2,
       'proposal2_lang': poolconfig.proposal2_lang,
       'explorer': poolconfig.explorer,
       'coin': poolconfig.coin}

    #app.run(host=data.pool_ip, port=data.pool_port)
    server = Process(target=app.run, args=(poolconfig.pool_ip, poolconfig.pool_port))
    server.start()
