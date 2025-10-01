#!/usr/bin/env node

/**
 * Step 1: Deploy Flash Loan Strategy Contract
 *
 * This script deploys your flash loan receiver contract.
 * You only need to do this ONCE, then reuse the deployed address.
 */

const { ethers } = require("hardhat");

// Configuration
const PLASMA_RPC = 'https://testnet-rpc.plasma.to';
const FLASH_LOAN_PROVIDER = '0x63A6E3A5743F75388e58e8B778023380694aD3e5';
const PRIVATE_KEY = '<YOUR_PRIVATE_KEY_HERE>';

async function main() {
  console.log('\n🚀 Flash Loan Contract Deployment\n');
  console.log('='.repeat(60));

  // Setup provider and wallet
  const provider = new ethers.JsonRpcProvider(PLASMA_RPC);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

  console.log('\n📍 Network: Plasma Testnet');
  console.log('👤 Deployer:', wallet.address);

  // Check balance
  const balance = await provider.getBalance(wallet.address);
  console.log('💰 Balance:', ethers.formatEther(balance), 'XPL');

  if (balance === 0n) {
    console.log('\n❌ Error: No XPL for gas!');
    console.log('   Get XPL from: https://gas.zip/faucet/plasma');
    return;
  }

  console.log('\n' + '='.repeat(60));
  console.log('Deploying FlashLoanTester Contract...');
  console.log('='.repeat(60));

  // Deploy FlashLoanTester contract
  const FlashLoanTester = await ethers.getContractFactory('FlashLoanTester', wallet);

  console.log('\n⏳ Deploying contract...');
  const tester = await FlashLoanTester.deploy(FLASH_LOAN_PROVIDER);

  console.log('⏳ Waiting for deployment confirmation...');
  await tester.waitForDeployment();

  const testerAddress = await tester.getAddress();

  console.log('\n' + '='.repeat(60));
  console.log('✅ CONTRACT DEPLOYED SUCCESSFULLY!');
  console.log('='.repeat(60));

  console.log('\n📋 Deployment Details:');
  console.log('   Contract Address:', testerAddress);
  console.log('   Flash Loan Provider:', FLASH_LOAN_PROVIDER);
  console.log('   Owner:', wallet.address);
  console.log('   Block Explorer:', `https://testnet.plasmascan.to/address/${testerAddress}`);

  console.log('\n' + '='.repeat(60));
  console.log('📝 SAVE THIS ADDRESS!');
  console.log('='.repeat(60));
  console.log('\nYour deployed contract address:');
  console.log(`\n    ${testerAddress}\n`);
  console.log('Copy this address and use it in step 2!\n');

  console.log('Next step:');
  console.log('   node 2-execute-flashloan.cjs\n');
}

if (require.main === module) {
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('\n❌ Deployment failed:', error.message);
      process.exit(1);
    });
}

module.exports = { main };
