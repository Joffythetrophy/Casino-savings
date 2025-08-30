/**
 * Real Balance Synchronization Component
 * Allows users to sync their database balances with real blockchain holdings
 * Fixes the fake balance issue by connecting to actual blockchain data
 */

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { useAuth } from './UserAuth';
import axios from 'axios';

const RealBalanceSync = () => {
    const [syncing, setSyncing] = useState(false);
    const [syncResult, setSyncResult] = useState(null);
    const [error, setError] = useState('');

    const { user } = useAuth();

    const syncRealBalances = async () => {
        if (!user || !user.wallet_address) {
            setError('No wallet address found. Please login first.');
            return;
        }

        setSyncing(true);
        setError('');
        setSyncResult(null);

        try {
            const response = await axios.post(
                `${process.env.REACT_APP_BACKEND_URL}/api/wallet/sync-real-balances`,
                {
                    wallet_address: user.wallet_address
                },
                {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                    }
                }
            );

            if (response.data.success) {
                setSyncResult(response.data);
            } else {
                setError(response.data.message || 'Synchronization failed');
            }
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Synchronization failed');
        }

        setSyncing(false);
    };

    return (
        <Card className="w-full max-w-2xl mx-auto bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
            <CardHeader className="text-center">
                <CardTitle className="flex items-center justify-center gap-2 text-green-800">
                    🔄 Real Balance Synchronization
                    <Badge className="bg-red-100 text-red-800">URGENT FIX</Badge>
                </CardTitle>
                <CardDescription className="text-green-600">
                    Sync your database balances with REAL blockchain token holdings
                </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* User Information */}
                {user && (
                    <div className="p-3 bg-white rounded-lg border border-green-200">
                        <div className="text-sm text-gray-600">Your Wallet Address</div>
                        <div className="font-mono text-sm text-green-800 break-all">
                            {user.wallet_address}
                        </div>
                        <div className="text-xs text-green-600 mt-1">
                            Username: {user.username}
                        </div>
                    </div>
                )}

                {/* Balance Issues Warning */}
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="text-sm font-medium text-red-800 mb-2">
                        ⚠️ Balance Issue Detected
                    </div>
                    <div className="text-xs text-red-700 space-y-1">
                        <div>• Your CRT balance may be from database only (not real blockchain)</div>
                        <div>• Some balances might show discrepancies</div>
                        <div>• Fake transaction hashes may exist in your history</div>
                        <div>• This sync will connect to REAL Solana blockchain</div>
                    </div>
                </div>

                {/* Sync Information */}
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="text-sm font-medium text-blue-800 mb-2">
                        🔍 What This Sync Does
                    </div>
                    <div className="text-xs text-blue-700 space-y-1">
                        <div>✅ Connects to real Solana blockchain for CRT, USDC, SOL</div>
                        <div>✅ Updates your deposit balances with actual token holdings</div>
                        <div>✅ Preserves your gaming/winnings history</div>
                        <div>✅ Marks balances as "REAL_BLOCKCHAIN_SYNCHRONIZED"</div>
                        <div>✅ Eliminates fake balance issues</div>
                    </div>
                </div>

                {/* Sync Button */}
                <Button 
                    onClick={syncRealBalances} 
                    disabled={syncing || !user}
                    className="w-full bg-green-600 hover:bg-green-700 text-white"
                >
                    {syncing ? '🔄 Synchronizing with Blockchain...' : '🔗 Sync Real Balances Now'}
                </Button>

                {/* Sync Results */}
                {syncResult && (
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg space-y-3">
                        <div className="text-sm font-medium text-green-800">
                            ✅ Synchronization Completed Successfully!
                        </div>
                        
                        <div className="text-xs text-green-700">
                            <div><strong>Sync Time:</strong> {new Date(syncResult.sync_timestamp).toLocaleString()}</div>
                            <div><strong>Balance Source:</strong> {syncResult.balance_source}</div>
                        </div>

                        {syncResult.blockchain_balances && Object.keys(syncResult.blockchain_balances).length > 0 && (
                            <div className="space-y-2">
                                <div className="text-sm font-medium text-green-800">Real Blockchain Balances:</div>
                                {Object.entries(syncResult.blockchain_balances).map(([currency, balance]) => (
                                    <div key={currency} className="flex justify-between text-xs bg-white p-2 rounded border">
                                        <span className="text-gray-600">{currency}</span>
                                        <span className="text-green-800 font-mono">
                                            {balance?.toFixed(6) || '0.000000'}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="text-xs text-green-600 italic">
                            {syncResult.note}
                        </div>
                    </div>
                )}

                {/* Error Display */}
                {error && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                        <div className="text-sm text-red-800">❌ {error}</div>
                        <div className="text-xs text-red-600 mt-1">
                            Please try again or contact support if the issue persists.
                        </div>
                    </div>
                )}

                <Separator />

                {/* Additional Information */}
                <div className="text-xs text-gray-600 space-y-1">
                    <div>🔒 <strong>Security:</strong> Your private keys are never exposed during sync</div>
                    <div>⚡ <strong>Speed:</strong> Sync uses real-time blockchain data</div>
                    <div>💾 <strong>Data:</strong> Gaming history and winnings are preserved</div>
                    <div>🌐 <strong>Blockchain:</strong> Connects to Solana mainnet for token balances</div>
                </div>
            </CardContent>
        </Card>
    );
};

export default RealBalanceSync;