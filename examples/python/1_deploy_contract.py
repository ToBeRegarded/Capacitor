#!/usr/bin/env python3
"""
Step 1: Deploy Flash Loan Strategy Contract

This script deploys your flash loan receiver contract.
You only need to do this ONCE, then reuse the deployed address.
"""

from web3 import Web3
import json
import sys

# Configuration
PLASMA_RPC = 'https://testnet-rpc.plasma.to'
FLASH_LOAN_PROVIDER = '0x63A6E3A5743F75388e58e8B778023380694aD3e5'
PRIVATE_KEY = '<YOUR_PRIVATE_KEY_HERE>'

# Contract ABI and bytecode (compile with hardhat first)
FLASH_LOAN_TESTER_ABI = json.loads('''
[
  {
    "inputs": [{"internalType": "address", "name": "_flashLoanProvider", "type": "address"}],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "inputs": [],
    "name": "owner",
    "outputs": [{"internalType": "address", "name": "", "type": "address"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType": "address", "name": "token", "type": "address"},
      {"internalType": "uint256", "name": "amount", "type": "uint256"},
      {"internalType": "uint8", "name": "mode", "type": "uint8"}
    ],
    "name": "testFlashLoan",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
''')

def main():
    print('\n🚀 Flash Loan Contract Deployment\n')
    print('=' * 60)

    # Validate private key
    if PRIVATE_KEY == '<YOUR_PRIVATE_KEY_HERE>' or not PRIVATE_KEY.startswith('0x'):
        print('\n❌ Error: Invalid private key!')
        print('\nPlease update PRIVATE_KEY in the script:')
        print('   PRIVATE_KEY = "0x...your key..."')
        return

    # Connect to Plasma testnet
    w3 = Web3(Web3.HTTPProvider(PLASMA_RPC))

    if not w3.is_connected():
        print('\n❌ Error: Cannot connect to Plasma testnet')
        print(f'   RPC: {PLASMA_RPC}')
        return

    # Setup account
    account = w3.eth.account.from_key(PRIVATE_KEY)

    print(f'\n📍 Network: Plasma Testnet')
    print(f'👤 Deployer: {account.address}')

    # Check balance
    balance = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f'💰 Balance: {balance_eth} XPL')

    if balance == 0:
        print('\n❌ Error: No XPL for gas!')
        print('   Get XPL from: https://gas.zip/faucet/plasma')
        return

    print('\n' + '=' * 60)
    print('Deploying FlashLoanTester Contract...')
    print('=' * 60)

    # Load compiled contract
    # Note: You need to compile with hardhat first
    # This loads from artifacts directory
    try:
        with open('../../artifacts/contracts/FlashLoanTester.sol/FlashLoanTester.json', 'r') as f:
            contract_json = json.load(f)
            bytecode = contract_json['bytecode']
            abi = contract_json['abi']
    except FileNotFoundError:
        print('\n❌ Error: Contract not compiled!')
        print('\nPlease compile first:')
        print('   cd ../..')
        print('   npx hardhat compile')
        print('   cd examples/python')
        return

    print('\n⏳ Deploying contract...')

    # Create contract instance
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Build transaction
    construct_txn = Contract.constructor(FLASH_LOAN_PROVIDER).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price,
    })

    # Sign and send transaction
    signed_txn = account.sign_transaction(construct_txn)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    print(f'📝 Transaction sent: {tx_hash.hex()}')
    print('⏳ Waiting for deployment confirmation...')

    # Wait for receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt['contractAddress']

    print('\n' + '=' * 60)
    print('✅ CONTRACT DEPLOYED SUCCESSFULLY!')
    print('=' * 60)

    print('\n📋 Deployment Details:')
    print(f'   Contract Address: {contract_address}')
    print(f'   Flash Loan Provider: {FLASH_LOAN_PROVIDER}')
    print(f'   Owner: {account.address}')
    print(f'   Block: {tx_receipt["blockNumber"]}')
    print(f'   Gas Used: {tx_receipt["gasUsed"]}')
    print(f'   Block Explorer: https://testnet.plasmascan.to/address/{contract_address}')

    print('\n' + '=' * 60)
    print('📝 SAVE THIS ADDRESS!')
    print('=' * 60)
    print('\nYour deployed contract address:')
    print(f'\n    {contract_address}\n')
    print('Copy this address and use it in step 2!\n')

    print('Next step:')
    print('   python3 2_execute_flashloan.py\n')

if __name__ == '__main__':
    main()
