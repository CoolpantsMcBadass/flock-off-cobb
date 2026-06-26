# Changelog

All notable changes to the Flock Off Cobb site are recorded here.

## 2026-06-26

### Added
- Deployed to the custom domain **https://deflockcobb.com** (GitHub Pages). `CNAME` file added; DNS is four A records to GitHub's Pages IPs (185.199.108–111.153, "DNS only" on Cloudflare) plus a `www` CNAME; HTTPS enforced.
- Floating social cluster (Instagram, TikTok, Facebook group), fixed to the bottom-right, with a scroll-driven inertial sway: still when idle, tugs opposite the scroll direction and springs back to center. Disabled on mobile (becomes a bottom bar) and under prefers-reduced-motion.
- "Join the Campaign" now has a 5th step, "Follow us on social," a full-width box with the three social accounts shown as icon buttons.
- A teal status note on the Mableton city card: newly incorporated with no active Flock contract yet, framed proactively.
- Resources (vetted for mission alignment, all links confirmed): Media Coverage — EFF Georgia school-residency searches, Cherokee County deputies' ALPR misuse, Atlanta PD ICE searches, Dunwoody contract. Lawsuits & Legal — Georgia's ALPR statute (§ 35-1-22) and the ACLU of Georgia contract-terms warning. Other Communities — DeFlock Atlanta's tracker, the ACLU "Get The Flock Out" toolkit, and EFF's wins roundup. Earlier in the day also added four media links and three Georgia/national community links.

### Changed
- Nav brand wordmark → "DEFLOCK COBB" to match the domain (the hero headline stays "Flock Off – Cobb").
- Renamed the "Take Action" section (and its nav link) to "Join the Campaign," with a new intro line pointing people to deflockcobb@proton.me.
- Page `<title>`, `og:title`, and a new `canonical` + `og:url` all updated to deflockcobb.com.
- README deploy notes rewritten for the live domain and DNS setup.
- Trimmed Resources to Georgia plus general/national pieces, removing items tied to other localities: the SF Chronicle article, the Norfolk/San Jose/Oakland lawsuits, the Get The Flock Out (Santa Cruz) campaign, and Oakland Privacy. With no lawsuits left in that column, renamed "Lawsuits & Legal" → "Know the Law." (The Norfolk/San Jose/Oakland references in The Case and The Letter were left in place as supporting content.)
- Removed all ACLU resources (the ACLU of Georgia contract-terms warning and the ACLU "Get The Flock Out" toolkit).

## 2026-06-20

### Fixed
- Address lookup is far more forgiving. It normalizes whitespace and stray/duplicate commas, then falls back through looser query variants when the first try fails: strips apartment/unit/suite tokens (which made the geocoder return nothing), and — the big one — handles the common case where a street's mailing city isn't its OSM administrative city (e.g. a "Marietta, GA" address that actually sits in unincorporated Cobb). It detects the ZIP/state, drops the conflicting city, and trims trailing tokens until the street resolves. The original query is always tried first, so addresses that already worked are unaffected.

### Changed
- Expanded the map's camera dataset from the Cobb-area bounding box (2,109 points) to the northern half of Georgia (6,878 points), re-pulled from OpenStreetMap via Overpass. Renamed `assets/cobb-cameras.geojson` → `assets/ga-alpr-cameras.geojson`. Map now uses a canvas renderer (`preferCanvas`) and a lower `minZoom` (7) to stay smooth and let users zoom out to the regional view.

### Added
- Address lookup for the map: type an address/ZIP to geocode it (OpenStreetMap Nominatim, no API key) and drop the home pin there, flying the map to it. The cameras-within-1-mile readout now stays hidden behind a prompt until a pin is placed — by address search, by clicking the map, or by dragging the pin. Address is not stored.
- Interactive map: a draggable "home" pin (Red Blob Games-style explorable). Drag it anywhere and a live readout shows how many ALPR cameras sit within 1 mile and the distance to the nearest, with a dashed 1-mile radius ring. Counts computed from the real DeFlock camera data already on the map.
- Subtle risograph "misregistration" effect: Anton headings get a red/teal channel split on hover (hover-capable devices only; transition disabled under prefers-reduced-motion).
- Live "next meeting" countdown on each city card (all except Acworth, which has no published recurring schedule). Computed client-side from each council's recurring rule, locked to America/New_York with DST-correct math, including the Powder Springs July–Sept "3rd Monday only" exception. No backend or ongoing maintenance for the regular cadence.
- Caveat note under the city grid: countdowns are estimates; confirm via the agenda link before showing up.

### Changed
- Art credit now reads "Art by Marietta artist @mind_invader_comics" (removed first name) in both the main credit and the footer.

### Fixed
- Cobb Board of Commissioners meeting schedule: corrected from "2nd and 4th Tuesday at 7 PM" to "2nd Tuesday at 9 AM and 4th Tuesday at 7 PM" (the 2nd-Tuesday session is a 9 AM morning meeting, not evening).
- Powder Springs City Council schedule: corrected from "3rd Wednesday, 7 PM" to "1st & 3rd Monday, 7 PM" (wrong day of week and missing the 1st-Monday meeting).

### Verified (no change needed)
- All five Cobb commissioners' names, districts, phone numbers, and emails match the county's official District Commissioners page.
- City council schedules for Austell, Kennesaw, Mableton, Smyrna, and Marietta are accurate.
- All 17 outbound links resolve and load.
