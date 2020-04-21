from web3 import Web3, HTTPProvider # , IPCProvider
import json
import time
import datetime as dt

# await web3.eth.getBlockNumber((e,r)=> web3.eth.getBlock(r, (e,r) => console.log(parseInt(r.hash)/57896044618658097711785492504343953926634992332820282019728792003956564819968)))
provider_ropsten = "https://ropsten.infura.io/v3/5f65182f06a14f5182a2e9af8d8fff33"
provider_local = "http://127.0.0.1:7545"
LOCAL=True
if LOCAL:
    provider = provider_local
else:
    provider = provider_ropsten
w3 = Web3(HTTPProvider(provider))

def dev_get_ith_last_block_and_hash(block_number=0):
    if block_number <= 0:
        block_number = w3.eth.blockNumber + block_number
    block_hash = w3.eth.getBlock(block_number).hash.hex()
    return block_number, block_hash, int(block_hash, 0)

last_block_number, _, _ = dev_get_ith_last_block_and_hash()
while True:
    try:
        block_number, block_hash, _ = dev_get_ith_last_block_and_hash()
    except:
        continue
    if last_block_number != block_number:
        if block_number - last_block_number > 1:
            for mid_block_bumber in range(last_block_number+1, block_number):
                block_number_, block_hash_, _ = dev_get_ith_last_block_and_hash(mid_block_bumber)
                print(f'{block_number_} | {block_hash_}')
        last_block_number = block_number
        print(f'{block_number} | {block_hash}')
    time.sleep(3)