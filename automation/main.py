from web3 import Web3, HTTPProvider # , IPCProvider
import json

w3 = Web3(HTTPProvider('http://localhost:7545'))
print(w3.eth.getBlock('latest'))

w3.eth.defaultAccount = w3.eth.accounts[0]
my_address = w3.eth.accounts[0]
friends_address = '0xDd26977F5A85e107aE931188EC8CBaDF0bb1c72b'

# Load contract ABI
contract_address = '0x82EC013431fDc135947fAD5471F33bF9ed648bdb' # will change depending on the network
contract_path = 'build/contracts/Coin.json'
with open(contract_path, 'rb') as f:
    cj = json.load(f)
    abi = cj['abi']


# Connect to contract
c = w3.eth.contract(contract_address, abi=abi)
my_balance = c.functions.balances(w3.eth.defaultAccount).call()

c.functions.send(friends_address, 3).transact()

my_new_balance = c.functions.balances(w3.eth.defaultAccount).call()
frineds_new_balance = c.functions.balances(friends_address).call()
print(f'frineds_new_balance: {frineds_new_balance},\nmy_new_balance: {my_new_balance}')

# Create contract
a = w3.eth.account.create()

# Send ether from main account to newly created
t = dict(
    nonce=w3.eth.getTransactionCount(w3.eth.defaultAccount),
    gasPrice = w3.eth.gasPrice, 
    gas = 100000,
    to=a.address,
    value=w3.toWei(10,'ether')
)
w3.eth.sendTransaction(t) # if that would be not hosted key: sendRawTransaction(  ... w3.eth.account.signTransaction().rawTransaction

# Print my currency for new address
c.functions.mint(a.address, 30000).transact()

# Set new address as working address 
w3.eth.defaultAccount = a.address

# Prepare transaction
transaction = c.functions.send(w3.eth.accounts[0], 1000).buildTransaction({
    'gasPrice': w3.toWei('1', 'gwei'),
    'nonce': w3.eth.getTransactionCount(a.address)
})
# Sign it and send
signed = a.sign_transaction(transaction)
w3.eth.sendRawTransaction(signed.rawTransaction)
