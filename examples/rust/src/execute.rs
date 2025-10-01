// Step 2: Execute Flash Loan
//
// This program executes a flash loan using your deployed contract.
// Replace <DEPLOYED_CONTRACT_ADDRESS> with the address from step 1.

use ethers::{
    prelude::*,
    utils::{format_ether, format_units, parse_ether},
};
use eyre::Result;
use std::sync::Arc;

// Configuration
const PLASMA_RPC: &str = "https://testnet-rpc.plasma.to";
const FLASH_LOAN_PROVIDER: &str = "0x63A6E3A5743F75388e58e8B778023380694aD3e5";
const TUSDT_TOKEN: &str = "0xE5aE1FF9c761F581ac4F1d3075e12ae340500C99";
const PRIVATE_KEY: &str = "<YOUR_PRIVATE_KEY_HERE>";

// YOUR DEPLOYED CONTRACT ADDRESS (from step 1)
const DEPLOYED_CONTRACT: &str = "<DEPLOYED_CONTRACT_ADDRESS>";

// ERC20 ABI (simplified)
abigen!(
    IERC20,
    r#"[
        function balanceOf(address account) external view returns (uint256)
        function transfer(address to, uint256 amount) external returns (bool)
        function symbol() external view returns (string)
        function decimals() external view returns (uint8)
    ]"#,
);

// FlashLoanTester ABI
abigen!(
    IFlashLoanTester,
    r#"[
        function owner() external view returns (address)
        function testFlashLoan(address token, uint256 amount, uint8 mode) external
    ]"#,
);

#[tokio::main]
async fn main() -> Result<()> {
    println!("\n⚡ Execute Flash Loan\n");
    println!("{}", "=".repeat(60));

    // Validate contract address
    if DEPLOYED_CONTRACT == "<DEPLOYED_CONTRACT_ADDRESS>" || !DEPLOYED_CONTRACT.starts_with("0x") {
        println!("\n❌ Error: Invalid contract address!");
        println!("\nPlease update DEPLOYED_CONTRACT in src/execute.rs:");
        println!("   const DEPLOYED_CONTRACT: &str = \"0x...your address...\";");
        println!("\nRun deployment first:");
        println!("   cargo run --bin deploy");
        println!("   OR use Node.js/Python deployment scripts\n");
        return Ok(());
    }

    // Setup provider
    let provider = Provider::<Http>::try_from(PLASMA_RPC)?;
    let chain_id = provider.get_chainid().await?;

    // Setup wallet
    let wallet: LocalWallet = PRIVATE_KEY.parse()?;
    let wallet = wallet.with_chain_id(chain_id.as_u64());
    let address = wallet.address();

    println!("\n📍 Network: Plasma Testnet");
    println!("👤 Wallet: {:?}", address);
    println!("📄 Contract: {}", DEPLOYED_CONTRACT);

    // Create client
    let client = Arc::new(SignerMiddleware::new(provider.clone(), wallet.clone()));

    // Get TUSDT contract
    let tusdt_address: Address = TUSDT_TOKEN.parse()?;
    let tusdt = IERC20::new(tusdt_address, client.clone());

    // Check wallet balance
    let wallet_balance = tusdt.balance_of(address).await?;
    let symbol = tusdt.symbol().await?;
    let decimals = tusdt.decimals().await?;

    println!("💰 Wallet Balance: {} {}",
        format_units(wallet_balance, decimals as u32)?,
        symbol
    );

    if wallet_balance.is_zero() {
        println!("\n❌ Error: No TUSDT balance!");
        println!("   Get tokens from: https://gas.zip/faucet/plasma");
        return Ok(());
    }

    // Get deployed contract
    let contract_address: Address = DEPLOYED_CONTRACT.parse()?;
    let tester = IFlashLoanTester::new(contract_address, client.clone());

    // Verify ownership
    let owner = tester.owner().await?;
    if owner != address {
        println!("\n❌ Error: You are not the owner of this contract!");
        println!("   Contract owner: {:?}", owner);
        println!("   Your address: {:?}", address);
        return Ok(());
    }

    println!("\n{}", "=".repeat(60));
    println!("STEP 1: Fund Contract with Fee Amount");
    println!("{}", "=".repeat(60));

    // Flash loan parameters
    let loan_amount = parse_ether(100)?; // 100 TUSDT
    let fee = loan_amount / U256::from(10000); // 0.01%
    let funding_amount = parse_ether(1)?; // 1 TUSDT

    println!("\n💸 Sending {} {} to contract for fees...",
        format_units(funding_amount, decimals as u32)?,
        symbol
    );

    // Transfer tokens to contract
    let transfer_tx = tusdt.transfer(contract_address, funding_amount);
    let pending_tx = transfer_tx.send().await?;
    println!("⏳ Waiting for transfer confirmation...");
    let _receipt = pending_tx.await?;

    let contract_balance = tusdt.balance_of(contract_address).await?;
    println!("✅ Contract Balance: {} {}",
        format_units(contract_balance, decimals as u32)?,
        symbol
    );

    println!("\n{}", "=".repeat(60));
    println!("STEP 2: Execute Flash Loan");
    println!("{}", "=".repeat(60));

    println!("\n📋 Flash Loan Parameters:");
    println!("   Token: {}", symbol);
    println!("   Amount: {} {}", format_units(loan_amount, decimals as u32)?, symbol);
    println!("   Fee: {} {} (0.01%)", format_units(fee, decimals as u32)?, symbol);
    println!("   Total Repayment: {} {}",
        format_units(loan_amount + fee, decimals as u32)?,
        symbol
    );

    println!("\n⏳ Executing flash loan transaction...");

    // Execute flash loan
    // Mode 0 = SUCCESS
    let flashloan_tx = tester.test_flash_loan(tusdt_address, loan_amount, 0);

    let pending = flashloan_tx.send().await?;
    let tx_hash = pending.tx_hash();

    println!("📝 Transaction sent: {:?}", tx_hash);
    println!("   View: https://testnet.plasmascan.to/tx/{:?}", tx_hash);
    println!("⏳ Waiting for confirmation...");

    match pending.await {
        Ok(Some(receipt)) => {
            println!("\n{}", "=".repeat(60));
            println!("✅ FLASH LOAN EXECUTED SUCCESSFULLY!");
            println!("{}", "=".repeat(60));

            println!("\n📊 Transaction Results:");
            println!("   Block: {:?}", receipt.block_number);
            println!("   Gas Used: {}", receipt.gas_used.unwrap_or_default());
            println!("   Status: {}",
                if receipt.status.unwrap_or_default() == U64::from(1) {
                    "✅ Success"
                } else {
                    "❌ Failed"
                }
            );

            // Check balance after
            let final_balance = tusdt.balance_of(contract_address).await?;
            println!("\n💰 Contract Balance After: {} {}",
                format_units(final_balance, decimals as u32)?,
                symbol
            );

            // Calculate fee paid
            let fee_paid = contract_balance - final_balance;
            println!("📉 Fee Paid: {} {}",
                format_units(fee_paid, decimals as u32)?,
                symbol
            );

            println!("\n✅ Verification:");
            println!("   Expected Fee: {} {}", format_units(fee, decimals as u32)?, symbol);
            println!("   Actual Fee: {} {}", format_units(fee_paid, decimals as u32)?, symbol);
            println!("   Match: {}", if fee_paid == fee { "✅ Yes" } else { "❌ No" });
        }
        Ok(None) => {
            println!("\n❌ Transaction receipt not found");
        }
        Err(e) => {
            println!("\n{}", "=".repeat(60));
            println!("❌ FLASH LOAN FAILED");
            println!("{}", "=".repeat(60));

            println!("\n📋 Error: {:?}", e);

            println!("\n💡 Common Issues:");
            println!("   • Insufficient balance: Contract needs tokens to pay fee");
            println!("   • Pool disabled: Check if TUSDT pool is enabled");
            println!("   • Insufficient liquidity: Pool may not have enough tokens");
            println!("   • Gas too low: Try increasing gas limit");
            println!("\n   See ERRORS.md for detailed troubleshooting");

            return Err(e.into());
        }
    }

    println!("\n{}", "=".repeat(60));
    println!("✨ Flash Loan Complete!");
    println!("{}", "=".repeat(60));
    println!("\n💡 Next Steps:");
    println!("   1. Modify FlashLoanTester.sol to add your arbitrage logic");
    println!("   2. Redeploy your modified contract");
    println!("   3. Execute with real profit strategies");
    println!("   4. Withdraw profits from your contract\n");

    Ok(())
}
