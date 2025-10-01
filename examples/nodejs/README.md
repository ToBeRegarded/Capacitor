# Node.js Flash Loan Examples

Complete implementation of flash loan integration using Node.js and ethers.js.

## Prerequisites

- Node.js 18+ installed
- XPL tokens for gas (from [Plasma Faucet](https://gas.zip/faucet/plasma))
- TUSDT tokens for testing (from [Plasma Faucet](https://gas.zip/faucet/plasma))

## Setup

```bash
# From the OpenSource directory
npm install

# Compile contracts
npx hardhat compile
```

## Configuration

Before running, update the private key in both scripts:

```javascript
const PRIVATE_KEY = '<YOUR_PRIVATE_KEY_HERE>';
```

**⚠️ Security**: Never commit your private key to version control!

## Two-Step Process

### Step 1: Deploy Contract (Once)

Deploy your flash loan strategy contract:

```bash
node 1-deploy-contract.cjs
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
⏳ Waiting for deployment confirmation...

============================================================
✅ CONTRACT DEPLOYED SUCCESSFULLY!
============================================================

📋 Deployment Details:
   Contract Address: 0xYourContractAddress...
   Flash Loan Provider: 0x63A6E3A5743F75388e58e8B778023380694aD3e5
   Owner: 0x...
   Block Explorer: https://testnet.plasmascan.to/address/0x...

============================================================
📝 SAVE THIS ADDRESS!
============================================================

Your deployed contract address:

    0xYourContractAddress...

Copy this address and use it in step 2!
```

**Important:** Save the deployed contract address! You'll need it for step 2.

### Step 2: Execute Flash Loan (Reusable)

Once deployed, you can execute flash loans multiple times:

1. **Update the contract address** in `2-execute-flashloan.cjs`:
```javascript
const DEPLOYED_CONTRACT = '0xYourContractAddressFromStep1';
```

2. **Run the execution:**
```bash
node 2-execute-flashloan.cjs
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
   Block: 3549800
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

### Deployment Script (`1-deploy-contract.cjs`)

1. Connects to Plasma testnet
2. Deploys `FlashLoanTester` contract
3. Sets you as the owner
4. Outputs the deployed address

**You only run this ONCE per strategy.**

### Execution Script (`2-execute-flashloan.cjs`)

1. Connects to your deployed contract
2. Verifies you're the owner
3. Sends tokens to cover the flash loan fee
4. Executes the flash loan
5. Verifies repayment

**Run this as many times as you want.**

## Understanding the Contracts

### FlashLoanTester.sol

This is a test contract that demonstrates the flash loan callback pattern:

```solidity
contract FlashLoanTester is IFlashLoanReceiver {
    function executeOperation(
        address token,
        uint256 amount,
        uint256 fee,
        bytes calldata params
    ) external override returns (bool) {
        // 1. Contract receives borrowed tokens
        // 2. Execute your custom logic here
        // 3. Repay loan + fee
        IERC20(token).transfer(msg.sender, amount + fee);
        return true;
    }
}
```

**To add your strategy:**
1. Modify the `executeOperation` function
2. Add DEX swaps, liquidations, or other logic
3. Ensure you repay `amount + fee`
4. Redeploy with step 1

## Fee Structure

- **Flash Loan Fee**: 0.01% of borrowed amount
- **Distribution**: 50% to LPs, 50% to Protocol

**Example:**
```
Borrow:  100 TUSDT
Fee:       0.01 TUSDT
Repay:   100.01 TUSDT
```

## Gas Costs

- **Deployment**: ~1,500,000 gas
- **Flash Loan Execution**: ~250,000 - 300,000 gas

**Tip:** Monitor gas prices and execute during low-traffic periods.

## Troubleshooting

### "No XPL for gas"
**Solution:** Get XPL from https://gas.zip/faucet/plasma

### "No TUSDT balance"
**Solution:** Get TUSDT from https://gas.zip/faucet/plasma

### "Invalid contract address"
**Solution:** Run step 1 first, then copy the address to step 2

### "You are not the owner"
**Solution:** Make sure you're using the same wallet that deployed the contract

### "Insufficient balance to repay"
**Solution:** The contract needs tokens to pay the fee. Step 2 handles this automatically.

### "Pool disabled"
**Solution:** The TUSDT pool may be temporarily disabled. Check pool status:
```javascript
const details = await provider.getPoolDetails(TUSDT_TOKEN);
console.log('Enabled:', details.enabled);
```

## Example: Adding Arbitrage Logic

Modify `FlashLoanTester.sol`:

```solidity
function executeOperation(
    address token,
    uint256 amount,
    uint256 fee,
    bytes calldata params
) external override returns (bool) {
    require(msg.sender == flashLoanProvider, "Unauthorized");

    // YOUR ARBITRAGE LOGIC
    // 1. Swap on DEX A
    uint256 intermediateAmount = swapOnDexA(token, amount);

    // 2. Swap on DEX B
    uint256 finalAmount = swapOnDexB(intermediateAmount);

    // 3. Ensure profitable
    require(finalAmount >= amount + fee, "Not profitable");

    // 4. Repay flash loan
    IERC20(token).transfer(msg.sender, amount + fee);

    // 5. Profit stays in contract (withdraw later)
    return true;
}
```

Then redeploy:
```bash
node 1-deploy-contract.cjs
```

## Security Notes

1. **Never hardcode private keys** - Use environment variables
2. **Test on testnet first** - Always verify with small amounts
3. **Verify ownership** - Only contract owner can execute
4. **Check profitability** - Ensure profit > fees + gas

## Additional Resources

- **Protocol Docs**: See `../../README.md`
- **Error Guide**: See `../../ERRORS.md`
- **Block Explorer**: https://testnet.plasmascan.to
- **Faucet**: https://gas.zip/faucet/plasma

## Next Steps

1. Run step 1 to deploy your contract
2. Save the contract address
3. Run step 2 to execute flash loans
4. Modify the contract to add your strategy
5. Redeploy and test
6. Scale up when profitable!
