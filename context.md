# Project: Pentagon Pizza Index History - 2026

**Mission:** A year-long OSINT data collection project tracking the correlation between government facility "busyness" and global geopolitical events. At the end of the year, data is visualized, and the famous Pentagon Pizza Index accuracy is calculated.

## 🎯 Primary Goal
Automatically scrape "Live Busyness" data from Google Maps for specific restaurants near sensitive locations (Pentagon, Langley, Mar-a-Lago, and Control Locations) every 15 minutes and store it in a persistent, low-cost cloud architecture.

## 🏗️ Technical Architecture
- **Runner:** GitHub Actions (GHA) - Cron schedule `*/15 * * * *`.
- **Scraper:** Python + Playwright (Headless Chromium).
- **Backend:** Cloudflare Workers (API Gateway).
- **Storage:** - **Hot:** Cloudflare D1 (SQL) for the most recent 30 days.
    - **Cold:** Google Drive (2TB) for long-term archival.
- **Annotation:** OSINT news feeds (Twitter/X, RSS) and estimated DEFCON levels. Kalshi prediction market.

## 📍 Target Locations (Initial List)
1. **Pentagon Area (Arlington, VA):** 
- Domino's Pizza
- Extreme Pizza
- We, The Pizza
- District Pizza Palace
- Papa John's Pizza
- Pizzato Pizza 
- Freddie's Beach Bar (Inverse indicator)
- The Little Gay Pub (Inverse indicator)
2. **Mar-a-Lago Area (West Palm Beach, FL):**
- Lynora's Italian Kitchen
- Pizza De Roma
- Taste of Italy
3. **CIA Area (Langley, VA):**
- Andy's Pizza Tyson's/McLean
- &pizza
- Andy's Pizza Bethesda
4. **Control Locations (Random Areas):**
- Pizza Station (Hayward, CA)
- Mister O1 Extraordinary Pizza Alliance (Fort Worth)
- Mimi's Pizza (Manhattan)
- Due Amici Pizza & Pasta Bar (Tampa)
- Hapa Pizza (Beaverton, OR)
- Pizzeria Portofino (Chicago)

## 💹 Prediction Market Integration
- **Source:** Kalshi Public API (`v2/markets`)
- **Logic:** For every 15-minute cycle, pull the 'Yes' price for top 5 Geopolitical event contracts.
- **Data Column:** `market_probability` (0.0 - 1.0)
- **Goal:** Compare the "Pizza Delta" with "Market Delta" to identify lead-lag relationships.

## 🛠️ Agent Instructions
### 1. Scraping Strategy
- Use **Playwright** with a mobile User-Agent to minimize payload size.
- Target the `aria-label` attribute containing the string "busy" (e.g., `"Currently 85% busy; usually 40% busy"`).
- Implementation must include randomized wait times (1-5 seconds) and stealth headers to avoid Google's bot detection.

### 2. Error Handling
- If a scrape fails, log the error to the GitHub Action console but do not "fail" the build (to ensure the next 15-minute cycle runs).
- Implement a "Retry once" logic for 429 (Too Many Requests) errors.

### 3. Data Schema (Table: `busyness_logs`)
- `id`: Primary Key (Auto-inc)
- `timestamp`: ISO-8601
- `location_id`: String
- `live_percent`: Integer
- `typical_percent`: Integer
- `market_probability`: Float (0.0 - 1.0) (Optional, for later annotation)
- `news_snippet`: Text (Optional, for later annotation)

## 📅 Roadmap (get 1-4 working ASAP)
- **Phase 1 (Current):** Establish "Hello World" scrape on GHA to verify Google Maps accessibility.
- **Phase 2:** Implement Cloudflare Worker API to receive POST requests from GHA.
- **Phase 3:** Create the D1 database schema and connect the Worker.
- **Phase 4:** Build the "Cold Storage" pipeline to move data to Google Drive.
- **Phase 5 (End of Year):** Data visualization and calculation. 

## 📜 Constraints & Ethics
- Frequency must stay at 15 minutes to respect Google's infrastructure and stay within GHA free tier limits (2000 mins/mo).
- All data collected is from public, unauthenticated web surfaces.