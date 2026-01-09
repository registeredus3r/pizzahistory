"""Debug WITHOUT clicking popup - to test if that's the issue."""
import asyncio
from playwright.async_api import async_playwright

async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()
        
        url = "https://www.google.com/maps/place/Bear+Branch+Tavern/@38.9020863,-77.2663316,17z/data=!3m2!4b1!5s0x89b64bc839307059:0xd6fa84ed7f595e82!4m6!3m5!1s0x89b64b88a592d0a5:0x8d407dbcc0bdb54b!8m2!3d38.9020863!4d-77.2637567!16s%2Fg%2F11j52b3xf9!5m1!1e1?entry=ttu&g_ep=EgoyMDI2MDEwNi4wIKXMDSoASAFQAw%3D%3D"
        
        print("Loading page...")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(8)
        
        # Skip popup dismissal entirely!
        print("Skipping popup dismissal...")
        
        # Just scroll directly with keyboard
        print("Scrolling with keyboard...")
        sidebar = await page.query_selector('[role="main"]')
        if sidebar:
            await sidebar.click()
            await asyncio.sleep(0.3)
        
        for _ in range(8):
            await page.keyboard.press("PageDown")
            await asyncio.sleep(0.2)
        
        await asyncio.sleep(1)
        
        # Check for elements
        elements = await page.query_selector_all('[aria-label*="busy"]')
        print(f"\nFound {len(elements)} elements")
        
        if elements:
            for el in elements[:5]:
                label = await el.get_attribute("aria-label")
                print(f"  - {label}")
        
        await browser.close()

asyncio.run(debug())
