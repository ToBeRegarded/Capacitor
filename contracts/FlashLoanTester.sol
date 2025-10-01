// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

interface IFlashLoanProvider {
    function flashloan(address token, uint256 amount, bytes calldata params) external;
}

interface IFlashLoanReceiver {
    function executeOperation(address token, uint256 amount, uint256 fee, bytes calldata params) external returns (bool);
}

contract FlashLoanTester is IFlashLoanReceiver {
    address public owner;
    address public flashLoanProvider;

    enum TestMode {
        SUCCESS,           // Will repay loan + fee
        FAIL_NO_REPAY,    // Will not repay anything
        FAIL_PARTIAL      // Will repay only principal, not fee
    }

    event FlashLoanReceived(address token, uint256 amount, uint256 fee);
    event TestResult(TestMode mode, bool success);

    constructor(address _flashLoanProvider) {
        owner = msg.sender;
        flashLoanProvider = _flashLoanProvider;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    // Function to initiate a flash loan test
    function testFlashLoan(address token, uint256 amount, TestMode mode) external onlyOwner {
        bytes memory params = abi.encode(mode);
        IFlashLoanProvider(flashLoanProvider).flashloan(token, amount, params);
    }

    // Callback from flash loan provider
    function executeOperation(
        address token,
        uint256 amount,
        uint256 fee,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == flashLoanProvider, "Only flash loan provider");

        emit FlashLoanReceived(token, amount, fee);

        TestMode mode = abi.decode(params, (TestMode));

        if (mode == TestMode.SUCCESS) {
            // SUCCESS: Transfer back the full amount + fee
            uint256 totalRepayment = amount + fee;
            require(IERC20(token).transfer(flashLoanProvider, totalRepayment), "Transfer failed");
            emit TestResult(mode, true);
            return true;
        } else if (mode == TestMode.FAIL_NO_REPAY) {
            // FAIL_NO_REPAY: Return false to signal failure
            emit TestResult(mode, false);
            return false;
        } else if (mode == TestMode.FAIL_PARTIAL) {
            // FAIL_PARTIAL: Only transfer principal, not the fee
            require(IERC20(token).transfer(flashLoanProvider, amount), "Transfer failed");
            emit TestResult(mode, false);
            return true;
        }

        return false;
    }

    // Function to fund this contract with tokens
    function fundContract(address token, uint256 amount) external onlyOwner {
        require(IERC20(token).transferFrom(msg.sender, address(this), amount), "Transfer failed");
    }

    // Function to withdraw tokens
    function withdraw(address token, uint256 amount) external onlyOwner {
        require(IERC20(token).transfer(owner, amount), "Transfer failed");
    }

    // Function to check balance
    function getBalance(address token) external view returns (uint256) {
        return IERC20(token).balanceOf(address(this));
    }

    // Allow contract to receive ETH
    receive() external payable {}
}
