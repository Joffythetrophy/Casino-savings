/**
 * Test Real Blockchain Manager Directly
 * This script tests the blockchain manager functionality independently
 */

async function testBlockchainManager() {
    try {
        console.log("🧪 Testing Real Blockchain Manager...");
        
        // Import the blockchain manager
        const RealBlockchainManager = require('./blockchain/real_blockchain_manager.js');
        const manager = new RealBlockchainManager();
        
        console.log("✅ Blockchain manager loaded successfully");
        
        // Test 1: Address validation
        console.log("\n📍 Testing Address Validation:");
        
        const dogeAddress = "D7LCDsmMATQ5B7UonSZNfnrxCQ2GRTXKNi";
        const solanaAddress = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq";
        
        const dogeValidation = manager.validateAddress("DOGE", dogeAddress);
        console.log(`DOGE ${dogeAddress}: ${JSON.stringify(dogeValidation)}`);
        
        const solanaValidation = manager.validateAddress("SOL", solanaAddress);
        console.log(`SOL ${solanaAddress}: ${JSON.stringify(solanaValidation)}`);
        
        // Test 2: Network fees
        console.log("\n💰 Testing Network Fees:");
        try {
            const fees = await manager.getNetworkFees();
            console.log("Network fees:", JSON.stringify(fees, null, 2));
        } catch (error) {
            console.log("Network fees error:", error.message);
        }
        
        // Test 3: Balance check (only if we have valid addresses)
        console.log("\n💳 Testing Balance Checks:");
        try {
            const dogeBalance = await manager.getBalance("DOGE", dogeAddress);
            console.log(`DOGE balance for ${dogeAddress}:`, JSON.stringify(dogeBalance));
        } catch (error) {
            console.log("DOGE balance error:", error.message);
        }
        
        try {
            const solBalance = await manager.getBalance("SOL", solanaAddress);
            console.log(`SOL balance for ${solanaAddress}:`, JSON.stringify(solBalance));
        } catch (error) {
            console.log("SOL balance error:", error.message);
        }
        
        console.log("\n✅ Blockchain manager test completed");
        
    } catch (error) {
        console.error("❌ Blockchain manager test failed:", error);
        console.error("Stack trace:", error.stack);
    }
}

// Run the test
testBlockchainManager().catch(console.error);