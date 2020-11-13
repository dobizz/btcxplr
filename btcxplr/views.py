#!/usr/bin/env python3
'''
This is where the routes are defined. It may be split into a package of its own (yourapp/views/) with related views grouped together into modules.
'''
from btcxplr import app, rpc
from btcxplr.api import RPC, RPC_USER, RPC_PASS, RPC_HOST, RPC_PORT, get_coindesk_price
from flask import render_template, redirect, url_for
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
        data = rpc.getmempoolentry(txid)
        if data:
            return render_template(
                'pooltx.html',
                data=data
            )
        else:
            return redirect(url_for('list_mempool'))
    else:
        pool = rpc.getrawmempool()
        return render_template(
            'pool.html',
            data=pool
        )

@app.route('/blk/<int:blockid>', methods=['GET', 'POST'])
def get_block(blockid):
    block_hash = rpc.getblockhash(blockid)
    block_data = rpc.getblock(block_hash)#, verbosity=2)
    block_data['miner'] = rpc.getrawtransaction(block_data['tx'][0], verbose=True)['vout'][0]['scriptPubKey']['addresses'][0]
    block_stats = rpc.getblockstats(blockid)
    return render_template(
        'block.html',
        data=block_data,
        stats=block_stats,
    )


@app.route('/txn/<string:txid>', methods=['GET', 'POST'])
def get_txn(txid):
    data = rpc.getrawtransaction(txid, verbose=True)
    data['height'] = rpc.getblock(data['blockhash'])['height']

    for n, txin in enumerate(data['vin']):
        try:
            txin_data = rpc.getrawtransaction(txin['txid'], verbose=True)
            data['vin'][n]['value'] =  txin_data['vout'][n]['value']
            # data['vin'][n]['address'] =  txin_data['vout'][n]['scriptPubKey']['addresses'][0]
            data['vin'][n]['scriptPubKey'] = txin_data['vout'][n]['scriptPubKey']
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