from web3 import Web3
import solcx

solcx.install_solc()

# Ethereum node (replace with your own node URL)
ethereum_node_url = "https://sepolia.infura.io/v3/0776cf37dfb04efdacd478388c7c1dec"

# Solidity contract source code
f = open('./blockchain/SupervisedWallet.sol')
contract_source_code = f.read()
f.close()

# Compile the contract source code
compiled_sol = solcx.compile_source(contract_source_code)
contract_interface = compiled_sol["<stdin>:SupervisedWallet"]

# Connect to the Ethereum node
w3 = Web3(Web3.HTTPProvider(ethereum_node_url))

# Set default account (replace with your own account)
w3.eth.defaultAccount = w3.eth.accounts[0]

# Deploy the contract
SupervisedWallet = w3.eth.contract(abi=contract_interface["abi"], bytecode=contract_interface["bin"])
tx_hash = SupervisedWallet.constructor("0xSuperviseeAddress").transact()
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

# Get the deployed contract address
contract_address = tx_receipt["contractAddress"]
print("Contract deployed at:", contract_address)

# Interact with the contract
supervised_wallet = w3.eth.contract(address=contract_address, abi=contract_interface["abi"])

# sample transaction (Assuming supervisor has approved the transaction)
transaction_id = supervised_wallet.functions.pay("0xRecipientAddress", 100).transact()
print("Transaction sent. Transaction ID:", transaction_id)

# Check the contract state
supervisor_balance = supervised_wallet.functions.funds().call()
print("Supervisor's balance:", supervisor_balance)