from web3 import Web3, HTTPProvider # , IPCProvider
import json
import time
import datetime as dt

# await web3.eth.getBlockNumber((e,r)=> web3.eth.getBlock(r, (e,r) => console.log(parseInt(r.hash)/57896044618658097711785492504343953926634992332820282019728792003956564819968)))

w3 = Web3(HTTPProvider("https://ropsten.infura.io/v3/5f65182f06a14f5182a2e9af8d8fff33"))

private_key = '2F2C0F3E2F1CDF05D644104C7DE20A5C5642024308500954A92FE2BA83F49068'
a = w3.eth.account.privateKeyToAccount(private_key)

w3.eth.defaultAccount = a.address

abi_json = """[{"constant":true,"inputs":[],"name":"consecutiveWins","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function","signature":"0xe6f334d7"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":false,"inputs":[{"name":"_guess","type":"bool"}],"name":"flip","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function","signature":"0x1d263f67"}]"""
abi = json.loads(abi_json)

c = w3.eth.contract(address=Web3.toChecksumAddress("0xC5d48f5D90Bb685BD567e82dcF99483C6999d6b3".lower()), abi=abi)

def flip(b):
    tx = c.functions.flip(b).buildTransaction({
        'nonce': w3.eth.getTransactionCount(a.address),
        'gasPrice': w3.toWei('0.0001', 'gwei'),
        'gas': 100000
    })

    signed_tx = a.signTransaction(tx)
    x=w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return x

def dump_json(fn, v):
    with open(fn, 'wb') as f:
        f.wrtie(json.dumps(v))

def wins():
    return c.functions.consecutiveWins().call()
print(wins())


def get_last_block_hash_prediction():
    last_block_hash = w3.eth.getBlock(w3.eth.blockNumber).hash
    return int(last_block_hash.hex(), 0)/57896044618658097711785492504343953926634992332820282019728792003956564819968

tx_hash = flip(get_last_block_hash_prediction() >= 1)

# c.functions.flip(get_last_block_hash_prediction() >= 1).call()

def get_tx_info(tx_hash):
    return w3.eth.getTransactionReceipt(tx_hash)

log_blocks = []
log_flips = []
# log_blocks = pd.DataFrame({"block": [], "h": []})
# log_flips = pd.DataFrame({"curr_block": [], "decision": []})

prev_block = 0
while True:
    time.sleep(5)
    block_number = w3.eth.blockNumber
    if prev_block != block_number:
        at = dt.datetime.now().isoformat()
        this_block_hash = w3.eth.getBlock(block_number).hash
        last_block_hash = w3.eth.getBlock(block_number - 1).hash

        decision = (int(last_block_hash.hex(), 0)/57896044618658097711785492504343953926634992332820282019728792003956564819968) >= 1

        tx = flip(decision)

        print(at, block_number, decision)

        log_flips[block_number] = {'tx': tx, 'decision': decision, 'at': at}

        log_blocks[block_number - 1] = last_block_hash
        log_blocks[block_number] = this_block_hash

        dump_json('log_blocks.json', log_blocks)
        dump_json('log_flips.json', log_flips)

        prev_block = block_number

        
    

