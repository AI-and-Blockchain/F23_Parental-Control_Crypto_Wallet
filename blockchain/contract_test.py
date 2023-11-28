from typing import Any, Optional
from web3 import Web3, HTTPProvider
from web3.types import TxParams
from web3.contract.contract import Contract
from json import load

w3 = Web3(HTTPProvider("https://sepolia.infura.io/v3/0776cf37dfb04efdacd478388c7c1dec"))

parse_json_file = lambda filepath: load(open(filepath))

w3stuff: dict[str, Any] = parse_json_file("w3stuff.json")
account: str = w3stuff["account"]
contract: Contract = w3.eth.contract(w3stuff["contract"], abi=parse_json_file("abi.json"))

txn_hash = contract.functions.deposit().transact({
	"from": account,
	"value": w3.to_wei(50, "wei")
})

print(f"Transaction hash: {txn_hash}")
