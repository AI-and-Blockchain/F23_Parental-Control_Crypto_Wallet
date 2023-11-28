from typing import Optional
from web3 import Web3, HTTPProvider
from web3.types import TxParams
from json import load

w3 = Web3(HTTPProvider("https://sepolia.infura.io/v3/0776cf37dfb04efdacd478388c7c1dec"))

parse_json_file = lambda filepath: load(open(filepath))

w3stuff = parse_json_file("w3stuff.json")
account: str = w3stuff["account"]
contract = w3.to_checksum_address(w3stuff["contract"])
private_key: str = w3stuff["private_key"]

contract = w3.eth.contract(address=contract, abi=parse_json_file("abi.json"))

def transact(func_name: str, txparams: Optional[TxParams]):
	txn = contract.functions.__getattr__(func_name).build_transaction(txparams)
	signed_txn = w3.eth.account.sign_transaction(txn, private_key)
	return w3.eth.send_raw_transaction(signed_txn.rawTransaction)

txn_hash = transact("deposit", {
	"from": account,
	"value": w3.to_wei(50, "wei")
})

print(f"Transaction hash: {txn_hash}")
