# Flash Loan Error Documentation

Complete guide to errors you might encounter when executing flash loans, with causes and solutions.

## Table of Contents

- [Most Common Errors](#most-common-errors)
- [Smart Contract Errors](#smart-contract-errors)
- [Gas Errors](#gas-errors)
- [Generic 0x Errors](#generic-0x-errors)
- [Debugging Guide](#debugging-guide)

---

## Most Common Errors

### Error: "Insufficient balance to repay"

**Cause**: Your flash loan receiver contract doesn't have enough tokens to repay the loan + fee.

**Example Scenario**:
```
Borrowed: 1,000 TUSDT
Fee: 0.1 TUSDT
Required Repayment: 1,000.1 TUSDT
Contract Balance After Logic: 999.5 TUSDT ❌
```

**Solutions**:
1. **Ensure profitable strategy**: Your arbitrage/trading logic must generate enough profit to cover the fee
2. **Pre-fund contract**: Send tokens to your contract before executing flash loan
3. **Check calculations**: Verify you're calculating repayment correctly (principal + fee)
4. **Test with small amounts**: Start with 1-10 tokens to verify logic works

**Code Fix**:
```solidity
function executeFlashLoan(...) external override {
    // Your profit logic here

    // Verify we have enough before repaying
    uint256 totalRepayment = amount + fee;
    uint256 balance = IERC20(token).balanceOf(address(this));
    require(balance >= totalRepayment, "Insufficient balance to repay");

    IERC20(token).transfer(msg.sender, totalRepayment);
}
```

---

### Error: "Pool disabled"

**Cause**: The admin has temporarily disabled the token pool.

**How to Check Pool Status**:
```javascript
const poolDetails = await flashLoanProvider.getPoolDetails(tokenAddress);
console.log('Pool enabled:', poolDetails.enabled);
```

**Solutions**:
1. Wait for pool to be re-enabled
2. Use a different token pool
3. Contact protocol admin if disabled for extended period

---

### Error: "Amount exceeds available liquidity"

**Cause**: You're trying to borrow more tokens than are currently available in the pool.

**Example**:
```
Pool Liquidity: 1,000 TUSDT
Your Request: 1,500 TUSDT ❌
```

**Check Available Liquidity**:
```javascript
const poolDetails = await flashLoanProvider.getPoolDetails(TUSDT_TOKEN);
console.log('Available:', ethers.formatUnits(poolDetails.availableLiquidity, 18));
```

**Solutions**:
1. **Reduce loan amount** to be less than available liquidity
2. **Split into multiple loans** if you need more than available
3. **Wait for deposits** - Check back later when more liquidity is added

---

## Smart Contract Errors

### Error: "ERC20: transfer amount exceeds balance"

**Cause**: Trying to transfer more tokens than the contract holds.

**Debug**:
```javascript
// Check contract balance
const balance = await token.balanceOf(contractAddress);
console.log('Balance:', ethers.formatUnits(balance, 18));

// Check required amount
const required = loanAmount + fee;
console.log('Required:', ethers.formatUnits(required, 18));

if (balance < required) {
    console.log('❌ Insufficient balance!');
}
```

**Solution**: Ensure your logic generates enough profit or pre-fund the contract.

---

### Error: "ERC20: approve to the zero address"

**Cause**: Trying to approve tokens to address `0x0000...0000`.

**Fix**:
```javascript
// ❌ Wrong
await token.approve('0x0000000000000000000000000000000000000000', amount);

// ✅ Correct
await token.approve(flashLoanProviderAddress, amount);
```

---

### Error: "Reentrancy detected"

**Cause**: Your contract is trying to call the flash loan provider again while a flash loan is already in progress.

**Example of Reentrancy**:
```solidity
function executeFlashLoan(...) external override {
    // ❌ Calling flashLoan again creates reentrancy
    IFlashLoanProvider(msg.sender).flashLoan(address(this), token, amount, data);
}
```

**Solution**: Never call `flashLoan()` from within `executeFlashLoan()`. Complete your logic and repay.

---

## Gas Errors

### Error: "out of gas"

**Cause**: Transaction ran out of gas before completing.

**Typical Gas Usage**:
| Operation | Gas Required |
|-----------|--------------|
| Simple flash loan | 150,000 - 200,000 |
| Flash loan + 1 swap | 250,000 - 350,000 |
| Flash loan + 2 swaps | 400,000 - 500,000 |
| Complex strategy | 500,000 - 800,000 |

**Solutions**:
```javascript
// 1. Estimate gas first
const gasEstimate = await flashLoan.estimateGas.flashLoan(...);
console.log('Estimated gas:', gasEstimate.toString());

// 2. Add 20% buffer
const gasLimit = gasEstimate * 120n / 100n;

// 3. Execute with explicit limit
const tx = await flashLoan.flashLoan(..., { gasLimit });
```

---

### Error: "intrinsic gas too low"

**Cause**: Gas limit is below the minimum required for any transaction (21,000 gas).

**Solution**:
```javascript
// ❌ Too low
const tx = await flashLoan.flashLoan(..., { gasLimit: 10000 });

// ✅ Minimum for flash loan
const tx = await flashLoan.flashLoan(..., { gasLimit: 150000 });
```

---

## Generic 0x Errors

### Error: "0x" or Empty Error

**This is a catch-all revert with no specific message. Common causes:**

#### 1. Integer Overflow/Underflow

**Pre-Solidity 0.8**:
```solidity
// ❌ Can overflow
uint256 result = a + b;

// ✅ Use SafeMath
uint256 result = a.add(b);
```

**Solidity 0.8+**: Automatic overflow protection

#### 2. Division by Zero

```solidity
// ❌ Reverts with 0x if b is 0
uint256 result = a / b;

// ✅ Check first
require(b != 0, "Division by zero");
uint256 result = a / b;
```

#### 3. Array Out of Bounds

```solidity
// ❌ Reverts with 0x if index >= length
uint256 value = myArray[index];

// ✅ Check bounds
require(index < myArray.length, "Index out of bounds");
uint256 value = myArray[index];
```

#### 4. Failed External Call

```solidity
// ❌ Silent failure
token.transfer(to, amount);

// ✅ Check return value
require(token.transfer(to, amount), "Transfer failed");
```

#### 5. Insufficient Token Allowance

**Check**:
```javascript
const allowance = await token.allowance(owner, spender);
if (allowance < amount) {
    await token.approve(spender, amount);
}
```

### Debugging 0x Errors

```javascript
try {
    const tx = await flashLoan.flashLoan(...);
    await tx.wait();
} catch (error) {
    console.log('Error message:', error.message);
    console.log('Error code:', error.code);
    console.log('Error data:', error.data);

    // Try to decode revert reason
    if (error.data) {
        const reason = ethers.toUtf8String('0x' + error.data.slice(138));
        console.log('Revert reason:', reason);
    }

    // Estimate gas to see if it's a gas issue
    try {
        const estimate = await flashLoan.estimateGas.flashLoan(...);
        console.log('Gas estimate succeeds:', estimate.toString());
        console.log('→ Likely not a gas issue');
    } catch (estimateError) {
        console.log('Gas estimate fails → Transaction will revert');
        console.log('Reason:', estimateError.message);
    }
}
```

---

## Debugging Guide

### Step 1: Isolate the Issue

```javascript
// Test each component separately

// 1. Can you connect to network?
const provider = new ethers.JsonRpcProvider('https://testnet-rpc.plasma.to');
const blockNumber = await provider.getBlockNumber();
console.log('✅ Network connection:', blockNumber);

// 2. Does your wallet have tokens?
const balance = await token.balanceOf(wallet.address);
console.log('✅ Token balance:', ethers.formatUnits(balance, 18));

// 3. Is the pool enabled?
const poolDetails = await flashLoanProvider.getPoolDetails(token);
console.log('✅ Pool enabled:', poolDetails.enabled);

// 4. Is there enough liquidity?
console.log('✅ Available liquidity:', ethers.formatUnits(poolDetails.availableLiquidity, 18));

// 5. Can you estimate gas?
const gasEstimate = await flashLoan.estimateGas.flashLoan(...);
console.log('✅ Gas estimate:', gasEstimate.toString());
```

### Step 2: Enable Verbose Logging

```javascript
// Log everything
const tx = await flashLoan.flashLoan(receiver, token, amount, data, {
    gasLimit: 500000n
});

console.log('Transaction object:', {
    to: tx.to,
    from: tx.from,
    data: tx.data,
    gasLimit: tx.gasLimit?.toString(),
    gasPrice: tx.gasPrice?.toString()
});

const receipt = await tx.wait();
console.log('Receipt:', {
    blockNumber: receipt.blockNumber,
    gasUsed: receipt.gasUsed.toString(),
    status: receipt.status,
    logs: receipt.logs
});
```

### Step 3: Check On-Chain State

```javascript
// Check pool state
const poolDetails = await flashLoanProvider.getPoolDetails(token);
console.log('Pool state:', {
    ticker: poolDetails.ticker,
    totalLiquidity: ethers.formatUnits(poolDetails.totalLiquidity, 18),
    availableLiquidity: ethers.formatUnits(poolDetails.availableLiquidity, 18),
    enabled: poolDetails.enabled
});

// Check receiver contract
const code = await provider.getCode(receiverAddress);
console.log('Receiver deployed:', code !== '0x');

// Check token balances
const receiverBalance = await token.balanceOf(receiverAddress);
console.log('Receiver balance:', ethers.formatUnits(receiverBalance, 18));
```

### Step 4: Test on Block Explorer

1. Go to https://testnet.plasmascan.to
2. Search for your contract address
3. Try "Read Contract" to check state
4. Try "Write Contract" to test functions
5. View past transactions for errors

### Step 5: Start Simple

```javascript
// Test with smallest possible amount
const minAmount = ethers.parseUnits('0.1', 18); // 0.1 TUSDT

// Use high gas limit to rule out gas issues
const gasLimit = 1000000n;

// Add detailed logging
try {
    console.log('Attempting flash loan...');
    const tx = await flashLoan.flashLoan(receiver, token, minAmount, '0x', { gasLimit });
    console.log('Transaction sent:', tx.hash);

    const receipt = await tx.wait();
    console.log('Success! Gas used:', receipt.gasUsed.toString());
} catch (error) {
    console.log('Failed. Error:', error.message);
}
```

---

## Getting Help

If you encounter an error not listed here:

1. **Check transaction on explorer**: https://testnet.plasmascan.to
2. **Enable verbose logging** as shown in debugging guide
3. **Test with minimal example** to isolate the issue
4. **Check network status** - RPC may be down
5. **Verify contract is deployed** and has correct code
6. **Review your custom logic** - Ensure it's profitable and doesn't revert

## Protocol Information

- **Network**: Plasma Testnet (Chain ID: 13473)
- **RPC**: https://testnet-rpc.plasma.to
- **Explorer**: https://testnet.plasmascan.to
- **Flash Loan Provider**: `0x63A6E3A5743F75388e58e8B778023380694aD3e5`
- **TUSDT Token**: `0xE5aE1FF9c761F581ac4F1d3075e12ae340500C99`
