"""
Pentagon Pizza Index - Google Maps Busyness Scraper

Scrapes live busyness data from Google Maps for target restaurant locations.
Uses Playwright with stealth techniques to avoid bot detection.
"""

import asyncio
import random
import re
import logging
from typing import Optional
from dataclasses import dataclass
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from proxy_utils import proxy_manager

logger = logging.getLogger(__name__)


@dataclass
class BusynessData:
    """Scraped busyness data for a location."""
    location_id: str
    live_percent: Optional[int]
    typical_percent: Optional[int]
    raw_text: Optional[str]
    error: Optional[str]


# Stealth configuration - Using DESKTOP User-Agents (Popular Times only shows on desktop web)
DESKTOP_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

STEALTH_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


def parse_busyness_text(text: str) -> tuple[Optional[int], Optional[int]]:
    """
    Parse busyness text from Google Maps aria-label.
    
    Two formats:
    1. Live: "Currently 12% busy, usually 18% busy."
    2. Hourly: "41% busy at 9 PM."
    """
    live_percent = None
    typical_percent = None
    
    # Format 1: Live data - "Currently X% busy, usually Y% busy."
    live_match = re.search(r'[Cc]urrently\s+(\d+)%\s*busy,?\s*usually\s+(\d+)%', text)
    if live_match:
        live_percent = int(live_match.group(1))
        typical_percent = int(live_match.group(2))
        return live_percent, typical_percent
    
    # Format 2: Hourly data - "X% busy at TIME"
    hourly_match = re.search(r'(\d+)%\s*busy\s+at', text)
    if hourly_match:
        typical_percent = int(hourly_match.group(1))
    
    return live_percent, typical_percent


async def scrape_location(url: str, location_id: str, max_retries: int = 2) -> BusynessData:
    """
    Scrape busyness data from a Google Maps location URL.
    
    Args:
        url: Google Maps URL for the location
        location_id: Unique identifier for the location
        max_retries: Maximum number of retry attempts for 429 errors
    
    Returns:
        BusynessData with scraped values or error information
    """
    user_agent = random.choice(DESKTOP_USER_AGENTS)
    
    for attempt in range(max_retries + 1):
        proxy = await proxy_manager.get_valid_proxy()
        if proxy:
            logger.info(f"[{location_id}] Using proxy: {proxy}")
        
        try:
            async with async_playwright() as p:
                launch_kwargs = {"headless": True}
                if proxy:
                    launch_kwargs["proxy"] = {"server": proxy}
                
                browser = await p.chromium.launch(**launch_kwargs)
                context = await browser.new_context(
                    user_agent=user_agent,
                    viewport={"width": 1280, "height": 900},  # Desktop viewport for Popular Times
                )
                
                page = await context.new_page()
                # Increase timeout for potentially slow proxies
                page.set_default_timeout(60000) 
                
                # Randomized wait before navigation (1-5 seconds)
                await asyncio.sleep(random.uniform(1, 5))
                
                # Navigate to the page
                response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Check for rate limiting
                if response and response.status == 429:
                    if attempt < max_retries:
                        print(f"[{location_id}] Rate limited (429), retrying in 10s...")
                        await browser.close()
                        await asyncio.sleep(10)
                        continue
                    else:
                        await browser.close()
                        return BusynessData(
                            location_id=location_id,
                            live_percent=None,
                            typical_percent=None,
                            raw_text=None,
                            error="Rate limited (429) after retries"
                        )
                
                # Wait for page content to fully load (JS-rendered content)
                await asyncio.sleep(random.uniform(6, 8))
                
                # Scroll down using keyboard (container scroll doesn't work reliably)
                # First click on the sidebar to focus it
                try:
                    sidebar = await page.query_selector('[role="main"]')
                    if sidebar:
                        await sidebar.click()
                        await asyncio.sleep(0.3)
                    
                    # Use Page Down to scroll and reveal Popular Times section
                    for _ in range(8):
                        await page.keyboard.press("PageDown")
                        await asyncio.sleep(0.2)
                    
                    await asyncio.sleep(1)
                except Exception:
                    pass
                
                # Look for busyness elements - get ALL of them and pick the best
                busyness_elements = await page.query_selector_all('[aria-label*="busy"]')
                
                if busyness_elements:
                    # Find the best match
                    # Priority: 1) Live data "X% busy, usually Y%" 2) "currently" 3) First hourly
                    best_label = None
                    for el in busyness_elements:
                        label = await el.get_attribute("aria-label")
                        if label:
                            # Top priority: Live data with "usually" (format: "19% busy, usually 18% busy")
                            if ", usually" in label.lower() or "usually" in label.lower():
                                best_label = label
                                break
                            # Also check for "currently"
                            if "currently" in label.lower():
                                best_label = label
                                break
                            # Otherwise use first valid one
                            if best_label is None and "% busy" in label.lower():
                                best_label = label
                    
                    if best_label:
                        live_percent, typical_percent = parse_busyness_text(best_label)
                        
                        await browser.close()
                        return BusynessData(
                            location_id=location_id,
                            live_percent=live_percent,
                            typical_percent=typical_percent,
                            raw_text=best_label,
                            error=None
                        )
                
                # Try alternative selectors for busyness data
                # Sometimes google shows it in different elements
                page_content = await page.content()
                busy_match = re.search(r'(\d+)%\s*busy', page_content, re.IGNORECASE)
                
                if busy_match:
                    await browser.close()
                    return BusynessData(
                        location_id=location_id,
                        live_percent=int(busy_match.group(1)),
                        typical_percent=None,
                        raw_text=busy_match.group(0),
                        error=None
                    )
                
                await browser.close()
                return BusynessData(
                    location_id=location_id,
                    live_percent=None,
                    typical_percent=None,
                    raw_text=None,
                    error="No busyness data found (location may be closed or data unavailable)"
                )
                
        except PlaywrightTimeout as e:
            logger.warning(f"[{location_id}] Timeout with proxy {proxy}: {e}")
            if attempt < max_retries:
                continue
            return BusynessData(
                location_id=location_id,
                live_percent=None,
                typical_percent=None,
                raw_text=None,
                error=f"Timeout: {str(e)}"
            )
        except Exception as e:
            logger.warning(f"[{location_id}] Error with proxy {proxy}: {e}")
            if attempt < max_retries:
                continue
            return BusynessData(
                location_id=location_id,
                live_percent=None,
                typical_percent=None,
                raw_text=None,
                error=f"Error: {str(e)}"
            )
    
    return BusynessData(
        location_id=location_id,
        live_percent=None,
        typical_percent=None,
        raw_text=None,
        error="Max retries exceeded"
    )


async def scrape_locations_batch(locations: list[dict], batch_size: int = 3) -> list[BusynessData]:
    """
    Scrape multiple locations in batches to avoid overwhelming the target.
    
    Args:
        locations: List of location dictionaries with 'url' and 'id' keys
        batch_size: Number of concurrent scrapes per batch
    
    Returns:
        List of BusynessData results
    """
    results = []
    
    for i in range(0, len(locations), batch_size):
        batch = locations[i:i + batch_size]
        tasks = [
            scrape_location(loc["url"], loc["id"])
            for loc in batch
        ]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)
        
        # Wait between batches
        if i + batch_size < len(locations):
            await asyncio.sleep(random.uniform(3, 7))
    
    return results
