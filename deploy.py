import os
from web3 import Web3
from solcx import compile_standard
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol") as file:
    simple_storage_file = file.read()


# Compile the contract
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

# Get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]


# Get ABI
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]


# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
my_address = os.getenv("MY_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")


# Create contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the lastest transaction
nonce = w3.eth.getTransactionCount(my_address)


# 1. Build a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)


# 2. Sign the transaction
signed_transaction = w3.eth.account.signTransaction(transaction, private_key)


# 3. Send the transaction
print("Deploying contract...")
tx_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
print("Deployed!")

# Working with Contract, you need:
# 1. Contract ABI
# 2. Contract Address
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Call -> Simulate making the call and getting the result value
# Transact -> Actually make a stage change

print(simple_storage.functions.retrive().call())

print("Updating contract...")
store_transaction = simple_storage.functions.store(52).buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
signed_store_txn = w3.eth.account.signTransaction(store_transaction, private_key)
send_store_txn = w3.eth.sendRawTransaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.waitForTransactionReceipt(send_store_txn)
print("Updated!")

print(simple_storage.functions.retrive().call())
