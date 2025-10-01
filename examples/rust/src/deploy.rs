// Step 1: Deploy Flash Loan Strategy Contract
//
// This program deploys your flash loan receiver contract.
// You only need to do this ONCE, then reuse the deployed address.

use ethers::{
    prelude::*,
    utils::format_ether,
};
use eyre::Result;
use std::sync::Arc;

// Configuration
const PLASMA_RPC: &str = "https://testnet-rpc.plasma.to";
const FLASH_LOAN_PROVIDER: &str = "0x63A6E3A5743F75388e58e8B778023380694aD3e5";
const PRIVATE_KEY: &str = "<YOUR_PRIVATE_KEY_HERE>";

// Contract bytecode and ABI (compile with hardhat first)
// Note: This is a placeholder - load from artifacts in production
const CONTRACT_BYTECODE: &str = "0x..."; // Load from artifacts

#[tokio::main]
async fn main() -> Result<()> {
    println!("\n🚀 Flash Loan Contract Deployment\n");
    println!("{}", "=".repeat(60));

    // Validate private key
    if PRIVATE_KEY == "<YOUR_PRIVATE_KEY_HERE>" || !PRIVATE_KEY.starts_with("0x") {
        println!("\n❌ Error: Invalid private key!");
        println!("\nPlease update PRIVATE_KEY in src/deploy.rs:");
        println!("   const PRIVATE_KEY: &str = \"0x...your key...\";");
        return Ok(());
    }

    // Setup provider
    let provider = Provider::<Http>::try_from(PLASMA_RPC)?;
    let chain_id = provider.get_chainid().await?;

    println!("\n📍 Network: Plasma Testnet");
    println!("📡 Chain ID: {}", chain_id);

    // Setup wallet
    let wallet: LocalWallet = PRIVATE_KEY.parse()?;
    let wallet = wallet.with_chain_id(chain_id.as_u64());
    let address = wallet.address();

    println!("👤 Deployer: {:?}", address);

    // Check balance
    let balance = provider.get_balance(address, None).await?;
    println!("💰 Balance: {} XPL", format_ether(balance));

    if balance.is_zero() {
        println!("\n❌ Error: No XPL for gas!");
        println!("   Get XPL from: https://gas.zip/faucet/plasma");
        return Ok(());
    }

    // Create client
    let client = Arc::new(SignerMiddleware::new(provider, wallet));

    println!("\n{}", "=".repeat(60));
    println!("Deploying FlashLoanTester Contract...");
    println!("{}", "=".repeat(60));

    println!("\n⏳ Deploying contract...");

    // NOTE: In production, you would:
    // 1. Load ABI and bytecode from Hardhat artifacts
    // 2. Use ethers-rs contract deployment
    // 3. Wait for deployment confirmation
    //
    // Example:
    // let factory = ContractFactory::new(abi, bytecode, client);
    // let contract = factory.deploy(constructor_args)?.send().await?;
    // let address = contract.address();

    println!("
⚠️  IMPORTANT: Contract Deployment in Rust

To deploy contracts in Rust, you need to:

1. Compile the contract with Hardhat:
   cd ../..
   npx hardhat compile

2. Load the ABI and bytecode from artifacts:
   let abi_json = include_str!(\"../../artifacts/contracts/FlashLoanTester.sol/FlashLoanTester.json\");
   let contract_json: serde_json::Value = serde_json::from_str(abi_json)?;

3. Create factory and deploy:
   let factory = ContractFactory::new(abi, bytecode, client);
   let contract = factory
       .deploy(flash_loan_provider)?
       .send()
       .await?;

4. Get deployed address:
   let address = contract.address();

For a complete working example, use the Node.js or Python deployment scripts:
   cd ../nodejs && node 1-deploy-contract.cjs
   cd ../python && python3 1_deploy_contract.py

Then use the deployed address in the Rust execution script.
");

    println!("\n{}", "=".repeat(60));
    println!("📝 Recommended: Use Node.js or Python for deployment");
    println!("{}", "=".repeat(60));

    println!("\nDeployment options:");
    println!("   1. cd ../nodejs && node 1-deploy-contract.cjs");
    println!("   2. cd ../python && python3 1_deploy_contract.py");
    println!("\nThen use the address in src/execute.rs\n");

    Ok(())
}
