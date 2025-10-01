# Quick Start Guide

Get started with flash loans in 5 minutes.

## Prerequisites

- Node.js 18+ (for Node.js examples)
- Python 3.8+ (for Python examples)
- Rust 1.70+ (for Rust examples)

## Step 1: Get Test Tokens

1. Visit [Plasma Faucet](https://gas.zip/faucet/plasma)
2. Request:
   - XPL (for gas fees)
   - TUSDT (test tokens to use in flash loans)
3. Verify tokens arrived in your wallet

## Step 2: Clone and Install

```bash
# Install dependencies
npm install

# Verify installation
npx hardhat compile
```

## Step 3: Run Your First Flash Loan

### Node.js Example

```bash
cd examples/nodejs
node flashloan-complete.cjs
```

**Expected Output**:
```
🚀 Complete Flash Loan Example
============================================================

📍 Network: Plasma Testnet
👤 Wallet: 0x...
💰 Initial Balance: 1000.0 TUSD

============================================================
STEP 1: Deploy Flash Loan Receiver Contract
============================================================

📝 Deploying FlashLoanTester...
✅ Contract deployed at: 0x...

============================================================
STEP 2: Fund Contract with Tokens
============================================================

💸 Funding contract with 1.0 TUSD...
✅ Contract funded: 1.0 TUSD

============================================================
STEP 3: Execute Flash Loan
============================================================

📋 Flash Loan Details:
   Token: TUSD
   Amount: 5.0 TUSD
   Fee: 0.0005 TUSD (0.01%)
   Total Repayment: 5.0005 TUSD

⏳ Executing flash loan...
📝 Transaction sent: 0x...
✅ FLASH LOAN SUCCESSFUL!

💰 Contract Balance After: 0.9995 TUSD
📉 Fee Paid: 0.0005 TUSD

✨ Example Complete!
```

## Understanding the Fee

**Flash Loan Fee: 0.01%**

Example:
```
Borrow:  1,000 TUSDT
Fee:         0.1 TUSDT (0.01% of 1,000)
Repay:   1,000.1 TUSDT
```

Fee Distribution:
- 50% to Liquidity Providers (those who deposited tokens)
- 50% to Protocol Treasury

## Common Issues

### "No TUSDT balance"

**Solution**: Get tokens from faucet
```bash
Visit: https://gas.zip/faucet/plasma
Request: TUSDT tokens
```

### "Insufficient balance to repay"

**Solution**: Your strategy needs to be profitable
```
The example contract has 1 TUSD to cover fees.
If you borrow 5 TUSD, you must repay 5.0005 TUSD.
The 0.0005 TUSD fee is taken from your contract's balance.
```

### "Out of gas"

**Solution**: Increase gas limit
```javascript
const tx = await flashLoan.flashLoan(..., {
    gasLimit: 500000n // Increase this if needed
});
```

## Next Steps

1. **Read the full README.md** - Understand how flash loans work
2. **Check ERRORS.md** - Complete error documentation
3. **Modify the example** - Add your own profit logic
4. **Test thoroughly** - Always test on testnet first
5. **Scale up** - Start small, increase amounts gradually

## Example Use Cases

### Arbitrage
Buy low on one DEX, sell high on another. Keep the profit.

### Liquidation
Liquidate undercollateralized positions for liquidation bonuses.

### Collateral Swap
Change your collateral type without closing your position.

## Smart Contract Template

Here's the core logic you need:

```solidity
contract MyFlashLoanBot is IFlashLoanReceiver {
    function executeFlashLoan(
        address token,
        uint256 amount,
        uint256 fee,
        bytes calldata data
    ) external override {
        require(msg.sender == flashLoanProvider, "Unauthorized");

        // YOUR PROFIT LOGIC HERE
        // Example: arbitrage, liquidation, collateral swap

        // Repay the loan
        uint256 repayment = amount + fee;
        IERC20(token).transfer(msg.sender, repayment);
    }
}
```

## Protocol Information

- **Network**: Plasma Testnet (Chain ID: 13473)
- **RPC**: https://testnet-rpc.plasma.to
- **Explorer**: https://testnet.plasmascan.to
- **Flash Loan Provider**: `0x63A6E3A5743F75388e58e8B778023380694aD3e5`
- **TUSDT Token**: `0xE5aE1FF9c761F581ac4F1d3075e12ae340500C99`

## Testing Your Strategy

### 1. Start Small
```javascript
const testAmount = ethers.parseUnits('1', 18); // 1 TUSDT only
```

### 2. Verify Profitability
```javascript
const balanceBefore = await token.balanceOf(myAddress);
// Execute flash loan
const balanceAfter = await token.balanceOf(myAddress);
const profit = balanceAfter - balanceBefore;
console.log('Profit:', ethers.formatUnits(profit, 18));
```

### 3. Check on Explorer
Every transaction is viewable at:
```
https://testnet.plasmascan.to/tx/YOUR_TX_HASH
```

## Resources

- **README.md** - Complete documentation
- **ERRORS.md** - All possible errors and solutions
- **examples/** - Working code in Node.js, Python, Rust

## Support

Having issues? Check:
1. **ERRORS.md** - Complete error documentation
2. **Transaction on explorer** - See what reverted
3. **Balance** - Ensure you have tokens
4. **Gas** - Try increasing gas limit

---

Happy flash loaning! 🚀
