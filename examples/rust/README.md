# Rust Flash Loan Examples

Type-safe flash loan integration using Rust and ethers-rs.

## Prerequisites

- Rust 1.70+ installed ([rustup.rs](https://rustup.rs/))
- XPL tokens for gas (from [Plasma Faucet](https://gas.zip/faucet/plasma))
- TUSDT tokens for testing (from [Plasma Faucet](https://gas.zip/faucet/plasma))

## Setup

```bash
# Check Rust installation
rustc --version

# Build the project
cargo build --release
```

## Configuration

Before running, update the private key in both `src/deploy.rs` and `src/execute.rs`:

```rust
const PRIVATE_KEY: &str = "<YOUR_PRIVATE_KEY_HERE>";
```

**⚠️ Security**: Never commit your private key! Use environment variables in production:

```rust
use std::env;

let private_key = env::var("PRIVATE_KEY")
    .expect("PRIVATE_KEY must be set");
```

## Two-Step Process

### Step 1: Deploy Contract

For contract deployment, we recommend using the Node.js or Python scripts as they handle Hardhat artifact loading better:

**Option A: Node.js (Recommended)**
```bash
cd ../nodejs
node 1-deploy-contract.cjs
```

**Option B: Python**
```bash
cd ../python
python3 1_deploy_contract.py
```

**Option C: Rust (Advanced)**
```bash
cargo run --bin deploy
```

Note: The Rust deployment script provides guidance but requires manual artifact loading. For simplicity, use Node.js or Python for deployment.

Save the deployed contract address!

### Step 2: Execute Flash Loan

Once deployed, execute flash loans using Rust:

1. **Update the contract address** in `src/execute.rs`:
```rust
const DEPLOYED_CONTRACT: &str = "0xYourContractAddressFromStep1";
```

2. **Run the execution:**
```bash
cargo run --bin execute --release
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
⏳ Waiting for transfer confirmation...
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
   Block: 3549900
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

### Deployment (Recommended: Node.js/Python)

The deployment process is more straightforward in Node.js or Python due to better Hardhat integration. Use those languages for deployment, then use Rust for execution.

### Execution Script (`src/execute.rs`)

1. Connects to Plasma testnet using `ethers-rs`
2. Creates type-safe contract instances
3. Verifies ownership
4. Sends tokens to cover fees
5. Executes flash loan
6. Verifies results

## Understanding the Code

### Type-Safe Contract Bindings

```rust
use ethers::prelude::*;

// Generate type-safe bindings
abigen!(
    IERC20,
    r#"[
        function balanceOf(address) external view returns (uint256)
        function transfer(address, uint256) external returns (bool)
    ]"#,
);

// Use the contract
let token = IERC20::new(token_address, client);
let balance = token.balance_of(address).await?;
```

### Async/Await with Tokio

```rust
#[tokio::main]
async fn main() -> Result<()> {
    // Async code here
    let provider = Provider::<Http>::try_from(RPC_URL)?;
    let balance = provider.get_balance(address, None).await?;
    Ok(())
}
```

### Transaction Sending

```rust
// Build transaction
let tx = contract.test_flash_loan(token, amount, 0);

// Send and get pending transaction
let pending = tx.send().await?;

// Wait for confirmation
let receipt = pending.await?;

// Check status
if receipt.status == Some(U64::from(1)) {
    println!("✅ Success!");
}
```

### Error Handling

```rust
use eyre::Result;

async fn execute_flashloan() -> Result<()> {
    let tx = contract.test_flash_loan(token, amount, 0)
        .send()
        .await?;

    match tx.await {
        Ok(Some(receipt)) => {
            println!("Success!");
        }
        Ok(None) => {
            println!("Receipt not found");
        }
        Err(e) => {
            eprintln!("Error: {:?}", e);
            return Err(e.into());
        }
    }

    Ok(())
}
```

## Fee Structure

- **Flash Loan Fee**: 0.01% of borrowed amount
- **Distribution**: 50% to LPs, 50% to Protocol

```rust
let loan_amount = parse_ether(100)?;  // 100 TUSDT
let fee = loan_amount / U256::from(10000);  // 0.01 TUSDT
let repayment = loan_amount + fee;  // 100.01 TUSDT
```

## Gas Optimization

```rust
// Estimate gas
let estimated_gas = contract
    .test_flash_loan(token, amount, 0)
    .estimate_gas()
    .await?;

println!("Estimated gas: {}", estimated_gas);

// Add buffer and set gas limit
let gas_limit = estimated_gas * 120 / 100;  // 20% buffer
let tx = contract
    .test_flash_loan(token, amount, 0)
    .gas(gas_limit);
```

## Building for Production

### Release Build

```bash
# Optimized build
cargo build --release

# Run optimized binary
./target/release/execute
```

### Cross-Compilation

```bash
# For Linux from macOS
cargo build --release --target x86_64-unknown-linux-gnu

# For Windows
cargo build --release --target x86_64-pc-windows-gnu
```

## Troubleshooting

### "Cannot connect to Plasma testnet"
**Solution:** Check RPC URL and internet connection

### "Invalid private key"
**Solution:** Ensure private key starts with '0x' and is 66 characters

### "You are not the owner"
**Solution:** Use the same wallet that deployed the contract

### "Compilation errors"
**Solution:** Update Rust and dependencies:
```bash
rustup update
cargo update
cargo clean
cargo build
```

### "No XPL for gas"
**Solution:** Get XPL from https://gas.zip/faucet/plasma

### "No TUSDT balance"
**Solution:** Get TUSDT from https://gas.zip/faucet/plasma

## Example: Environment Variables

Create `.env` file:
```bash
PRIVATE_KEY=0xyourkey...
DEPLOYED_CONTRACT=0xcontractaddress...
```

Load in Rust:
```rust
use std::env;

fn main() {
    dotenv::dotenv().ok();

    let private_key = env::var("PRIVATE_KEY")
        .expect("PRIVATE_KEY must be set");
    let contract = env::var("DEPLOYED_CONTRACT")
        .expect("DEPLOYED_CONTRACT must be set");
}
```

Add dependency:
```toml
[dependencies]
dotenv = "0.15"
```

## Advanced: Custom Error Types

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum FlashLoanError {
    #[error("Insufficient balance to repay")]
    InsufficientBalance,

    #[error("Pool disabled")]
    PoolDisabled,

    #[error("Not profitable: need {needed}, have {have}")]
    NotProfitable { needed: U256, have: U256 },

    #[error("Contract error: {0}")]
    ContractError(#[from] ethers::contract::ContractError<SignerMiddleware<Provider<Http>, LocalWallet>>),
}
```

## Testing

```bash
# Run tests
cargo test

# Run with output
cargo test -- --nocapture

# Run specific test
cargo test test_flash_loan
```

## Documentation

Generate and view documentation:

```bash
# Generate docs
cargo doc --open

# Include private items
cargo doc --document-private-items --open
```

## Performance

Rust provides excellent performance for:
- High-frequency trading bots
- MEV (Maximal Extractable Value) strategies
- Low-latency arbitrage
- Parallel transaction processing

**Benchmark:**
```bash
cargo bench
```

## Additional Resources

- **Protocol Docs**: See `../../README.md`
- **Error Guide**: See `../../ERRORS.md`
- **ethers-rs Docs**: https://docs.rs/ethers/
- **Rust Book**: https://doc.rust-lang.org/book/
- **Block Explorer**: https://testnet.plasmascan.to

## Next Steps

1. Deploy contract using Node.js or Python
2. Save the contract address
3. Update `src/execute.rs` with the address
4. Run: `cargo run --bin execute --release`
5. Modify contract for your strategy
6. Redeploy and scale up!

## Why Rust for Flash Loans?

- **Type Safety**: Catch errors at compile time
- **Performance**: Native speed for arbitrage bots
- **Memory Safety**: No garbage collection pauses
- **Concurrency**: Easily parallelize strategies
- **Reliability**: Production-ready for high-stakes DeFi

Rust is ideal for MEV bots and high-frequency arbitrage strategies where performance and reliability are critical.
