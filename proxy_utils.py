import asyncio
import random
import aiohttp
import logging
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyManager:
    """Manages fetching, validating, and rotating free proxies."""
    
    SOURCES = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
    ]

    def __init__(self):
        self.proxies: List[str] = []
        self.last_fetch = 0
        self._lock = None

    def _get_lock(self):
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def fetch_proxies(self) -> List[str]:
        """Fetch fresh proxies and limit the list size."""
        all_proxies = set()
        async with aiohttp.ClientSession() as session:
            tasks = []
            for source in self.SOURCES:
                tasks.append(self._fetch_source(session, source))
            
            results = await asyncio.gather(*tasks)
            for res in results:
                all_proxies.update(res)
        
        proxy_list = list(all_proxies)
        random.shuffle(proxy_list)
        # Limit to 1000 proxies to avoid massive validation times
        self.proxies = proxy_list[:1000]
        logger.info(f"Initialized pool with {len(self.proxies)} proxies.")
        return self.proxies

    async def _fetch_source(self, session: aiohttp.ClientSession, url: str) -> List[str]:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    return [p.strip() for p in text.split('\n') if p.strip() and ':' in p]
        except Exception as e:
            logger.warning(f"Failed to fetch from {url}: {e}")
        return []

    async def validate_proxy(self, proxy: str) -> Optional[str]:
        """Test a proxy against a simple endpoint."""
        url = "http://www.google.com"
        proxy_url = f"http://{proxy}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, proxy=proxy_url, timeout=5) as response:
                    if response.status == 200:
                        return proxy_url
        except Exception:
            pass
        return None

    async def get_valid_proxy(self, max_attempts: int = 50, batch_size: int = 10) -> Optional[str]:
        """Get a single validated proxy, testing in batches."""
        async with self._get_lock():
            if not self.proxies:
                await self.fetch_proxies()

            attempts = 0
            while self.proxies and attempts < max_attempts:
                # Take a batch of proxies to validate in parallel
                batch = [self.proxies.pop() for _ in range(min(len(self.proxies), batch_size))]
                attempts += len(batch)
                
                tasks = [self.validate_proxy(p) for p in batch]
                results = await asyncio.gather(*tasks)
                
                # Return the first one that passed
                for r in results:
                    if r:
                        logger.info(f"Found valid proxy: {r}")
                        return r
            
            # If we ran out, re-fetch
            if attempts >= max_attempts or not self.proxies:
                await self.fetch_proxies()
                if self.proxies:
                    return await self.get_valid_proxy(max_attempts=20)
            
        return None

# Singleton instance
proxy_manager = ProxyManager()
