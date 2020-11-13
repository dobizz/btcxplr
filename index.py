#!/usr/bin/env python3

# from btcxplr.api import RPC, RPC_USER, RPC_PASS, RPC_HOST, RPC_PORT
from btcxplr import rpc

genesis_block_hash = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"

print(rpc.getblock(genesis_block_hash, 2))