#!/usr/bin/env python3
"""
Debug DOGE Deposit Address Response
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://crypto-treasury-app.preview.emergentagent.com/api"

async def debug_doge_response():
    user_wallet_address = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    
    async with aiohttp.ClientSession() as session:
        endpoint = f"{BACKEND_URL}/deposit/doge-address/{user_wallet_address}"
        print(f"Testing endpoint: {endpoint}")
        
        async with session.get(endpoint) as response:
            print(f"Status: {response.status}")
            print(f"Headers: {dict(response.headers)}")
            
            # Get raw response
            raw_response = await response.text()
            print(f"Raw response: {raw_response}")
            
            # Try to parse as JSON
            try:
                json_response = await response.json()
                print(f"JSON response type: {type(json_response)}")
                print(f"JSON response: {json_response}")
            except Exception as e:
                print(f"JSON parse error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_doge_response())