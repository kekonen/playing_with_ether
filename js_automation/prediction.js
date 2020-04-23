const Web3 = require('web3');
const EthereumTx = require('ethereumjs-tx').Transaction

const LOCAL = false
let GAS_PRICE = 0.8 * 1e9

let provider = null
let contract_address = null
let privateKey = null;

let abi = null 



if (LOCAL) {
    provider = "http://127.0.0.1:7545"
    contract_address = '0xC48D3849546EBb3a1252a1a9461AC2c620EE77e0'
    abi = require('../build/contracts/CoinFlip.json').abi
    privateKey = '0x618fd34a529886db15375bc6ae2ec683263446caf836d5fb717c9345fe859e69'
} else {
    provider = "wss://ropsten.infura.io/ws/v3/5f65182f06a14f5182a2e9af8d8fff33"//"https://ropsten.infura.io/v3/5f65182f06a14f5182a2e9af8d8fff33"
    contract_address = "0xC5d48f5D90Bb685BD567e82dcF99483C6999d6b3"
    abi = [{"constant":true,"inputs":[],"name":"consecutiveWins","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function","signature":"0xe6f334d7"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":false,"inputs":[{"name":"_guess","type":"bool"}],"name":"flip","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function","signature":"0x1d263f67"}]
    privateKey = '0x2F2C0F3E2F1CDF05D644104C7DE20A5C5642024308500954A92FE2BA83F49068'
}



const w3 = new Web3(provider); // 'ws://localhost:8546'

const c = new w3.eth.Contract(abi, contract_address);

const a = w3.eth.accounts.privateKeyToAccount(privateKey);





// (async () => {
//     GAS_PRICE = await w3.eth.getGasPrice()
//     console.log(await wins());
//     console.log('Account ->', a);
//     w3.eth.subscribe('newBlockHeaders', () => {
//         console.log('  NEW BLOCK! ')
//     });

//     await win_once()
//     // await flip(true).then(r => {console.log(r);});
// })()

(async () => {
    GAS_PRICE = await w3.eth.getGasPrice();
    console.log(await wins());
    console.log('Account :\n', a);
    let nonce = await w3.eth.getTransactionCount(a.address);

    // w3.eth.subscribe('newBlockHeaders', async () => {
    //     const w = await wins();
    //     console.log(`  NEW BLOCK! `);
    //     console.log('wins:', w);
    //     if (w >= 10) {
    //         w3.eth.clearSubscriptions()
    //         return 0
    //     } else {
    //         nonce ++;
    //         await win_once(nonce);
    //     }
    // });

    let max_collected = 0

    let w = await wins();

    while ( w < 10 ) {
        try {
            await win_once();
            w = await wins()
            if (w > max_collected) max_collected = w
            console.log(`(${(new Date()).toISOString()})   --   wins: ${w} | max: ${max_collected}|`)
        } catch(e) {
            console.log('Oooops, some error')
        }
    }
})()






function int2hex(v) {
    return '0x' + v.toString(16)
}

function hex2int(v) {
    return parseInt(v, 'hex')
}

function str2hex(v) {
    return '0x' + Buffer.from(v, 'utf8').toString('hex');
}






async function flip(side, options={}) {
    const gasLimit = 3000000;
    const data = c.methods.flip(side).encodeABI(); // abi encoded request to the contract

    const rawTransaction = {
        "nonce": options.nonce && options.nonce >= 0 ? options.nonce : int2hex(await w3.eth.getTransactionCount(a.address)),
        "gasPrice": int2hex(GAS_PRICE),
        "gasLimit": int2hex(gasLimit),
        "to": c._address,
        "value": "0x00",
        "data": data,
        // "chainId": 4 //change the chainID accordingly
    };

    // console.log(rawTransaction)

    const tx = new EthereumTx(rawTransaction, {'chain':'ropsten'});
    const privateKey = Buffer.from(a.privateKey.substr(2), 'hex') 
    tx.sign(privateKey);

    const serializedTx = tx.serialize();
    return w3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
    // .once('transactionHash', function(hash){ ... })
    // .once('receipt', function(receipt){ ... })
    // .on('confirmation', function(confNumber, receipt){ ... })
    // .on('error', function(error){ ... })
    // .then(function(receipt){
    //     // will be fired once the receipt is mined
    // });
}




async function wins() {
    return c.methods.consecutiveWins().call()
}

async function dev_get_ith_last_block_and_hash(block_number=0) {
    if (block_number <= 0) {
        block_number = await w3.eth.getBlockNumber() + block_number
    }
    const block_hash = (await w3.eth.getBlock(block_number)).hash
    return {block_number, block_hash, block_hash_uint: parseInt(block_hash, 0)}
}

async function get_last_block_hash_prediction(){
    const {block_hash_uint} = await dev_get_ith_last_block_and_hash(0)
    return (block_hash_uint/57896044618658097711785492504343953926634992332820282019728792003956564819968) >= 0
}

async function win_once(nonce=-1) {
    const decision = await get_last_block_hash_prediction()
    return flip(decision, {nonce})
}