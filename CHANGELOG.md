# Changelog

All notable changes to the Flock Off Cobb site are recorded here.

## 2026-06-20

### Fixed
- Address lookup is far more forgiving: it now normalizes whitespace and stray/duplicate commas, and falls back through looser query variants when the first try fails — stripping apartment/unit/suite tokens (which made the geocoder return nothing) and adding a "Georgia, USA" hint for inputs with no state. Bumped to 5 candidate results. The original query is always tried first, so good addresses are unaffected.

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
