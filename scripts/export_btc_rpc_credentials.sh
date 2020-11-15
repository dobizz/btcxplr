#!/usr/bin/env bash
echo Appending BTC_RPC_USER and BTC_RPC_PASS to /etc/environment
sudo echo BTC_RPC_USER=`cat ~/.bitcoin/bitcoin.conf | grep rpcuser | cut -d'=' -f2` >> /etc/environment
sudo echo BTC_RPC_PASS=`cat ~/.bitcoin/bitcoin.conf | grep rpcpassword | cut -d'=' -f2` >> /etc/environment