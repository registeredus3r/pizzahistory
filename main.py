"""
Pentagon Pizza Index - Main Entry Point

Fetches busyness data from APIs (pizzint.watch and besttime.app) and outputs results as JSON.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any

from locations import LOCATIONS
from api_clients import PizzaWatchClient, BestTimeClient, BusynessData

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Run the API fetchers and output results."""
    logger.info("Starting Pentagon Pizza Index API fetch...")
    
    # Initialize clients
    pizzawatch = PizzaWatchClient()
    besttime_key = os.environ.get("BESTTIME_API_KEY")
    besttime = BestTimeClient(besttime_key) if besttime_key else None
    
    if not besttime_key:
        logger.warning("No BESTTIME_API_KEY found. Mar-a-Lago locations will be skipped/error.")

    # 1. Fetch Pentagon Data (Batch)
    logger.info("Fetching Pentagon data from pizzint.watch...")
    pentagon_data = await pizzawatch.fetch_data()
    # Map pizzawatch data by place_id for easy lookup
    # pizzawatch data structure is dict with "data" key containing list of locations
    locations_list = pentagon_data.get("data", [])
    pw_map = {item.get("place_id"): item for item in locations_list if isinstance(item, dict)}

    results = []
    
    for loc in LOCATIONS:
        area = loc.get("area")
        loc_id = loc["id"]
        
        # Initialize result with "No data"
        b_data = BusynessData(
            location_id=loc_id,
            live_percent=None,
            typical_percent=None,
            raw_text=None,
            error=None
        )

        if area == "Pentagon":
            # Process Pentagon locations using PizzaWatch Data
            pw_id = loc.get("pizzawatch_id")
            if pw_id and pw_id in pw_map:
                item = pw_map[pw_id]
                # PizzaWatch provides 'current_popularity' (live)
                # It might also provide baseline. The user output showed 'baseline_popular_times'.
                # We'll extract what we can.
                live = item.get("current_popularity")
                
                # Check for closed status
                is_closed = item.get("is_closed_now", False)
                
                if live is not None:
                     b_data.live_percent = int(live)
                     b_data.raw_text = f"Live popularity: {live}"
                elif is_closed:
                    b_data.error = "Location is closed"
                else:
                    b_data.error = "No live data available"
            else:
                 b_data.error = "Data not found in PizzaWatch response"

        elif area == "Mar-a-Lago":
            # Process Mar-a-Lago using BestTime.app
            if besttime:
                logger.info(f"Fetching BestTime data for {loc['name']}...")
                # We need to use name and address. 
                # Ideally we'd cache the venue_id to save credits/lookups, but strictly following 'forecasts' endpoint for now.
                resp = await besttime.get_venue_forecast(loc["name"], loc.get("address", ""))
                
                if "error" in resp:
                    b_data.error = resp["error"]
                else:
                    # Parse BestTime response
                    # Structure depends on endpoint. Assuming 'analysis' -> 'venue_live_busyness'
                    # Or 'analysis' -> 'venue_forecast'
                    # We will need to adjust this parsing based on actual response structure.
                    # For now, simplistic check:
                    analysis = resp.get("analysis", {})
                    live_busyness = analysis.get("venue_live_busyness")
                    
                    if live_busyness is not None:
                         b_data.live_percent = live_busyness
                         b_data.raw_text = f"BestTime Live: {live_busyness}"
                    else:
                        b_data.error = "BestTime: No live busyness data"
            else:
                b_data.error = "Skipped (No API Key)"
        
        else:
            b_data.error = "Skipped (Control/Other)"
            
        results.append(b_data)

    # Output JSON
    timestamp = datetime.now(timezone.utc).isoformat()
    output = {
        "timestamp": timestamp,
        "total_locations": len(LOCATIONS),
        "successful_scrapes": sum(1 for r in results if r.live_percent is not None),
        "results": []
    }

    for result in results:
        location_info = next((loc for loc in LOCATIONS if loc["id"] == result.location_id), {})
        output["results"].append({
            "location_id": result.location_id,
            "name": location_info.get("name", "Unknown"),
            "area": location_info.get("area", "Unknown"),
            "live_percent": result.live_percent,
            "typical_percent": result.typical_percent,
            "raw_text": result.raw_text,
            "error": result.error
        })
        
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
