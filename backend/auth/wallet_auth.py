from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import secrets
import jwt
import os
from pydantic import BaseModel

security = HTTPBearer()

class WalletAuthManager:
    def __init__(self, jwt_secret: str = None):
        self.jwt_secret = jwt_secret or os.getenv("JWT_SECRET_KEY", "casino_dapp_secret_2024")
        self.active_challenges = {}
        
    def generate_challenge(self, wallet_address: str) -> Dict[str, str]:
        """Generate authentication challenge for wallet"""
        nonce = secrets.token_hex(16)
        timestamp = datetime.utcnow().isoformat()
        
        challenge_message = f"""
Hello, please sign this message to authenticate with Casino dApp!

Chain: Multi-Chain Casino
Address: {wallet_address}
App: CasinoSavings
Time: {timestamp}
Nonce: {nonce}

This signature will be used to verify your wallet ownership.
        """.strip()
        
        challenge_hash = hashlib.sha256(challenge_message.encode()).hexdigest()
        
        # Store challenge for verification (expires in 5 minutes)
        self.active_challenges[challenge_hash] = {
            "wallet_address": wallet_address,
            "message": challenge_message,
            "created_at": datetime.utcnow(),
            "nonce": nonce
        }
        
        return {
            "challenge": challenge_message,
            "challenge_hash": challenge_hash
        }
    
    def verify_wallet_signature(self, 
                               challenge_hash: str, 
                               signature: str,
                               wallet_address: str) -> bool:
        """Verify wallet signature against challenge"""
        if challenge_hash not in self.active_challenges:
            return False
            
        challenge_data = self.active_challenges[challenge_hash]
        
        # Check if challenge has expired (5 minutes)
        if datetime.utcnow() - challenge_data["created_at"] > timedelta(minutes=5):
            del self.active_challenges[challenge_hash]
            return False
            
        # For demo purposes, we'll accept any signature that's not empty
        # In production, you would verify the actual cryptographic signature
        if signature and len(signature) > 10:
            # Clean up used challenge
            del self.active_challenges[challenge_hash]
            return True
            
        return False
    
    def create_jwt_token(self, wallet_address: str, network: str = "multi") -> str:
        """Create JWT token for authenticated wallet"""
        payload = {
            "wallet_address": wallet_address,
            "network": network,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
            "type": "wallet_auth"
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return wallet info"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return {
                "wallet_address": payload.get("wallet_address"),
                "network": payload.get("network", "multi"),
                "type": payload.get("type")
            }
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

# Initialize global auth manager
auth_manager = WalletAuthManager()

def get_authenticated_wallet(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to extract authenticated wallet from JWT token"""
    wallet_info = auth_manager.verify_jwt_token(credentials.credentials)
    
    if not wallet_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return wallet_info

# Pydantic models for request/response
class ChallengeRequest(BaseModel):
    wallet_address: str
    network: str = "solana"

class VerifyRequest(BaseModel):
    challenge_hash: str
    signature: str
    wallet_address: str
    network: str = "solana"