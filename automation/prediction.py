from web3 import Web3, HTTPProvider # , IPCProvider
import json
import time
import datetime as dt
from hexbytes import HexBytes

# await web3.eth.getBlockNumber((e,r)=> web3.eth.getBlock(r, (e,r) => console.log(parseInt(r.hash)/57896044618658097711785492504343953926634992332820282019728792003956564819968)))
provider = None
contract_address = None
abi = None
a = None
LOCAL = False

if LOCAL:
    contract_address = '0xC48D3849546EBb3a1252a1a9461AC2c620EE77e0' # will change depending on the network
    contract_path = 'build/contracts/CoinFlip.json'
    with open(contract_path, 'rb') as f:
        cj = json.load(f)
        abi = cj['abi']
    provider = "http://127.0.0.1:7545"
else:
    contract_address = "0xC5d48f5D90Bb685BD567e82dcF99483C6999d6b3"
    abi_json = """[{"constant":true,"inputs":[],"name":"consecutiveWins","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function","signature":"0xe6f334d7"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":false,"inputs":[{"name":"_guess","type":"bool"}],"name":"flip","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function","signature":"0x1d263f67"}]"""
    abi = json.loads(abi_json)
    provider = "https://ropsten.infura.io/v3/5f65182f06a14f5182a2e9af8d8fff33"

w3 = Web3(HTTPProvider(provider))
c = w3.eth.contract(address=Web3.toChecksumAddress(contract_address.lower()), abi=abi)


if LOCAL:
    # a = w3.eth.accounts[0]
    private_key = '618fd34a529886db15375bc6ae2ec683263446caf836d5fb717c9345fe859e69'
    a = w3.eth.account.privateKeyToAccount(private_key)
    w3.eth.defaultAccount = a.address
else:
    private_key = '2F2C0F3E2F1CDF05D644104C7DE20A5C5642024308500954A92FE2BA83F49068'
    a = w3.eth.account.privateKeyToAccount(private_key)
    w3.eth.defaultAccount = a.address


def flip(b):
    tx = c.functions.flip(b).buildTransaction({
        'nonce': w3.eth.getTransactionCount(a.address), #, 'pending'
        'gasPrice': w3.toWei('0.0001', 'gwei'),
        'gas': 100000
    })

    signed_tx = a.signTransaction(tx)
    x = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print('TX!')
    return x

def dump_json(fn, v):
    with open(fn, 'w') as f:
        f.write(json.dumps(v))

def wins():
    return c.functions.consecutiveWins().call()
print(wins())

def dev_get_ith_last_block_and_hash(v=0):
    block_number = w3.eth.blockNumber + v
    block_hash = w3.eth.getBlock(w3.eth.blockNumber).hash.hex()
    return block_number, block_hash, int(block_hash, 0)

def get_last_block_hash_prediction():
    _, _, uint_hash = dev_get_ith_last_block_and_hash()
    # last_block_hash = w3.eth.getBlock(w3.eth.blockNumber).hash
    return uint_hash/57896044618658097711785492504343953926634992332820282019728792003956564819968


# tx_hash = flip(get_last_block_hash_prediction() >= 1)

# c.functions.flip(get_last_block_hash_prediction() >= 1).call()

def get_tx_info(tx_hash):
    return w3.eth.getTransactionReceipt(tx_hash)

def win_once():
    return flip(get_last_block_hash_prediction()>=1)


RUN = False
if RUN:
    log_blocks = {}
    log_flips = {}
    log_flips_past_flips = {}
    # log_blocks = pd.DataFrame({"block": [], "h": []})
    # log_flips = pd.DataFrame({"curr_block": [], "decision": []})

    last_tx = None
    last_wins = 0
    prev_block = 0
    while True:
        time.sleep(5)
        block_number = w3.eth.blockNumber
        if prev_block != block_number:
            wins_ = wins()
            print('wins:', wins_)
            try:
                at = dt.datetime.now().isoformat()
                this_block_hash = w3.eth.getBlock(block_number).hash
                last_block_hash = w3.eth.getBlock(block_number - 1).hash
            except:
                continue

            try:
                if last_tx:
                    get_tx_info(last_tx)
                decision = (int(this_block_hash.hex(), 0)/57896044618658097711785492504343953926634992332820282019728792003956564819968) >= 1
                print(at, block_number, decision)
                tx = flip(decision)
                log_flips_past_flips[last_tx] = wins_ - last_wins
                dump_json('log_flips_past_flips.json', log_flips_past_flips)

                last_tx = tx.hex()
                log_flips[block_number] = {'tx': tx.hex(), 'decision': decision, 'at': at}
                dump_json('log_flips.json', log_flips)
            except:
                pass



            log_blocks[block_number - 1] = last_block_hash.hex()
            log_blocks[block_number] = this_block_hash.hex()
            dump_json('log_blocks.json', log_blocks)

            prev_block = block_number
            last_wins = wins_

        
    

