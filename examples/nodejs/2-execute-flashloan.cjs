#!/usr/bin/env node

/**
 * Step 2: Execute Flash Loan
 *
 * This script executes a flash loan using your deployed contract.
 * Replace <DEPLOYED_CONTRACT_ADDRESS> with the address from step 1.
 */

const { ethers } = require("hardhat");

// Configuration
const PLASMA_RPC = 'https://testnet-rpc.plasma.to';
const FLASH_LOAN_PROVIDER = '0x63A6E3A5743F75388e58e8B778023380694aD3e5';
const TUSDT_TOKEN = '0xE5aE1FF9c761F581ac4F1d3075e12ae340500C99';
const PRIVATE_KEY = '<YOUR_PRIVATE_KEY_HERE>';

// YOUR DEPLOYED CONTRACT ADDRESS (from step 1)
const DEPLOYED_CONTRACT = '<DEPLOYED_CONTRACT_ADDRESS>';

async function main() {
  console.log('\n⚡ Execute Flash Loan\n');
  console.log('='.repeat(60));

  // Validate contract address
  if (DEPLOYED_CONTRACT === '<DEPLOYED_CONTRACT_ADDRESS>' || !DEPLOYED_CONTRACT.startsWith('0x')) {
    console.log('\n❌ Error: Invalid contract address!');
    console.log('\nPlease update DEPLOYED_CONTRACT with your address from step 1:');
    console.log('   const DEPLOYED_CONTRACT = "0x...your address...";');
    console.log('\nRun step 1 first if you haven\'t deployed:');
    console.log('   node 1-deploy-contract.cjs\n');
    return;
  }

  // Setup provider and wallet
  const provider = new ethers.JsonRpcProvider(PLASMA_RPC);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

  console.log('\n📍 Network: Plasma Testnet');
  console.log('👤 Wallet:', wallet.address);
  console.log('📄 Contract:', DEPLOYED_CONTRACT);

  // Get TUSDT contract
  const tusdtAbi = [
    'function balanceOf(address account) external view returns (uint256)',
    'function transfer(address to, uint256 amount) external returns (bool)',
    'function symbol() external view returns (string)',
    'function decimals() external view returns (uint8)'
  ];
  const tusdt = new ethers.Contract(TUSDT_TOKEN, tusdtAbi, wallet);

  // Check wallet balance
  const walletBalance = await tusdt.balanceOf(wallet.address);
  const symbol = await tusdt.symbol();
  console.log(`💰 Wallet Balance: ${ethers.formatUnits(walletBalance, 18)} ${symbol}`);

  if (walletBalance === 0n) {
    console.log('\n❌ Error: No TUSDT balance!');
    console.log('   Get tokens from: https://gas.zip/faucet/plasma');
    return;
  }

  // Get contract instance
  const testerAbi = [
    'function testFlashLoan(address token, uint256 amount, uint8 mode) external',
    'function owner() external view returns (address)'
  ];
  const tester = new ethers.Contract(DEPLOYED_CONTRACT, testerAbi, wallet);

  // Verify ownership
  const owner = await tester.owner();
  if (owner.toLowerCase() !== wallet.address.toLowerCase()) {
    console.log('\n❌ Error: You are not the owner of this contract!');
    console.log(`   Contract owner: ${owner}`);
    console.log(`   Your address: ${wallet.address}`);
    return;
  }

  console.log('\n' + '='.repeat(60));
  console.log('STEP 1: Fund Contract with Fee Amount');
  console.log('='.repeat(60));

  // Flash loan parameters
  const loanAmount = ethers.parseUnits('100', 18); // 100 TUSDT
  const fee = loanAmount / 10000n; // 0.01% fee
  const fundingAmount = ethers.parseUnits('1', 18); // 1 TUSDT to cover fee

  console.log(`\n💸 Sending ${ethers.formatUnits(fundingAmount, 18)} ${symbol} to contract for fees...`);

  const transferTx = await tusdt.transfer(DEPLOYED_CONTRACT, fundingAmount);
  await transferTx.wait();

  const contractBalance = await tusdt.balanceOf(DEPLOYED_CONTRACT);
  console.log(`✅ Contract Balance: ${ethers.formatUnits(contractBalance, 18)} ${symbol}`);

  console.log('\n' + '='.repeat(60));
  console.log('STEP 2: Execute Flash Loan');
  console.log('='.repeat(60));

  console.log(`\n📋 Flash Loan Parameters:`);
  console.log(`   Token: ${symbol}`);
  console.log(`   Amount: ${ethers.formatUnits(loanAmount, 18)} ${symbol}`);
  console.log(`   Fee: ${ethers.formatUnits(fee, 18)} ${symbol} (0.01%)`);
  console.log(`   Total Repayment: ${ethers.formatUnits(loanAmount + fee, 18)} ${symbol}`);

  console.log('\n⏳ Executing flash loan transaction...');

  try {
    // Execute flash loan
    // Mode 0 = SUCCESS (contract will repay correctly)
    const tx = await tester.testFlashLoan(TUSDT_TOKEN, loanAmount, 0, {
      gasLimit: 500000n
    });

    console.log('📝 Transaction sent:', tx.hash);
    console.log('   View: https://testnet.plasmascan.to/tx/' + tx.hash);
    console.log('⏳ Waiting for confirmation...');

    const receipt = await tx.wait();

    console.log('\n' + '='.repeat(60));
    console.log('✅ FLASH LOAN EXECUTED SUCCESSFULLY!');
    console.log('='.repeat(60));

    console.log('\n📊 Transaction Results:');
    console.log('   Block:', receipt.blockNumber);
    console.log('   Gas Used:', receipt.gasUsed.toString());
    console.log('   Status:', receipt.status === 1 ? '✅ Success' : '❌ Failed');

    // Check balances after
    const finalContractBalance = await tusdt.balanceOf(DEPLOYED_CONTRACT);
    console.log(`\n💰 Contract Balance After: ${ethers.formatUnits(finalContractBalance, 18)} ${symbol}`);

    // Calculate fee paid
    const feePaid = contractBalance - finalContractBalance;
    console.log(`📉 Fee Paid: ${ethers.formatUnits(feePaid, 18)} ${symbol}`);

    console.log('\n✅ Verification:');
    console.log(`   Expected Fee: ${ethers.formatUnits(fee, 18)} ${symbol}`);
    console.log(`   Actual Fee: ${ethers.formatUnits(feePaid, 18)} ${symbol}`);
    console.log(`   Match: ${feePaid === fee ? '✅ Yes' : '❌ No'}`);

  } catch (error) {
    console.log('\n' + '='.repeat(60));
    console.log('❌ FLASH LOAN FAILED');
    console.log('='.repeat(60));

    console.log('\n📋 Error Details:');
    console.log('   Message:', error.message);

    if (error.code) {
      console.log('   Code:', error.code);
    }

    console.log('\n💡 Common Issues:');
    console.log('   • Insufficient balance: Contract needs tokens to pay fee');
    console.log('   • Pool disabled: Check if TUSDT pool is enabled');
    console.log('   • Insufficient liquidity: Pool may not have enough tokens');
    console.log('   • Gas too low: Try increasing gas limit');
    console.log('\n   See ERRORS.md for detailed troubleshooting');

    throw error;
  }

  console.log('\n' + '='.repeat(60));
  console.log('✨ Flash Loan Complete!');
  console.log('='.repeat(60));
  console.log('\n💡 Next Steps:');
  console.log('   1. Modify FlashLoanTester.sol to add your arbitrage logic');
  console.log('   2. Redeploy your modified contract');
  console.log('   3. Execute with real profit strategies');
  console.log('   4. Withdraw profits from your contract\n');
}

if (require.main === module) {
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('\n❌ Execution failed:', error.message);
      process.exit(1);
    });
}

module.exports = { main };
