# Python Flash Loan Examples

Complete implementation of flash loan integration using Python and web3.py.

## Prerequisites

- Python 3.8+ installed
- XPL tokens for gas (from [Plasma Faucet](https://gas.zip/faucet/plasma))
- TUSDT tokens for testing (from [Plasma Faucet](https://gas.zip/faucet/plasma))

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Compile contracts (from OpenSource directory)
cd ../..
npx hardhat compile
cd examples/python
```

## Configuration

Before running, update the private key in both scripts:

```python
PRIVATE_KEY = '<YOUR_PRIVATE_KEY_HERE>'
```

**⚠️ Security**: Never commit your private key! Use environment variables in production:

```python
import os
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
```

## Two-Step Process

### Step 1: Deploy Contract (Once)

Deploy your flash loan strategy contract:

```bash
python3 1_deploy_contract.py
```

**Output:**
```
🚀 Flash Loan Contract Deployment
============================================================

📍 Network: Plasma Testnet
👤 Deployer: 0x...
💰 Balance: 1.5 XPL

============================================================
Deploying FlashLoanTester Contract...
============================================================

⏳ Deploying contract...
📝 Transaction sent: 0x...
⏳ Waiting for deployment confirmation...

============================================================
✅ CONTRACT DEPLOYED SUCCESSFULLY!
============================================================

📋 Deployment Details:
   Contract Address: 0xYourContractAddress...
   Flash Loan Provider: 0x63A6E3A5743F75388e58e8B778023380694aD3e5
   Owner: 0x...
   Block: 3549800
   Gas Used: 1234567

============================================================
📝 SAVE THIS ADDRESS!
============================================================

Your deployed contract address:

    0xYourContractAddress...

Copy this address and use it in step 2!
```

**Important:** Save the deployed contract address!

### Step 2: Execute Flash Loan (Reusable)

1. **Update the contract address** in `2_execute_flashloan.py`:
```python
DEPLOYED_CONTRACT = '0xYourContractAddressFromStep1'
```

2. **Run the execution:**
```bash
python3 2_execute_flashloan.py
```

**Output:**
```
⚡ Execute Flash Loan
============================================================

📍 Network: Plasma Testnet
👤 Wallet: 0x...
📄 Contract: 0x...
💰 Wallet Balance: 1000.0 TUSD

============================================================
STEP 1: Fund Contract with Fee Amount
============================================================

💸 Sending 1.0 TUSD to contract for fees...
✅ Contract Balance: 1.0 TUSD

============================================================
STEP 2: Execute Flash Loan
============================================================

📋 Flash Loan Parameters:
   Token: TUSD
   Amount: 100.0 TUSD
   Fee: 0.01 TUSD (0.01%)
   Total Repayment: 100.01 TUSD

⏳ Executing flash loan transaction...
📝 Transaction sent: 0x...
⏳ Waiting for confirmation...

============================================================
✅ FLASH LOAN EXECUTED SUCCESSFULLY!
============================================================

📊 Transaction Results:
   Block: 3549850
   Gas Used: 268290
   Status: ✅ Success

💰 Contract Balance After: 0.99 TUSD
📉 Fee Paid: 0.01 TUSD

✅ Verification:
   Expected Fee: 0.01 TUSD
   Actual Fee: 0.01 TUSD
   Match: ✅ Yes
```

## How It Works

### Deployment Script (`1_deploy_contract.py`)

1. Connects to Plasma testnet via web3.py
2. Loads compiled contract from Hardhat artifacts
3. Deploys `FlashLoanTester` contract
4. Sets you as the owner
5. Outputs the deployed address

**You only run this ONCE per strategy.**

### Execution Script (`2_execute_flashloan.py`)

1. Connects to your deployed contract
2. Verifies you're the owner
3. Sends TUSDT to cover the flash loan fee
4. Executes the flash loan
5. Verifies repayment and fee

**Run this as many times as you want.**

## Understanding the Code

### Web3 Connection

```python
from web3 import Web3

# Connect to Plasma
w3 = Web3(Web3.HTTPProvider('https://testnet-rpc.plasma.to'))

# Check connection
if w3.is_connected():
    print('Connected!')
```

### Account Management

```python
# Load account from private key
account = w3.eth.account.from_key(PRIVATE_KEY)
print(f'Address: {account.address}')

# Check balance
balance = w3.eth.get_balance(account.address)
```

### Contract Interaction

```python
# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Call view function
owner = contract.functions.owner().call()

# Send transaction
txn = contract.functions.testFlashLoan(token, amount, 0).build_transaction({
    'from': account.address,
    'nonce': w3.eth.get_transaction_count(account.address),
    'gas': 500000,
    'gasPrice': w3.eth.gas_price,
})

# Sign and send
signed = account.sign_transaction(txn)
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

# Wait for receipt
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
```

## Fee Structure

- **Flash Loan Fee**: 0.01% of borrowed amount
- **Distribution**: 50% to LPs, 50% to Protocol

**Example:**
```python
loan_amount = 100 * 10**18  # 100 TUSDT
fee = loan_amount // 10000   # 0.01 TUSDT
repayment = loan_amount + fee  # 100.01 TUSDT
```

## Gas Optimization

```python
# Estimate gas before sending
gas_estimate = contract.functions.testFlashLoan(
    token, amount, 0
).estimate_gas({'from': account.address})

print(f'Estimated gas: {gas_estimate}')

# Add 20% buffer
gas_limit = int(gas_estimate * 1.2)
```

## Error Handling

```python
try:
    # Execute flash loan
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt['status'] == 1:
        print('✅ Success!')
    else:
        print('❌ Transaction reverted')

except Exception as error:
    print(f'❌ Error: {str(error)}')

    # Check specific errors
    if 'insufficient funds' in str(error):
        print('Need more XPL for gas')
    elif 'nonce too low' in str(error):
        print('Transaction already sent')
```

## Troubleshooting

### "Cannot connect to Plasma testnet"
**Solution:** Check RPC URL and internet connection

### "Contract not compiled"
**Solution:** Run from OpenSource directory:
```bash
cd ../..
npx hardhat compile
cd examples/python
```

### "No XPL for gas"
**Solution:** Get XPL from https://gas.zip/faucet/plasma

### "No TUSDT balance"
**Solution:** Get TUSDT from https://gas.zip/faucet/plasma

### "Invalid private key"
**Solution:** Ensure private key starts with '0x' and is 66 characters

### "You are not the owner"
**Solution:** Use the same wallet that deployed the contract

## Example: Environment Variables

For better security:

```python
# .env file
PRIVATE_KEY=0xyourkey...
DEPLOYED_CONTRACT=0xcontractaddress...

# Python script
import os
from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY = os.getenv('PRIVATE_KEY')
DEPLOYED_CONTRACT = os.getenv('DEPLOYED_CONTRACT')
```

Install python-dotenv:
```bash
pip install python-dotenv
```

## Advanced: Adding Arbitrage Logic

To add custom logic, modify the Solidity contract:

```solidity
function executeOperation(
    address token,
    uint256 amount,
    uint256 fee,
    bytes calldata params
) external override returns (bool) {
    // YOUR ARBITRAGE LOGIC HERE
    // - Swap on DEX A
    // - Swap on DEX B
    // - Ensure profit > fee

    // Repay loan
    IERC20(token).transfer(msg.sender, amount + fee);
    return true;
}
```

Then redeploy with step 1.

## Additional Resources

- **Protocol Docs**: See `../../README.md`
- **Error Guide**: See `../../ERRORS.md`
- **Web3.py Docs**: https://web3py.readthedocs.io/
- **Block Explorer**: https://testnet.plasmascan.to

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Compile contracts: `cd ../.. && npx hardhat compile`
3. Run deployment: `python3 1_deploy_contract.py`
4. Save contract address
5. Run execution: `python3 2_execute_flashloan.py`
6. Modify contract for your strategy
7. Redeploy and scale up!
