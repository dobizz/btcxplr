#!/usr/bin/env python3
'''
This is where the routes are defined. It may be split into a package of its own (yourapp/views/) with related views grouped together into modules.
'''
from btcxplr import app, rpc
from btcxplr.api import RPC, RPC_USER, RPC_PASS, RPC_HOST, RPC_PORT, get_coindesk_price
from flask import render_template, redirect, url_for, flash
from datetime import datetime



@app.route('/')
def index():
    peers = rpc.getpeerinfo()
    return render_template(
            'index.html',
            peers=peers
        )

@app.route('/node')
def get_nodeinfo():
    peers = rpc.getpeerinfo()
    return render_template(
            'node.html',
            peers=peers
        )

@app.route('/stats')
def get_stats():
    mining = rpc.getmininginfo()
    return render_template(
            'stats.html',
            data=mining
        )

@app.route('/pool', defaults={'txid': None})
@app.route('/pool/<string:txid>')
def list_mempool(txid):
    if txid:
        rtx = rpc.getrawtransaction(txid, verbose=True)
        confirmed = True if 'confirmations' in rtx else False
        # if block is mined
        if confirmed:
            flash('Transaction already in blockchain', 'primary')
            return redirect(url_for('get_txn', txid=txid))
            
        # if still in mempool
        else:
            data = rpc.getmempoolentry(txid)
            # if valid txid
            if data:
                return render_template(
                    'pooltx.html',
                    data=data, rtx=rtx
                )
            # flash warning and redirect if invalid txid
            else:
                flash('Invalid Transaction ID', 'warning')
                return redirect(url_for('list_mempool'))
    else:
        pool = rpc.getrawmempool()
        return render_template(
            'pool.html',
            data=pool
        )

@app.route('/blk/<int:blockid>', methods=['GET', 'POST'])
def get_block(blockid):
    blockchain_info = rpc.getblockchaininfo()

    # flash waring and redirect if blockid is less than genesis block or more than current block height 
    if blockid > blockchain_info['blocks'] or blockid < 0:
        flash('Invalid Block Height', 'warning')
        return redirect(url_for('get_stats'))

    block_hash = rpc.getblockhash(blockid)
    block_data = rpc.getblock(block_hash)#, verbosity=2)

    try:
        block_data['miner'] = rpc.getrawtransaction(block_data['tx'][0], verbose=True)['vout'][0]['scriptPubKey']['addresses'][0]
    except:
        block_data['miner'] = None

    try:
        block_stats = rpc.getblockstats(blockid)
    except:
        block_stats = {}

    return render_template(
        'block.html',
        data=block_data,
        stats=block_stats,
        info=blockchain_info,
    )


@app.route('/txn/<string:txid>', methods=['GET', 'POST'])
def get_txn(txid):
    # special case for genesis block
    if txid == '4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b':
        data=build_genesis_txn()

    else:
        data = rpc.getrawtransaction(txid, verbose=True)

    try:
        data['height'] = rpc.getblock(data['blockhash'])['height']
    except:
        data['height'] = None

    for n, txin in enumerate(data['vin']):
        try:
            txin_data = rpc.getrawtransaction(txin['txid'], verbose=True)
            data['vin'][n]['value'] =  txin_data['vout'][txin['vout']]['value']
            # data['vin'][n]['address'] =  txin_data['vout'][n]['scriptPubKey']['addresses'][0]
            data['vin'][n]['scriptPubKey'] = txin_data['vout'][txin['vout']]['scriptPubKey']
        except:
            data['vin'][n]['value'] = None
            data['vin'][n]['scriptPubKey'] = None

    for n, txout in enumerate(data['vout']):
        data['vout'][n]['spent'] = False if rpc.gettxout(txid, n) else True

    return render_template(
        'txn.html',
        data=data
    )


@app.route('/addr/<string:address>', methods=['GET', 'POST'])
def get_addr(address):
    raw_tx = rpc.getaddressinfo(address)
    return render_template(
        'index.html',
        data=raw_tx
    )

### Error Handlers ###
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))

### Templates ###
@app.template_filter('ctime')
def timectime(s):
    return datetime.fromtimestamp(s)

### Auxiliary Functions ###
def build_genesis_txn():
    genesis_block_hash = '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'
    block_data = rpc.getblock(genesis_block_hash, verbosity=2)

    # build txn data from genesis block data
    data = dict()
    data['txid'] = block_data['tx'][0]['txid']
    data['hash'] = block_data['tx'][0]['hash']
    data['version'] = block_data['tx'][0]['version']
    data['size'] = block_data['tx'][0]['size']
    data['version'] = block_data['tx'][0]['version']
    data['vsize'] = block_data['tx'][0]['vsize']
    data['weight'] = block_data['tx'][0]['weight']
    data['locktime'] = block_data['tx'][0]['locktime']
    data['vin'] = block_data['tx'][0]['vin']
    data['vout'] = block_data['tx'][0]['vout']
    data['hex'] = block_data['tx'][0]['hex']
    data['blockhash'] = block_data['hash']
    data['confirmations'] = block_data['confirmations']
    data['time'] = block_data['time']
    data['blocktime'] = block_data['time']

    return data