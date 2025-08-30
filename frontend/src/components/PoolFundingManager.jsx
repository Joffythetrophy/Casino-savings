/**
 * Pool Funding Manager - Fund Orca Pools with User's Real Balances
 * Uses your existing $230K balance to create real liquidity pools
 */

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { useAuth } from './UserAuth';
import axios from 'axios';

const PoolFundingManager = () => {
    const [funding, setFunding] = useState(false);
    const [fundingResult, setFundingResult] = useState(null);
    const [error, setError] = useState('');
    
    const { user } = useAuth();

    const fundPoolsWithUserBalance = async () => {
        if (!user || !user.wallet_address) {
            setError('No wallet address found. Please login first.');
            return;
        }

        setFunding(true);
        setError('');
        setFundingResult(null);

        try {
            // Your requested pool configuration
            const poolRequests = [
                {
                    pool_type: "USDC/CRT",
                    amount_usd: 10000,  // $10K Bridge
                    description: "USDC/CRT Bridge Pool - $10K"
                },
                {
                    pool_type: "CRT/SOL", 
                    amount_usd: 10000,  // $10K Bridge
                    description: "CRT/SOL Bridge Pool - $10K"
                },
                {
                    pool_type: "CRT/USDC",
                    amount_usd: 20000,  // $20K Pool 1
                    description: "CRT/USDC Liquidity Pool 1 - $20K"
                },
                {
                    pool_type: "CRT/SOL",
                    amount_usd: 20000,  // $20K Pool 2
                    description: "CRT/SOL Liquidity Pool 2 - $20K"
                }
            ];

            const response = await axios.post(
                `${process.env.REACT_APP_BACKEND_URL}/api/pools/fund-with-user-balance`,
                {
                    wallet_address: user.wallet_address,
                    pool_requests: poolRequests
                },
                {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                    }
                }
            );

            if (response.data.success) {
                setFundingResult(response.data);
            } else {
                setError(response.data.error || 'Pool funding failed');
            }
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Pool funding failed');
        }

        setFunding(false);
    };

    const calculateTotalFunding = () => {
        return 10000 + 10000 + 20000 + 20000; // $60K total
    };

    return (
        <Card className="w-full max-w-4xl mx-auto bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
            <CardHeader className="text-center">
                <CardTitle className="flex items-center justify-center gap-2 text-blue-800">
                    🏊‍♂️ Pool Funding Manager
                    <Badge className="bg-green-100 text-green-800">REAL FUNDING</Badge>
                </CardTitle>
                <CardDescription className="text-blue-600">
                    Fund Orca liquidity pools using your existing $230K cryptocurrency balance
                </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* User Information */}
                {user && (
                    <div className="p-3 bg-white rounded-lg border border-blue-200">
                        <div className="text-sm text-gray-600">Your Wallet</div>
                        <div className="font-mono text-sm text-blue-800 break-all">
                            {user.wallet_address}
                        </div>
                        <div className="text-xs text-blue-600 mt-1">
                            Available Balance: ~$230,000 (21M CRT + DOGE + TRX + SOL + USDC)
                        </div>
                    </div>
                )}

                {/* Pool Funding Plan */}
                <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg">
                    <div className="text-sm font-medium text-green-800 mb-3">
                        🎯 Your Pool Funding Plan
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3 text-xs">
                        <div className="bg-white p-3 rounded border">
                            <div className="font-medium text-blue-800">Bridge Pools ($20K)</div>
                            <div className="text-gray-600 mt-1">
                                • USDC/CRT Bridge: $10,000
                            </div>
                            <div className="text-gray-600">
                                • CRT/SOL Bridge: $10,000
                            </div>
                        </div>
                        
                        <div className="bg-white p-3 rounded border">
                            <div className="font-medium text-blue-800">Liquidity Pools ($40K)</div>
                            <div className="text-gray-600 mt-1">
                                • CRT/USDC Pool 1: $20,000
                            </div>
                            <div className="text-gray-600">
                                • CRT/SOL Pool 2: $20,000
                            </div>
                        </div>
                    </div>

                    <Separator className="my-3" />
                    
                    <div className="flex justify-between items-center">
                        <div className="text-sm font-medium text-green-800">
                            Total Funding Required:
                        </div>
                        <div className="text-lg font-bold text-green-800">
                            ${calculateTotalFunding().toLocaleString()}
                        </div>
                    </div>
                </div>

                {/* Balance Requirements */}
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="text-sm font-medium text-yellow-800 mb-2">
                        💰 Estimated Balance Usage
                    </div>
                    <div className="text-xs text-yellow-700 space-y-1">
                        <div>• CRT Needed: ~3,000,000 CRT (from your 21M balance)</div>
                        <div>• USDC Needed: ~$30,000 (for USDC pools)</div>
                        <div>• SOL Needed: ~125 SOL (for SOL pools)</div>
                        <div>• Will preserve gaming/winnings balances</div>
                    </div>
                </div>

                {/* Fund Pools Button */}
                <Button 
                    onClick={fundPoolsWithUserBalance} 
                    disabled={funding || !user}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3"
                >
                    {funding ? '🏊‍♂️ Funding Pools with Your Balance...' : '💰 Fund All Pools ($60K) with My Balance'}
                </Button>

                {/* Funding Results */}
                {fundingResult && (
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg space-y-3">
                        <div className="text-sm font-medium text-green-800">
                            ✅ Pool Funding Completed Successfully!
                        </div>
                        
                        <div className="text-xs text-green-700">
                            <div><strong>Pools Created:</strong> {fundingResult.funded_pools?.length || 0}</div>
                            <div><strong>Funding Source:</strong> {fundingResult.funding_source}</div>
                        </div>

                        {fundingResult.funded_pools && (
                            <div className="space-y-2">
                                <div className="text-sm font-medium text-green-800">Created Pools:</div>
                                {fundingResult.funded_pools.map((pool, index) => (
                                    <div key={index} className="bg-white p-3 rounded border space-y-1">
                                        <div className="flex justify-between items-center">
                                            <span className="font-medium text-blue-800">{pool.pool_type}</span>
                                            <Badge className="bg-green-100 text-green-800">REAL</Badge>
                                        </div>
                                        
                                        {pool.crt_amount && (
                                            <div className="text-xs text-gray-600">
                                                CRT: {pool.crt_amount.toLocaleString()}
                                            </div>
                                        )}
                                        {pool.usdc_amount && (
                                            <div className="text-xs text-gray-600">
                                                USDC: ${pool.usdc_amount.toLocaleString()}
                                            </div>
                                        )}
                                        {pool.sol_amount && (
                                            <div className="text-xs text-gray-600">
                                                SOL: {pool.sol_amount.toFixed(4)}
                                            </div>
                                        )}
                                        
                                        {pool.transaction_hash && (
                                            <div className="text-xs font-mono text-blue-600 break-all">
                                                TX: {pool.transaction_hash}
                                            </div>
                                        )}
                                        
                                        {pool.pool_address && (
                                            <div className="text-xs font-mono text-green-600 break-all">
                                                Pool: {pool.pool_address}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}

                        {fundingResult.remaining_balances && (
                            <div className="p-3 bg-blue-50 rounded border">
                                <div className="text-sm font-medium text-blue-800 mb-2">Remaining Balances:</div>
                                {Object.entries(fundingResult.remaining_balances).map(([currency, balance]) => (
                                    <div key={currency} className="flex justify-between text-xs">
                                        <span className="text-gray-600">{currency}</span>
                                        <span className="text-blue-800 font-mono">
                                            {balance?.toLocaleString() || '0'}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="text-xs text-green-600 italic">
                            {fundingResult.note}
                        </div>
                    </div>
                )}

                {/* Error Display */}
                {error && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                        <div className="text-sm text-red-800">❌ {error}</div>
                        <div className="text-xs text-red-600 mt-1">
                            Please check your balance or try again.
                        </div>
                    </div>
                )}

                <Separator />

                {/* Important Notes */}
                <div className="text-xs text-gray-600 space-y-1">
                    <div>🔒 <strong>Security:</strong> Uses your existing cryptocurrency balances</div>
                    <div>⚡ <strong>Real Transactions:</strong> Creates actual Orca liquidity pools on Solana</div>
                    <div>💾 <strong>Data Preserved:</strong> Gaming history and winnings remain intact</div>
                    <div>🌊 <strong>Pools:</strong> 2 bridge pools ($20K) + 2 liquidity pools ($40K)</div>
                    <div>💰 <strong>Total:</strong> $60K from your $230K balance</div>
                </div>
            </CardContent>
        </Card>
    );
};

export default PoolFundingManager;