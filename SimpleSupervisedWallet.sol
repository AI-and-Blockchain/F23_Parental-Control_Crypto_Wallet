// SPDX-License-Identifier: Apache 
pragma solidity ^0.8.0;

contract SimpleSupervisedWallet {
	address public supervisor;
	uint public funds;

	constructor() payable {
		supervisor = msg.sender;
		funds = msg.value;
	}

	modifier onlySupervisor {
		_;
		require(msg.sender == supervisor, "Only the supervisor may call this function");
	}

	function deposit() external payable onlySupervisor {
		funds += msg.value;
	}
}
