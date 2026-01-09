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
        self.raw_proxies: List[str] = []
        self.validated_proxies: List[str] = []
        self._lock = None
        self._replenishing = False

    def _get_lock(self):
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def fetch_proxies(self) -> None:
        """Fetch fresh proxies from sources and store in raw_proxies."""
        all_proxies = set()
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_source(session, source) for source in self.SOURCES]
            results = await asyncio.gather(*tasks)
            for res in results:
                all_proxies.update(res)
        
        plist = list(all_proxies)
        random.shuffle(plist)
        self.raw_proxies = plist[:2000] # Limit pool
        logger.info(f"Fetched {len(self.raw_proxies)} fresh proxies.")

    async def _fetch_source(self, session: aiohttp.ClientSession, url: str) -> List[str]:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    return [p.strip() for p in text.split('\n') if p.strip() and ':' in p]
        except Exception as e:
            logger.warning(f"Failed to fetch from {url}: {e}")
        return []

    async def validate_proxy(self, session: aiohttp.ClientSession, proxy: str) -> Optional[str]:
        """Test a proxy against https://www.google.com to ensure HTTPS tunnel works."""
        url = "https://www.google.com"
        proxy_url = f"http://{proxy}"
        try:
            async with session.get(url, proxy=proxy_url, timeout=5) as response:
                if response.status == 200:
                    return proxy_url
        except Exception:
            pass
        return None

    async def replenish_validated_pool(self, target_count: int = 5):
        """Finds and validates multiple proxies in parallel to fill the pool."""
        if self._replenishing:
            return
        
        self._replenishing = True
        try:
            if not self.raw_proxies:
                await self.fetch_proxies()

            async with aiohttp.ClientSession() as session:
                batch_size = 50 # Increase parallelism
                while len(self.validated_proxies) < target_count and self.raw_proxies:
                    batch = [self.raw_proxies.pop() for _ in range(min(len(self.raw_proxies), batch_size))]
                    tasks = [self.validate_proxy(session, p) for p in batch]
                    results = await asyncio.gather(*tasks)
                    
                    found = [r for r in results if r]
                    if found:
                        self.validated_proxies.extend(found)
                        logger.info(f"Added {len(found)} validated proxies to pool. Total: {len(self.validated_proxies)}")
                    
        finally:
            self._replenishing = False

    async def get_valid_proxy(self) -> Optional[str]:
        """Returns a validated proxy immediately if available, otherwise waits for replenishment."""
        async with self._get_lock():
            # If we have some, return one and trigger replenishment if low
            if self.validated_proxies:
                proxy = self.validated_proxies.pop()
                if len(self.validated_proxies) < 3:
                    asyncio.create_task(self.replenish_validated_pool())
                return proxy

            # If none validated, wait for a batch to be found
            await self.replenish_validated_pool(target_count=3)
            if self.validated_proxies:
                return self.validated_proxies.pop()
            
        return None

# Singleton instance
proxy_manager = ProxyManager()
