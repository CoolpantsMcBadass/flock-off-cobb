# Changelog

All notable changes to the Flock Off Cobb site are recorded here.

## 2026-08-04

### Added
- Full councilmember contacts for every Cobb city. Acworth, Austell, Kennesaw, Mableton, Powder Springs, and Smyrna join Marietta with name, seat, direct phone, and email for the mayor and every councilmember — 40 newly added officials, 48 across all seven cities. Every entry was verified against the city's own site on the day of the change.
- City councils are now click-to-expand panels. The old flat "cities" grid became a list of `<details>` accordions, one per city, alphabetical and all collapsed by default. The summary row keeps the city name, meeting schedule, and next-meeting countdown; expanding reveals an intro line, an agendas button, the address lookup where one applies, and the councilmember cards.
- Ward/district address lookups for the four cities that elect by ward: Austell (wards 1–4), Mableton (districts 1–6), Powder Springs (wards 1–3), and Smyrna (wards 1–7). Same forgiving Nominatim geocoder and client-side point-in-polygon test as the Cobb and Marietta lookups, against four new boundary files: `assets/austell-wards.geojson`, `assets/mableton-districts.geojson`, `assets/powder-springs-wards.geojson`, and `assets/smyrna-wards.geojson`. Refresh recipes are in the README.
- Marietta rejoined the meeting-countdown schedule (2nd Wednesday, 7 PM), since it now sits in the accordion list with the other cities.

### Changed
- Marietta folded into the accordion. Its standalone dark band, ward lookup, and eight always-visible cards became one panel matching the other six, so the whole section reads as a single consistent list.
- Highlight targeting is now scoped per city. Cards use a single `data-seat` attribute and each lookup declares a `scope` container in `CFG`, so five ward-based lookups coexist without highlighting each other's councilmembers. Replaces the old global `data-district` / `data-ward` attribute lookup.
- Acworth and Kennesaw get no address lookup and say so — both elect their entire council at large, so every member represents every resident. Kennesaw's panel also links the all-council address, kennesawcouncil@kennesaw-ga.gov.
- The section intro no longer says council email lists are still being compiled, since they now are.
- Smyrna's Ward 7 is Rickey N. Oglesby Jr. (elected 2024), corrected from a stale third-party listing that still named the previous councilmember.

- Resources → Other Communities: [DeFlock Cherokee](https://deflockcherokee.com/), the resident campaign against ALPRs, cameras, audio, and drones in Cherokee County, the county directly north of Cobb.

### Notes
- Acworth's Board of Aldermen meets Thursdays at 7 PM but not on a fixed week of the month, so it has no countdown. The caveat line under the accordions says this.

### Added
- "Marietta City Council" subsection in Reach Cobb Officials, below the Cobb Board of Commissioners. Reuses the officials-card layout with a dark header band, an agendas button, and cards for the mayor plus all seven ward councilmembers (name, phone, email). Each entry verified against the member's individual mariettaga.gov profile page. Councilmembers share the main line (770) 794-5526; the mayor and Ward 7 (Goldstein) list their own direct numbers.
- "Which district/ward am I in?" address lookups. Each officials band now has an address box: the Cobb band returns your commission district (1–4) and commissioner; the Marietta band returns your ward (1–7) and councilmember. On a hit, the matching card is highlighted. Uses the same forgiving Nominatim geocoder as the map, then a client-side point-in-polygon test against two new boundary files, `assets/cobb-districts.geojson` (Cobb County GIS) and `assets/marietta-wards.geojson` (City of Marietta GIS), simplified and lazy-loaded on first use. Addresses outside a jurisdiction get a clear "outside city limits / not in a Cobb district" message. No address is stored. Tested end-to-end across all four districts and all seven wards.

### Removed
- Marietta card (and its meeting-countdown entry) from the "cities" grid, now that Marietta has full contacts and a ward lookup in its own subsection above.

## 2026-07-06

### Changed
- Hero art replaced with new @mind_invader_comics piece (`assets/deflockchicken.jpg`, a red robotic chicken with "DeFlock Cobb!" lettering). Alt text updated to match.
- The original bird art (`assets/img0.jpeg`) moved to the footer as a tilted poster between the headline and the CTA column: paper-white frame, red offset shadow, straightens on hover, lazy-loaded, and clicking it returns to the top of the page. Stacks below the CTAs on mobile.

## 2026-06-27

### Added
- GoatCounter analytics (privacy-friendly: no cookies, no IP retention, no cross-site tracking) via a small async beacon before `</body>`. Dashboard at deflockcobb.goatcounter.com.

### Removed
- Resources cleanup, dropping duplicates and dead/uncertain links. Dig Into the Data: the broken top-level Flock transparency portal (Woodstock's working portal stays) and the Google-Docs "full resource doc" (unowned, of unknown provenance). Other Communities: the DeFlock Atlanta tracker and the "EFF on the communities" link, since DeFlock Atlanta and the EFF are already listed in that column.

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
