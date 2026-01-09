"""
Pentagon Pizza Index - Main Entry Point

Runs the busyness scraper on all configured locations and outputs results as JSON.
"""

import asyncio
import json
import sys
from datetime import datetime, timezone

from locations import LOCATIONS
from scraper import scrape_locations_batch


async def main():
    """Run the scraper and output results."""
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Pentagon Pizza Index scrape...")
    print(f"Scraping {len(LOCATIONS)} locations...")
    
    # Run the scraper
    results = await scrape_locations_batch(LOCATIONS, batch_size=3)
    
    # Convert results to JSON-serializable format
    timestamp = datetime.now(timezone.utc).isoformat()
    output = {
        "timestamp": timestamp,
        "total_locations": len(LOCATIONS),
        "successful_scrapes": sum(1 for r in results if r.error is None),
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
    
    # Print results as JSON
    print("\n" + "=" * 60)
    print("SCRAPE RESULTS")
    print("=" * 60)
    print(json.dumps(output, indent=2))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {timestamp}")
    print(f"Total locations: {output['total_locations']}")
    print(f"Successful scrapes: {output['successful_scrapes']}")
    print(f"Failed scrapes: {output['total_locations'] - output['successful_scrapes']}")
    
    # Print any errors
    errors = [r for r in results if r.error]
    if errors:
        print("\nErrors:")
        for r in errors:
            print(f"  - {r.location_id}: {r.error}")
    
    return output


if __name__ == "__main__":
    asyncio.run(main())
