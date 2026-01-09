import aiohttp
import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

@dataclass
class BusynessData:
    location_id: str
    live_percent: Optional[int]
    typical_percent: Optional[int]
    raw_text: Optional[str]
    error: Optional[str]

class PizzaWatchClient:
    """Client for pizzint.watch API (Pentagon locations)."""
    API_URL = "https://www.pizzint.watch/api/dashboard-data"
    
    # Mapping from our location IDs to PizzaWatch place_ids or names
    # Based on the user's provided dashboard data output
    # We might need to map by address or verify place_ids.
    # For now, I'll fetch the data and try to match by name or address if possible, 
    # or just assume the dashboard endpoint returns a list we can parse.
    # The output shown in the previous turn had "place_id" and "name". 
    # Matches need to be robust.
    
    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch all dashboard data."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.API_URL) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to fetch PizzaWatch data: {response.status}")
                    return {}

class BestTimeClient:
    """Client for BestTime.app API (Mar-a-Lago locations)."""
    BASE_URL = "https://besttime.app/api/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    async def get_venue_forecast(self, venue_name: str, venue_address: str) -> Dict[str, Any]:
        """
        Get live/forecast data for a venue. 
        BestTime usually requires adding the venue first or using their search/forecast endpoint.
        We'll use the 'forecasts/live' or similar endpoint if available, or 'forecasts' with Name/Address.
        """
        if not self.api_key:
            return {"error": "Missing BestTime API Key"}

        params = {
            "api_key_private": self.api_key,
            "venue_name": venue_name,
            "venue_address": venue_address
        }
        
        # Using the New Foot Traffic Forecast endpoint (or Live if available/paid)
        # Docs say: POST /api/v1/forecasts
        url = f"{self.BASE_URL}/forecasts"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    logger.warning(f"BestTime API Rate Limit Exceeded for {venue_name}")
                    return {"error": "Rate limited"}
                else:
                    logger.error(f"BestTime API Error for {venue_name}: {response.status}")
                    text = await response.text()
                    logger.error(f"Response: {text}")
                    return {"error": f"API Error {response.status}"}

