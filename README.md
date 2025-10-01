<div align="center">

<img src="https://i.ibb.co/q3S4Z50J/Capacitor.png" alt="Capacitor Logo" width="200"/>

# Capacitor Flash Loan Protocol

**Execute arbitrage, liquidations, and DeFi strategies with zero upfront capital**

Production flash loan protocol on Plasma blockchain

[![Website](https://img.shields.io/badge/Website-capacitor.finance-blue)](https://capacitor.finance)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289da)](https://discord.gg/JPMrHTUMDX)
[![X](https://img.shields.io/badge/X-@CapacitorFI-000000)](https://x.com/CapacitorFI)

[Quick Start](#-quick-start) • [Documentation](#-integration-patterns) • [Examples](#-examples) • [Community](#-community)

</div>

---

## 🚀 What is Capacitor?

Capacitor is a **flash loan protocol** that lets you borrow large amounts of crypto with **zero collateral**—as long as you repay within the same transaction. Perfect for arbitrage, liquidations, and advanced DeFi strategies.

**Key Features:**
- ⚡ **Zero Upfront Capital** - Borrow up to the pool's liquidity
- 💰 **Ultra-Low Fees** - Only 0.01% per flash loan
- 🔒 **Battle-Tested** - Production-ready on Plasma blockchain
- 🛠️ **Developer-Friendly** - Complete examples in Node.js, Python & Rust

---

## ⚠️ Important: Smart Contract Requirement

**Flash loans require deploying a smart contract.** This isn't a limitation of Capacitor—it's how flash loans work on all EVM chains (Ethereum, Polygon, Plasma, etc.).

### Why You Need a Contract

Flash loans involve three steps in **ONE atomic transaction**:
1. 📥 **Borrow** tokens from the protocol
2. 🔄 **Execute** your custom logic (swaps, liquidations, etc.)
3. 📤 **Repay** the loan + fee

This atomic execution requires smart contract code. Your wallet alone cannot do this.

### Comparison to Other Chains

| Platform | Requirements |
|----------|-------------|
| **Kamino (Solana)** | No contract needed - Solana allows composing multiple program instructions |
| **EVM Chains** | Requires smart contract to implement callback pattern |

---

## 📡 Network & Deployment

### Plasma Testnet

| Resource | Link/Value |
|----------|------------|
| **Chain ID** | 13473 |
| **RPC URL** | https://testnet-rpc.plasma.to |
| **Block Explorer** | https://testnet.plasmascan.to |
| **Faucet** | https://gas.zip/faucet/plasma |

### Deployed Contracts

| Contract | Address |
|----------|---------|
| **FlashLoanProvider** | `0x63A6E3A5743F75388e58e8B778023380694aD3e5` |
| **TUSDT Token** | `0xE5aE1FF9c761F581ac4F1d3075e12ae340500C99` |

### Fee Structure

- **Flash Loan Fee**: 0.01% (1 basis point)
- **Fee Distribution**: 50% to LPs | 50% to Protocol

**Example:**
```
Borrow:  1,000 TUSDT
Fee:         0.1 TUSDT (0.01%)
Repay:   1,000.1 TUSDT

Distribution:
  → Liquidity Providers: 0.05 TUSDT
  → Protocol:            0.05 TUSDT
```

---

## 🎯 Quick Start

### Step 1: Get Test Tokens

Visit the [Plasma Faucet](https://gas.zip/faucet/plasma) and request:
- **XPL** for gas fees
- **TUSDT** test tokens

### Step 2: Review Examples

We provide complete working implementations:
- 📦 **Node.js** - `examples/nodejs/`
- 🐍 **Python** - `examples/python/`
- 🦀 **Rust** - `examples/rust/`

### Step 3: Deploy Your Strategy

```bash
# Install dependencies
npm install

# Compile contracts
npx hardhat compile

# Run the example (deploys contract + executes flash loan)
cd examples/nodejs
node flashloan-complete.cjs
```

---

## 🏗️ Integration Patterns

### Pattern 1: Deploy Your Strategy Contract

The standard approach—deploy a contract with your custom logic:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

interface IFlashLoanProvider {
    function flashloan(address token, uint256 amount, bytes calldata params) external;
}

interface IFlashLoanReceiver {
    function executeOperation(
        address token,
        uint256 amount,
        uint256 fee,
        bytes calldata params
    ) external returns (bool);
}

contract ArbitrageBot is IFlashLoanReceiver {
    address constant FLASH_LOAN_PROVIDER = 0x63A6E3A5743F75388e58e8B778023380694aD3e5;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function executeOperation(
        address token,
        uint256 amount,
        uint256 fee,
        bytes calldata params
    ) external override returns (bool) {
        // Security: Only flash loan provider can call this
        require(msg.sender == FLASH_LOAN_PROVIDER, "Unauthorized");

        // ================================================
        // YOUR CUSTOM ARBITRAGE LOGIC HERE
        // ================================================
        // Examples:
        // - Swap on DEX A: token → USDC
        // - Swap on DEX B: USDC → token (more tokens back)
        // - Liquidate: repay debt, receive collateral, sell
        // - Refinance: payoff expensive loan, take cheaper one
        // ================================================

        // Must repay loan + fee
        uint256 repayment = amount + fee;

        // Verify we have enough
        require(IERC20(token).balanceOf(address(this)) >= repayment, "Insufficient balance");

        // Repay the flash loan
        IERC20(token).transfer(FLASH_LOAN_PROVIDER, repayment);

        return true;
    }

    // Function to trigger flash loan
    function executeArbitrage(address token, uint256 amount) external {
        require(msg.sender == owner, "Only owner");

        IFlashLoanProvider(FLASH_LOAN_PROVIDER).flashloan(
            token,
            amount,
            "" // custom params if needed
        );
    }

    // Withdraw profits
    function withdrawProfits(address token) external {
        require(msg.sender == owner, "Only owner");
        uint256 balance = IERC20(token).balanceOf(address(this));
        IERC20(token).transfer(owner, balance);
    }
}
```

**Deploy and use:**
```javascript
// 1. Deploy your contract
const Bot = await ethers.getContractFactory("ArbitrageBot");
const bot = await Bot.deploy();
await bot.waitForDeployment();

// 2. Execute arbitrage when profitable
await bot.executeArbitrage(TUSDT_TOKEN, ethers.parseUnits("1000", 18));

// 3. Withdraw profits
await bot.withdrawProfits(TUSDT_TOKEN);
```

### Pattern 2: Add to Existing Contract

If you have an existing trading bot, vault, or protocol, add flash loan support:

```solidity
contract MyExistingVault is IFlashLoanReceiver {
    // Your existing code...

    mapping(address => bool) public authorizedStrategies;

    function executeOperation(
        address token,
        uint256 amount,
        uint256 fee,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == FLASH_LOAN_PROVIDER, "Unauthorized");

        // Decode which strategy to execute
        (string memory strategy, bytes memory strategyData) = abi.decode(params, (string, bytes));

        // Execute the appropriate strategy
        if (keccak256(bytes(strategy)) == keccak256("ARBITRAGE")) {
            _executeArbitrage(token, amount, strategyData);
        } else if (keccak256(bytes(strategy)) == keccak256("LIQUIDATION")) {
            _executeLiquidation(token, amount, strategyData);
        }

        // Repay
        IERC20(token).transfer(FLASH_LOAN_PROVIDER, amount + fee);
        return true;
    }

    // Your existing functions can now use flash loans
    function _executeArbitrage(address token, uint256 amount, bytes memory data) internal {
        // Your existing arbitrage logic
    }
}
```

---

## 💡 Use Cases

### 1. Arbitrage Trading

```
Price difference detected:
  DEX A: 1 ETH = 2,000 USDT
  DEX B: 1 ETH = 2,010 USDT

Flash loan execution:
  1. Borrow 20,000 USDT (fee: 2 USDT)
  2. Buy on DEX A: 20,000 USDT → 10 ETH
  3. Sell on DEX B: 10 ETH → 20,100 USDT
  4. Repay: 20,002 USDT
  5. Profit: 98 USDT ✅
```

### 2. Liquidation Bot

```
Undercollateralized position found:
  Debt: 10,000 USDT
  Collateral: 10,500 USDT worth (105% collateralization)
  Liquidation bonus: 5%

Flash loan execution:
  1. Borrow 10,000 USDT (fee: 1 USDT)
  2. Repay user's debt
  3. Receive 10,500 USDT collateral + 5% bonus = 11,025 USDT
  4. Repay: 10,001 USDT
  5. Profit: 1,024 USDT ✅
```

### 3. Collateral Swap

```
Your position:
  Collateral: 50,000 USDC
  Debt: 25,000 USDT
  Want: Change collateral to ETH

Flash loan execution:
  1. Borrow 50 ETH worth of ETH
  2. Deposit 50 ETH as new collateral
  3. Withdraw 50,000 USDC
  4. Swap USDC for ETH
  5. Repay flash loan + fee
  6. Result: Same debt, but ETH collateral instead of USDC ✅
```

---

## 📚 Examples

### Node.js

Complete working example with contract deployment and execution:

```bash
cd examples/nodejs
node flashloan-complete.cjs
```

**What it does:**
1. Deploys FlashLoanTester contract
2. Funds it with tokens
3. Executes flash loan
4. Verifies repayment

### Python

Web3.py integration:

```bash
cd examples/python
pip install -r requirements.txt
python3 flashloan_example.py
```

### Rust

Type-safe implementation using ethers-rs:

```bash
cd examples/rust
cargo run
```

---

## 📖 API Reference

### IFlashLoanProvider

```solidity
interface IFlashLoanProvider {
    /// @notice Execute a flash loan
    /// @param token Token address to borrow
    /// @param amount Amount to borrow
    /// @param params Custom data passed to your contract
    function flashloan(
        address token,
        uint256 amount,
        bytes calldata params
    ) external;

    /// @notice Get pool information
    /// @param token Token address
    /// @return Pool details (liquidity, APY, volume, enabled status)
    function getPoolDetails(address token) external view returns (
        string memory ticker,
        uint8 decimals,
        uint256 totalLiquidity,
        uint256 availableLiquidity,
        uint256 utilization,
        uint256 apy,
        uint256 volume24h,
        uint256 volume7d,
        uint256 totalVolume,
        uint256 totalFlashloans,
        bool enabled
    );
}
```

### IFlashLoanReceiver

```solidity
interface IFlashLoanReceiver {
    /// @notice Callback function executed during flash loan
    /// @dev Must return true or transaction reverts
    /// @param token Token borrowed
    /// @param amount Amount borrowed
    /// @param fee Fee that must be paid (in addition to principal)
    /// @param params Custom data from flashloan() call
    /// @return success Must return true
    function executeOperation(
        address token,
        uint256 amount,
        uint256 fee,
        bytes calldata params
    ) external returns (bool);
}
```

---

## ⚙️ Gas Costs

Typical gas usage on Plasma:

| Operation | Gas Cost |
|-----------|----------|
| Simple flash loan | 150,000 - 200,000 |
| Flash loan + 1 swap | 250,000 - 350,000 |
| Flash loan + 2 swaps | 400,000 - 500,000 |
| Complex strategy | 500,000 - 800,000 |

**Optimization tips:**
- Use `calldata` instead of `memory` for external functions
- Cache storage variables in memory
- Minimize external calls
- Batch operations when possible

---

## 🔒 Security Best Practices

### 1. Validate the Caller

```solidity
function executeOperation(...) external override returns (bool) {
    require(msg.sender == FLASH_LOAN_PROVIDER, "Unauthorized");
    // Your logic
}
```

### 2. Check Repayment

```solidity
uint256 repayment = amount + fee;
require(IERC20(token).balanceOf(address(this)) >= repayment, "Insufficient");
IERC20(token).transfer(FLASH_LOAN_PROVIDER, repayment);
```

### 3. Protect Against Reentrancy

```solidity
bool private locked;

modifier noReentrant() {
    require(!locked, "Reentrant call");
    locked = true;
    _;
    locked = false;
}

function executeArbitrage(...) external noReentrant {
    // Safe from reentrancy
}
```

### 4. Test Thoroughly

- ✅ Deploy on Plasma testnet first
- ✅ Test with small amounts
- ✅ Verify profitability calculations
- ✅ Check edge cases (slippage, price changes)

---

## 🐛 Debugging

### Check Pool Liquidity

```javascript
const poolDetails = await flashLoanProvider.getPoolDetails(TUSDT_TOKEN);
console.log('Available:', ethers.formatUnits(poolDetails.availableLiquidity, 18));
console.log('Enabled:', poolDetails.enabled);
```

### Estimate Gas

```javascript
try {
  const gasEstimate = await contract.estimateGas.executeArbitrage(token, amount);
  console.log('Gas needed:', gasEstimate.toString());
} catch (error) {
  console.error('Estimation failed:', error.message);
}
```

### Verify Profitability

```javascript
// Calculate all costs
const flashLoanFee = amount * 0.0001; // 0.01%
const gasPrice = await provider.getFeeData();
const gasCost = gasPrice.gasPrice * estimatedGas;
const dexFees = amount * 0.003; // 0.3% per swap

const totalCosts = flashLoanFee + gasCost + (dexFees * 2); // Two swaps

// Check revenue
const expectedProfit = calculateArbitrageProfit(amount);

console.log('Costs:', totalCosts);
console.log('Expected profit:', expectedProfit);
console.log('Profitable:', expectedProfit > totalCosts * 1.2); // 20% margin
```

---

## 📚 Additional Resources

- **QUICKSTART.md** - Get started in 5 minutes
- **ERRORS.md** - Complete error documentation
- **examples/** - Working code in Node.js, Python, Rust
- **Block Explorer** - https://testnet.plasmascan.to

---

## 🌐 Community

Join our growing community of flash loan developers:

- 🌍 **Website**: [capacitor.finance](https://capacitor.finance)
- 💬 **Discord**: [Join our server](https://discord.gg/JPMrHTUMDX)
- 🐦 **X (Twitter)**: [@CapacitorFI](https://x.com/CapacitorFI)

Have questions? Found a bug? Want to share your strategy? We'd love to hear from you!

---

## ⚖️ License

Educational purposes only. Use at your own risk.

**Disclaimer**: Flash loans are powerful financial tools. Test thoroughly on testnet. Ensure strategies are profitable after all fees and gas costs. Smart contract security audits are recommended before mainnet deployment.

---

<div align="center">

**Built with ⚡ by the Capacitor Team**

[capacitor.finance](https://capacitor.finance) | [Discord](https://discord.gg/JPMrHTUMDX) | [X](https://x.com/CapacitorFI)

</div>
