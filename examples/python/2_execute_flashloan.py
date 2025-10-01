#!/usr/bin/env python3
"""
Step 2: Execute Flash Loan

This script executes a flash loan using your deployed contract.
Replace <DEPLOYED_CONTRACT_ADDRESS> with the address from step 1.
"""

from web3 import Web3
import json

# Configuration
PLASMA_RPC = 'https://testnet-rpc.plasma.to'
FLASH_LOAN_PROVIDER = '0x63A6E3A5743F75388e58e8B778023380694aD3e5'
TUSDT_TOKEN = '0xE5aE1FF9c761F581ac4F1d3075e12ae340500C99'
PRIVATE_KEY = '<YOUR_PRIVATE_KEY_HERE>'

# YOUR DEPLOYED CONTRACT ADDRESS (from step 1)
DEPLOYED_CONTRACT = '<DEPLOYED_CONTRACT_ADDRESS>'

# ERC20 ABI
ERC20_ABI = json.loads('''
[
  {
    "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
    "name": "balanceOf",
    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType": "address", "name": "to", "type": "address"},
      {"internalType": "uint256", "name": "amount", "type": "uint256"}
    ],
    "name": "transfer",
    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "symbol",
    "outputs": [{"internalType": "string", "name": "", "type": "string"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "decimals",
    "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
    "stateMutability": "view",
    "type": "function"
  }
]
''')

# FlashLoanTester ABI
TESTER_ABI = json.loads('''
[
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
    print('\n⚡ Execute Flash Loan\n')
    print('=' * 60)

    # Validate contract address
    if DEPLOYED_CONTRACT == '<DEPLOYED_CONTRACT_ADDRESS>' or not DEPLOYED_CONTRACT.startswith('0x'):
        print('\n❌ Error: Invalid contract address!')
        print('\nPlease update DEPLOYED_CONTRACT with your address from step 1:')
        print('   DEPLOYED_CONTRACT = "0x...your address..."')
        print('\nRun step 1 first if you haven\'t deployed:')
        print('   python3 1_deploy_contract.py\n')
        return

    # Connect to Plasma
    w3 = Web3(Web3.HTTPProvider(PLASMA_RPC))

    if not w3.is_connected():
        print('\n❌ Error: Cannot connect to Plasma testnet')
        return

    # Setup account
    account = w3.eth.account.from_key(PRIVATE_KEY)

    print(f'\n📍 Network: Plasma Testnet')
    print(f'👤 Wallet: {account.address}')
    print(f'📄 Contract: {DEPLOYED_CONTRACT}')

    # Get TUSDT contract
    tusdt = w3.eth.contract(address=Web3.to_checksum_address(TUSDT_TOKEN), abi=ERC20_ABI)

    # Check wallet balance
    wallet_balance = tusdt.functions.balanceOf(account.address).call()
    symbol = tusdt.functions.symbol().call()
    decimals = tusdt.functions.decimals().call()

    print(f'💰 Wallet Balance: {wallet_balance / 10**decimals} {symbol}')

    if wallet_balance == 0:
        print('\n❌ Error: No TUSDT balance!')
        print('   Get tokens from: https://gas.zip/faucet/plasma')
        return

    # Get contract instance
    tester = w3.eth.contract(
        address=Web3.to_checksum_address(DEPLOYED_CONTRACT),
        abi=TESTER_ABI
    )

    # Verify ownership
    owner = tester.functions.owner().call()
    if owner.lower() != account.address.lower():
        print(f'\n❌ Error: You are not the owner of this contract!')
        print(f'   Contract owner: {owner}')
        print(f'   Your address: {account.address}')
        return

    print('\n' + '=' * 60)
    print('STEP 1: Fund Contract with Fee Amount')
    print('=' * 60)

    # Flash loan parameters
    loan_amount = 100 * 10**decimals  # 100 TUSDT
    fee = loan_amount // 10000  # 0.01%
    funding_amount = 1 * 10**decimals  # 1 TUSDT

    print(f'\n💸 Sending {funding_amount / 10**decimals} {symbol} to contract for fees...')

    # Transfer tokens to contract
    transfer_txn = tusdt.functions.transfer(
        DEPLOYED_CONTRACT,
        funding_amount
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
    })

    signed_transfer = account.sign_transaction(transfer_txn)
    transfer_hash = w3.eth.send_raw_transaction(signed_transfer.rawTransaction)
    w3.eth.wait_for_transaction_receipt(transfer_hash)

    contract_balance = tusdt.functions.balanceOf(DEPLOYED_CONTRACT).call()
    print(f'✅ Contract Balance: {contract_balance / 10**decimals} {symbol}')

    print('\n' + '=' * 60)
    print('STEP 2: Execute Flash Loan')
    print('=' * 60)

    print(f'\n📋 Flash Loan Parameters:')
    print(f'   Token: {symbol}')
    print(f'   Amount: {loan_amount / 10**decimals} {symbol}')
    print(f'   Fee: {fee / 10**decimals} {symbol} (0.01%)')
    print(f'   Total Repayment: {(loan_amount + fee) / 10**decimals} {symbol}')

    print('\n⏳ Executing flash loan transaction...')

    try:
        # Execute flash loan
        # Mode 0 = SUCCESS
        flashloan_txn = tester.functions.testFlashLoan(
            TUSDT_TOKEN,
            loan_amount,
            0  # SUCCESS mode
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 500000,
            'gasPrice': w3.eth.gas_price,
        })

        signed_flashloan = account.sign_transaction(flashloan_txn)
        flashloan_hash = w3.eth.send_raw_transaction(signed_flashloan.rawTransaction)

        print(f'📝 Transaction sent: {flashloan_hash.hex()}')
        print(f'   View: https://testnet.plasmascan.to/tx/{flashloan_hash.hex()}')
        print('⏳ Waiting for confirmation...')

        receipt = w3.eth.wait_for_transaction_receipt(flashloan_hash)

        print('\n' + '=' * 60)
        print('✅ FLASH LOAN EXECUTED SUCCESSFULLY!')
        print('=' * 60)

        print('\n📊 Transaction Results:')
        print(f'   Block: {receipt["blockNumber"]}')
        print(f'   Gas Used: {receipt["gasUsed"]}')
        print(f'   Status: {"✅ Success" if receipt["status"] == 1 else "❌ Failed"}')

        # Check balance after
        final_contract_balance = tusdt.functions.balanceOf(DEPLOYED_CONTRACT).call()
        print(f'\n💰 Contract Balance After: {final_contract_balance / 10**decimals} {symbol}')

        # Calculate fee paid
        fee_paid = contract_balance - final_contract_balance
        print(f'📉 Fee Paid: {fee_paid / 10**decimals} {symbol}')

        print('\n✅ Verification:')
        print(f'   Expected Fee: {fee / 10**decimals} {symbol}')
        print(f'   Actual Fee: {fee_paid / 10**decimals} {symbol}')
        print(f'   Match: {"✅ Yes" if fee_paid == fee else "❌ No"}')

    except Exception as error:
        print('\n' + '=' * 60)
        print('❌ FLASH LOAN FAILED')
        print('=' * 60)

        print(f'\n📋 Error: {str(error)}')

        print('\n💡 Common Issues:')
        print('   • Insufficient balance: Contract needs tokens to pay fee')
        print('   • Pool disabled: Check if TUSDT pool is enabled')
        print('   • Insufficient liquidity: Pool may not have enough tokens')
        print('   • Gas too low: Try increasing gas limit')
        print('\n   See ERRORS.md for detailed troubleshooting')
        raise

    print('\n' + '=' * 60)
    print('✨ Flash Loan Complete!')
    print('=' * 60)
    print('\n💡 Next Steps:')
    print('   1. Modify FlashLoanTester.sol to add your arbitrage logic')
    print('   2. Redeploy your modified contract')
    print('   3. Execute with real profit strategies')
    print('   4. Withdraw profits from your contract\n')

if __name__ == '__main__':
    main()
