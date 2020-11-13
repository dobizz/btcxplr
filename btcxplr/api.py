#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime

RPC_USER = os.getenv("BTC_RPC_USER")    # rpcuser from bitcoin.conf
RPC_PASS = os.getenv("BTC_RPC_PASS")    # rpcpassword from bitcoin.conf
RPC_HOST = "127.0.0.1"                  # rpcbind from bitcoin.conf
RPC_PORT = 8332                         # rpcport from bitcoin.conf
RPC_URL = f"http://{RPC_USER}:{RPC_PASS}@{RPC_HOST}:{RPC_PORT}"

class RPC:

    def __init__(self, username, password, host, port):
        self.__url = f"http://{username}:{password}@{host}:{port}"
        print(f"Caching RPC connection to {host}:{port}")


    def __rpc__(self, method, params=[]):
        '''Sends formatted RPC to server and returns JSON reply'''
        command = {
            "method": method,
            "params": params,
        }
        data = json.dumps(command)
        reply = requests.post(RPC_URL, data=data, timeout=120)        
        return json.loads(reply.text) if reply.status_code == 200 else {}

    ### node related info ###
    def getconnectioncount(self):
        '''Returns the number of connections to other nodes'''
        method = "getconnectioncount"
        reply = self.__rpc__(method)
        return reply['result'] if reply else reply

    def getpeerinfo(self):
        '''Returns list of information about peer nodes'''
        method = "getpeerinfo"
        reply = self.__rpc__(method)
        return reply['result'] if reply else reply

    ### blockchain network related info ###
    def getmininginfo(self):
        method = "getmininginfo"
        reply = self.__rpc__(method)
        return reply['result'] if reply else reply

    def getblockchaininfo(self):
        method = "getblockchaininfo"
        reply = self.__rpc__(method)
        return reply['result'] if reply else reply

    def getdifficulty(self):
        '''Returns the proof-of-work difficulty as a multiple of the minimum difficulty'''
        method = "getdifficulty"
        reply = self.__rpc__(method)
        return reply['result'] if reply else reply

    def getbestblockhash(self):
        '''version 0.9 Returns the hash of the best (tip) block in the longest block chain.'''
        method = "getbestblockhash"
        reply = self.__rpc__(method)
        return reply['result'] if reply else reply

    ### derived methods ###
    def getblockchainsize(self):
        '''get size of current blockchain in Giga Bytes'''
        reply = self.getblockchaininfo()
        return round(reply['size_on_disk'] / 2**30, 2) if reply else reply

    def getblockcount(self):
        '''Returns the number of blocks in the longest block chain.'''
        method = "getblockcount"
        reply = self.__rpc__(method)
        return reply['result'] if reply else reply

    def getblockhash(self, block):
        '''Returns hash for specified block {0..N}'''
        method = "getblockhash"
        params = [block,]
        reply = self.__rpc__(method, params)
        return reply['result'] if reply else reply

    def getblock(self, blockhash, verbosity=1):
        '''
            Returns information about the block with the given hash
            If verbosity is 0, returns a string that is serialized, hex-encoded data for block 'hash'.
            If verbosity is 1, returns an Object with information about block <hash>.
            If verbosity is 2, returns an Object with information about block <hash> and information about each transaction. 
        '''
        method = "getblock"
        params = [blockhash, verbosity]
        reply = self.__rpc__(method, params)
        return reply['result'] if reply else reply

    def getblockstats(self, height):
        method = "getblockstats"
        params = [height]
        reply = self.__rpc__(method, params)
        return reply['result'] if reply else reply

    def getaddressinfo(self, address):
        '''Returns information about the given address'''
        method = "getaddressinfo"
        params = [address,]
        reply = self.__rpc__(method, params)
        return reply['result'] if reply else reply

    def getrawtransaction(self, txid, verbose=False, blockhash=None):
        '''Returns information about the transaction with the given txid'''
        method = "getrawtransaction"
        params = [txid, verbose]
        if blockhash:
            params.append(blockhash)
        reply = self.__rpc__(method, params)
        return reply['result'] if reply else reply

    def validateaddress(self, address):
        '''Returns information about the validity of the given address'''
        method = "validateaddress"
        params = [address]
        reply = self.__rpc__(method, params)
        return reply['result'] if reply else reply

    def gettxout(self, txid, n):
        '''Returns details about an unspent transaction output (UTXO)'''
        method = "gettxout"
        params = [txid, n,]
        reply = self.__rpc__(method, params)
        return reply['result'] if reply else reply


    ### memory pool methods ###
    def getmempoolinfo(self):
        '''Returns information about the memory pool'''
        method = "getmempoolinfo"
        reply = self.__rpc__(method)
        return reply['result'] if reply else reply

    def getrawmempool(self):
        '''Returns list of txids in memory pool'''
        method = "getrawmempool"
        reply = self.__rpc__(method)
        return reply['result'] if reply else reply

    def getmempoolentry(self, txid):
        '''Returns information about the given txid'''
        method = "getmempoolentry"
        params = [txid,]
        reply = self.__rpc__(method, params)
        return reply['result'] if reply else reply

    def getmempoolancestors(self, txid):
        '''Returns list containing mempool ancestors of the given txid'''
        method = "getmempoolancestors"
        params = [txid,]
        reply = self.__rpc__(method, params)
        return reply['result'] if reply else reply

    def getmempooldescendants(self, txid):
        '''Returns list containing mempool ancestors of the given txid'''
        method = "getmempooldescendants"
        params = [txid,]
        reply = self.__rpc__(method, params)
        return reply['result'] if reply else reply

    ### wallet methods ###
    def getwalletinfo(self):
        '''Returns information about wallet'''
        method = "getwalletinfo"
        reply = self.__rpc__(method)
        return reply['result'] if reply else reply

    def getballance(self):
        pass

    def getballances(self):
        pass

def get_coindesk_price(timestamp):
    '''Warning! Untested with multiple timezones'''
    datestr = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    url = f"https://api.coindesk.com/v1/bpi/historical/close.json?start={datestr}&end={datestr}"
    reply = requests.get(url)
    return round(json.loads(reply.text)['bpi'][datestr], 2)

if __name__ == "__main__":
    print('__main__')
    rpc = RPC(RPC_USER, RPC_PASS, RPC_HOST, RPC_PORT)
    # print('Get hashes for first 10 blocks')
    # for block in range(10):
    #     blockhash = rpc.getblockhash(block)
    #     info = rpc.getblock(blockhash, verbosity=2)
    #     print(blockhash, info, '\n')

    # print(rpc.getblockchaininfo())
    # print("Best Block Hash:", rpc.getbestblockhash())
    # print("Size on disk:", rpc.getblockchainsize(), "GB")
    height = rpc.getblockcount()
    print("Blockheight:", height, "Blocks")
    
    # print("Difficulty:", rpc.getdifficulty())
    # print(rpc.getaddressinfo('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'))
    # print(rpc.getmininginfo())

    # test node methods #
    # print("Connected Nodes:", rpc.getconnectioncount())
    # print("Peer Info:", rpc.getpeerinfo())

    # test mempool methods
    # print("<--- MEMORY POOL --->")
    # print(rpc.getmempoolinfo())
    # txids = rpc.getrawmempool()
    # print('mempoolsize:', len(txids))
    # print(txids)
    # print(rpc.getmempoolentry(txids[-1]))
    # print(rpc.getmempoolancestors(txids[-1]))
    # print(rpc.getmempooldescendants(txids[10]))

    #block_data = rpc.getblock('00000000000000000003a92ea8052ced7b3b96684138ed9d31e4f29c0a446286', 2)
    # print(rpc.getblockstats(656364))
    #print(block_data)
    # for block in range(height//1000):
    #     blockhash = rpc.getblockhash(block)

    # print(rpc.getrawtransaction('509a4eeca8d4ebc9225a72105e12d33a3c97b849c4db0542e5043863ef0e4c31'))
    # print(rpc.getrawtransaction('509a4eeca8d4ebc9225a72105e12d33a3c97b849c4db0542e5043863ef0e4c31', True))
    # print(rpc.getrawtransaction('509a4eeca8d4ebc9225a72105e12d33a3c97b849c4db0542e5043863ef0e4c31', True, '000000000000000000095dfb80713f9ec808814e1be32cdef765d37b1d17bfaa'))

    #print(rpc.gettxout('243b954477d6a34c64da875709979d88f594e5c33d66143da39b5b06c0651b9f', 1))