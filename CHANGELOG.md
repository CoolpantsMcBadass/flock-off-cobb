# Changelog

All notable changes to the Flock Off Cobb site are recorded here. Entries are kept short;
the long-form reasoning behind older entries is in git history.

## 2026-08-25

### Added
- **Week of Action thank-you carousel** in the hero flyer, replacing the retired schedule flyer. Two slides, prev/next arrows, two dots, left/right arrow keys, no wrapping (end buttons disable). Each change announces "Slide 1 of 2" through the existing `.flyer-status` live region.
- Slides are the clean originals (`assets/week-recap-1.webp`, `-2.webp`, 1000px, 144KB + 108KB) rather than the screenshots they arrived as, which had Instagram's own arrows and dots baked into the pixels.
- **Four Cobb County PD town halls on Flock** on the event bars: Thu Aug 27 at Milford Recreation Center, Mon Aug 31 at Sewell Mill Library, Tue Sep 1 at West Cobb Senior Center, Tue Sep 15 at North Cobb Senior Center. All 6:30 to 8 PM. One series run four times, so `name` is shared and the venue tells them apart.
- The event strip now prints `where`. It was a declared field nothing rendered, which was fine with one event and isn't when four share a name and a time.
- **A card for events with no poster**, since most events are announced as prose, not a flyer: what the meeting is, the venue, the street address, the date and time. It repeats the date and time on purpose, because the bar's title is one ellipsised line and a long name eats the time first.
- **A recent-posts strip in step 5** of Join the Campaign, four cards driven by `assets/posts.json`. A missing, empty or malformed file hides the strip and leaves step 5 untouched, so it's safe to leave broken.
- `dev/add-post.py` adds a post: reads the public embed page, pulls the picture and its dimensions, writes a 640px WebP into `assets/posts/`, and upserts the entry keyed on post URL. Four posts came to 224KB against ~1.1MB of originals.
- The posts strip swipes on a phone. Below 760px it becomes a scroll-snap row of 80%-width cards, so the strip is one screen rather than four. The 80% is deliberate: the peek of the next card is the only thing saying there's more.

### Changed
- `ENDS` moves to **11:59 PM ET Thu 27 Aug 2026**. Slide 2 says "showing up at the Flock town hall meeting THIS THURSDAY", so the flyer is wrong the moment that Thursday passes. The three later town halls are carried correctly by the event bars.
- Burst label reads "Thank you, Cobb County! / Week of Action" instead of the schedule's dates.
- Clicking either event bar opens **all four town halls in date order**, not just the one the click landed on. A lap of four is 108 seconds, so aiming at one meant waiting for it to come round. `eventAt()` and its hit-testing are gone, along with `byId`, `clip()` and `current`.
- The soonest unfinished event is accented in red (rule, countdown, venue) so the list doesn't need reading end to end. `nextUp()` returns null once everything is over rather than falling back to the first row.
- A `note` shared by every live event is hoisted to the top of the panel instead of repeating on all four rows. Only when they all match.
- Events drop out of the panel as well as the tape as they retire, and an open panel keeps up with the clock. The 30-second tick calls `refresh()`, which rebuilds a closed bar but swaps contents in place on an open one, so a dropdown no longer slams shut as the list changes under the reader.
- The next-up accent moves in `paintCountdowns()` rather than being set once when the panel is filled, so the accent and the countdown are always reading the same clock.
- The town hall description drops "Safety" (company branding, not the name) and "safeguarded" (the exact claim the campaign disputes).

### Fixed
- **The hero flyer never rewound to slide 1 on a phone.** The guard tested `hovering` bare, and on a touch screen that's permanently true: a tap fires a synthetic `mouseenter` before the click and no `mouseleave` ever follows, so the flag latches on. Now gated on `hoverable.matches && hovering`, like every other read of that flag. It hid from every simulation because a dispatched click fires no `mouseenter`; reproducing it meant dispatching one on purpose.
- **`overflow-x:auto` alone did not make the posts strip scroll.** `.step` is a grid item and its text column is a flex item; both default to `min-width:auto` and refuse to shrink below their content, so the box grew to 456px on a 390px screen instead of scrolling. `.step, .step > div{min-width:0}` fixes it. Both links in the chain need it.
- **Two colours from the dark step box bled onto the paper cards.** `.step p` is pale cream and `.step a` is yellow, and both beat a bare `.igcap` or `.igcard`. Every colour on the card is now stated and the selectors are two classes deep. Second time this trap has been hit.
- **The venue headline on the event card rendered invisible, paper on paper.** `.ebar-card` set no `color`, so it inherited the bar's light-on-ink type. Caught on screen, not by reading.
- The mobile four-line caption clamp had never applied. It was a bare `.igcap`, and bumping the base rule to `.igcard .igcap` made the base more specific, so the phone kept the three-line clamp.
- **The tape scrolled roughly six times too fast with four events on it.** Lap time only equals speed while the run is a constant width, so the stylesheet's fixed 22.6s lap made a four-event run move four times as far per second (measured: 172 px/s against the single event's 27.9). Duration now derives from measured run width against a constant `TAPE_SPEED`, set to 36 px/s. That's the one number to turn. Re-paced on resize (type shrinks at 520px) and on `document.fonts.ready` (Space Mono is wider than the fallback).
- Pacing ran *before* the countdowns were painted, so the lap was sized for a narrower tape and sped up every time an event retired (39.4 px/s instead of 36). Both `build()` and `refresh()` now pace after painting.
- The picture box on posts cards is a fixed 4:5 with `object-fit:cover`, since the strip mixes 4:5 stills with 9:16 reels and unequal heights break the caption alignment.

### Removed
- The five day-ticks, their `DONE_AT` schedule, and the now-unused `DAYS` array. They belonged to the week's schedule artwork.

### Notes
- The carousel controls are **siblings** of `.flyer-btn`, not children. The toggle is one big `<button>` wrapping the whole sheet, so paging buttons inside it would be buttons inside a button. `.flyer-nav` sits alongside and is laid back over the sheet by carrying the button's width, rotation and transform origin. Each paging action needs `markOpen()`, or the dwell clock runs out and the next click reads as an abandon.
- Slides cross-fade rather than slide, because `.flyer-plate` is already being scaled by `--plate-s` and a nested second transform is a fight nobody wins.
- `--caption` and `--alt` are deliberately not scraped. **Describe the picture, not the post's subject**: the first pass got three of four wrong by paraphrasing what each post was about.
- `add-post.py` is a hand-run helper, not a pipeline. A scheduled job hitting Instagram from a datacenter IP is what risks the account. Instagram will reshape the embed page eventually; the fallback is saving a picture by hand and editing `posts.json`.
- Why hand-curated: Instagram's Basic Display API shut off in September 2024, its replacement needs a Business/Creator conversion, and an embed widget puts Meta's tracking in front of every visitor on a site whose whole argument is against unconsented tracking.
- Worth knowing before adding a fifth event: a longer bill means a longer lap. At four events a full cycle is ~2m19s, so any one hall is on screen about a quarter of the time. That's survivable because the run is built in date order and the tape starts at `translateX(0)`, so a fresh load opens on the soonest event. It stops being survivable at eight.

### Verified
- Retirement is 4 hours after each `end`, so a hall finishing at 8 PM drops at midnight. Checked against real data at ten instants across the whole run, including past the last retirement where the bars hide themselves. Every printed weekday matches the declared `[y, monthIndex, day]`, which is the cross-check that catches an off-by-one month.
- Both bars at desktop and at 390px in `dev/mobile-preview.html`. The extension's first synthetic click after a navigation doesn't reach the page, which reads exactly like a broken bar. The bar is fine; the harness needs the second click.

## 2026-08-17

### Changed
- The Week of Action flyer is the updated artwork. Only Tuesday changed: the Smyrna City Council meeting is now DeFlock Further at 45 South Avenue Marietta, with free tickets on Eventbrite, matching what the event bars already carried.
- The `alt` text was rewritten for that day. It's the only version of the schedule a screen reader gets, so a flyer swap that leaves it alone publishes last week's plan to the people who can least check it. (The artwork prints "Get free tickets n Eventbrite"; the alt text says "on".)
- The event poster is framed like every other piece of artwork on the site: 3px ink outline and the same hard offset shadow, thin rather than the hero's 5px. The panel gained 6px of bottom padding as the shadow's room.
- Both event bars scroll half again as fast, 34s a lap down to 22.6s.

### Fixed
- **On a real iPhone the event bar wouldn't close by tapping the strip that opened it**: it closed and reopened in one gesture. Touch hardware delivers a second click from the same tap, and the two paths through the click handler weren't symmetric about it. Every state change now stamps a clock, and clicks arriving within 450ms are treated as the gesture's own echo. No amount of synthetic tapping reproduces this; Playwright's WebKit delivers exactly one click per `tap()`.

### Verified
- Nothing else needed touching. New artwork is 1080×1350 like the old one so `--ar` stays at `.8`; the day tabs sit within 2px vertically so the tick positions hold; the dates are unchanged so `DONE_AT` and `ENDS` stay. Checked in real WebKit with the clock frozen at four instants, no page errors.

## 2026-08-14

### Added
- **An event bar for dated events, directly under the nav**, carrying the DeFlock Cobb Live Info Session on Tue Aug 18. It's there because that's the only place on the page that's high on a phone: measured in WebKit at iPhone 13 size, the hero art and flyer fill the whole first screen, putting the h1 at 1.23 screens and the old ticker at 1.96. Under the nav is y=60 at every width. It scrolls away rather than sticking, since a second pinned band would cost 44px of a 664px viewport forever.
- Built for more than one event from the start. The tape is generated from an `EVENTS` array and each event is its own segment, so which poster opens depends on which segment the click landed on. That's also why the tape stops dead on `pointerdown`: a target moving at 30 seconds a lap can't be aimed at fairly.
- **Events retire themselves.** Each entry has a `linger` in hours (6 here), so a session finishing at 10 PM stays up until 4 AM reading "Just happened" rather than claiming to be live. To add an event, add an entry; to retire one, do nothing. Once nothing is left the bar hides itself. Checked by freezing the clock at seven instants across the week.
- Opening is the tape running out: the strip accelerates off to the left as though the reel ended, and what's behind it is the poster. The panel is in the flow rather than overlaid, which makes this an accordion instead of a modal, with no scrim and no focus trap to get wrong.
- The countdown is days only and counts whole Eastern calendar days rather than 24-hour chunks, so the day before reads "Tomorrow" all evening. Same DST-correct `zoned()` helper as the council countdowns, because two clocks on one page must not disagree about what day it is.

### Changed
- **Two event bars now**, the second where the slogan ticker used to sit below the hero. Two instances rather than two copies: one set of events, one clock, one set of rules, rendered into every `.ebar-live`. They open and close independently and each carries its own panel id.
- The strip lifts under the cursor as well as stopping. The bar is full bleed, so the site's usual `translate(-2px,-2px)` and offset shadow can't work; it lifts straight up and its rule thickens from 3px to 6px, red to yellow. `.ebar` decides the hover, not the button, because a hit region that shrinks when it reacts flickers.
- Anything closes an open bar now, poster included. Opening scrolls the bar into view, which slides the strip out from under the pointer, so the obvious second click was landing on the one part that ignored it.
- The strip says "Click for info" / "Tap for info" in the space the address used to hold. The address is on the poster and in its alt text, which is where someone actually wants it.
- The poster comes down over the section below instead of pushing it, so the bar's 47px stays the only room any of it takes in the layout. What comes down is the flyer alone, no ground and no frame, so the page is covered by a poster rather than by a black box holding a poster.
- The sheet drops rather than fades: held one sheet-height above at rest and travelling down on the same duration and curve as the panel's height, so its bottom edge rides the panel's growing edge the whole way.
- Link buttons moved onto the sheet, parked by a per-event `linksAt` on the strip of artwork that already prints the same URLs. The offset belongs to the event because every flyer puts its furniture somewhere different; the default covered the venue address.

### Fixed
- Under `prefers-reduced-motion` the bar came up empty. Nothing scrolls there, so the static title is the payload, but the title was only written when a poster opened. It's now built up front and kept current by the same pass that paints countdowns.
- The bar's red rule moved from `.ebar` to `.ebar-btn`. The panel hangs off `.ebar` at `top:100%`, which resolves against the padding box and would have started the poster over its own rule. Declaring it in its own rule looked like it worked but didn't: the button's `border:0` sets `border-style:none`, and that computes every border width to 0 regardless of what a later rule asks for.

### Removed
- The slogan ticker, its rules, its marquee keyframes and its red ✕ separators. Its six lines (no warrant, no oversight, no consent, shared with ICE, hackable in under a minute, logins found on the dark web) aren't anywhere else on the page and are worth finding a home for.

### Added (hero flyer arrival)
- The flyer arrives a second after the page rather than being there from the first frame: a dot, then spikes out of it into the burst, the same way it comes back after a pop. `startReform()` now takes its delay and finisher as arguments.
- While it waits it's `visibility:hidden` rather than `[hidden]`, so the hero is laid out around it from first paint and nothing shifts when it lands. Hidden visibility also keeps it out of hit-testing and the tab order. The clock starts when the script runs, not on `load`, which waits on 800KB of hero artwork.
- Anything aimed at the flyer during the 260ms arrival ends it on the spot, since the open it's about to trigger owns the same path. Verified in both engines including a tap and a hover landing mid-arrival.

## 2026-08-13

### Added
- **iPhones get the morph too**, driven from script since the CSS `d` property doesn't exist in WebKit. Both shapes carry the same 32 points in the same order, so interpolating by hand is the same arithmetic. Rolled shape comes off each path's `d` attribute, open shape off the custom property the CSS rule would have used, so `dev/morph.py` remains the only thing that writes geometry.
- One implementation covers both engines: browsers with CSS `d` read `--burst-d` (an attribute would lose to the stylesheet), WebKit reads the attribute. Script writes both every frame.
- That loop reads its position back from the window's height each frame rather than running a second clock, so nothing can drift out of step. Open, quiet close, pop, and reduced motion are each just a different way for that height to move. Idles out after ~12 still frames.
- **The flyer pops shut instead of rolling back up.** The sheet is simply gone, leaving a fine mist: 26 ink dots between 4 and 10px, each flicking outward along its edge's normal on a few ms of stagger, none travelling further than ~35px, over in a third of a second. Suppressed under `prefers-reduced-motion`.
- Two louder treatments were tried and dropped, recorded so nobody reaches for them again: a comic starburst blown over the sheet (far too loud, fought the artwork) and the 4px frame lifting off as a swelling skin (better, still too much for a panel closing). `dev/pop-options.html` is the bench.
- The space the flyer occupied recedes over .25s instead of collapsing in a frame, and waits 125ms before it begins. An instant collapse yanked the page up ~300px while the mist was still tracing the sheet's outline; the pause is what makes the gap feel vacated rather than reclaimed.
- Clicking pops it on desktop, not just tapping on a phone. Hover has usually already opened the sheet, so "is it open" can't just be the `is-open` class, and an `is-dismissed` latch takes the hover rules out until the pointer actually leaves.
- A click skips the 250ms dwell on the desktop path. Clicking a `<button>` focuses it and `focusin` fires before `click`, so the very click that closes the flyer was resetting the dwell clock a moment before the handler read it. A phone keeps its dwell, since there a tap is both open and close.
- The button waits .6s after the pop before reforming, and assembles itself: a dot fades in over 120ms, then spikes grow out of it over 180ms. The dot is derived rather than drawn (every point pulled back onto a small ellipse along its own ray), so there's no third shape to keep in step.

### Fixed
- **Tapping the open flyer on an iPhone shrank it and left it open, with no pop.** `:focus-visible` was the cause: WebKit matches it after a tap on a button, Chrome doesn't, so the focus rule reasserted the open state after the class came off. **This is the third time this bug arrived in a different costume** (`activeElement`, then `:focus-within`, then `:focus-visible`), each fix verified in Chrome, where the difference can't show. The browser is no longer asked: the last input before a focus decides whether it counts as keyboard.
- With Reduce Motion on, the flyer went dead to the touch for 2+ seconds after every close. The reform ends the pop and declines to run under reduced motion, so nothing removed `is-popping` and every open-state selector is gated on `:not(.is-popping)`. `startReform()` now reports whether it took ownership. The stalled-rAF backstop came down from 2.2s to 1.4s.
- **The flyer was invisible on iPhones.** WebKit doesn't implement CSS `d`, and the three morphing paths carried no `d` attribute at all, so the burst had no shape and the clipPath was empty. An empty clipPath clips everything, so the poster went too. The rolled shape is now a plain attribute on each path, which is the floor every browser gets.
- Where CSS `d` is missing the flyer falls back to its pre-morph behaviour rather than a half-drawn version of it. `dev/no-d.html` renders that branch in Chrome so it can be looked at without a device.
- The fallback's `:hover` rules went behind the same `@media (hover:hover) and (min-width:861px)` guard as the real open-state rules. Without it, iOS keeping `:hover` stuck on the last-tapped element left a bordered empty box where the button used to be, on every tap after the first.
- **The flyer no longer fights itself on its own edge.** The tilt lived on `.flyer`, the element deciding `:hover`, so the hit region changed shape with the state: a cursor in a 5px sliver at x 472-476 hovered while closed and missed once open, and closing swept the bottom edge down over the hero buttons. The tilt moved to `.flyer-btn` and an unrotated pad (`.flyer::before`, inset -12px) now decides hover. **Lasting rule: anything that changes the flyer's shape belongs on the button or below, never on `.flyer`.** `dev/hover-stability.js` reruns the 320-point scans.
- The pop's timings moved out of `.is-popping` and into the closed state, which is where a close reads them from anyway. A transition reads its timing from the state it's heading into, so the closed rules are now the closing behaviour. The class is left doing one job: holding the rolled burst back until the sheet has gone, and adding the droplets.
- The unroll was choppy. The sheet was laid out at rolled width and grown, which rescales a 1080×1350 JPEG every frame. It's now laid out at open width and scaled down while rolled, so the image is rastered once and the compositor does the scaling.
- The burst was being redrawn every frame too. Its width is now pinned to the rolled width, the only width it's ever visible at.

### Changed
- **The jagged edge becomes the flyer's edge.** One path draws the outline the whole way through: the comic burst while rolled, the sheet's frame when open, and every shape between, with the spikes retracting along their own rays. The window consequently never draws a frame at all; its border is a transparent 4px spacer.
- Three things that had to line up: both shapes carry the same 32 points in the same order (CSS `d` won't interpolate otherwise) with the nearest point to each corner snapped onto it so the rectangle isn't chamfered; the burst's box became the window's box so the viewBox maps onto the sheet exactly; and `drop-shadow` came off, replaced by a second copy of the path offset 6px in CSS pixels. That last one matters twice: a filter over the whole sheet is expensive enough to stutter at 60fps, and a CSS-pixel offset stays a true 6px instead of being squeezed as the box changes proportion.
- Artwork now appears while the edge is still morphing, clipped to the very shape the outline is drawing. It starts at 60ms and is full by 250ms, against 260ms and 470ms before. **Three copies of the shape are kept in step** (outline, shadow, clip), all emitted by `dev/morph.py`.
- The unroll runs on one clock and one curve. Width, height, sheet and burst each had their own duration and easing (.3s to .6s), which reads as choppy even when no frames drop; they now share `--dur` and `--ease`.
- **Tapping the open flyer on a phone now pops it.** Two touch-only behaviours were breaking it: a tap focuses the button, so `:focus-within` silently held the sheet open (now keyed off `:has(:focus-visible)`); and a tap fires `mouseenter` before `click`, which called `markOpen()` and reset the dwell clock a moment before the click handler read it. `markOpen()` now runs from `mouseenter` only where hovering is what opens it. Verified with fifteen real tap-open/tap-close pairs in `dev/mobile-preview.html`.
- A close only counts as a pop if the sheet was open for 250ms first. Under that, `.is-soft-close` runs the unroll backwards over .25s with no droplets. A close is one-shot: `openedAt` is cleared on commit so the trailing `mouseleave` doesn't fire a second burst over empty space.
- The flyer is inert while the pop plays, so hover, focus and tap all do nothing for that half second. A tap in that window is ignored rather than queued.

### Removed
- **The curled bottom edge.** A 10px shaded strip stood in for paper curling where it had unwound from, which made sense while opening was a literal unroll. Four replacements were built and compared in `dev/curl-options.html` and the sheet simply stopping square won.

## 2026-08-12

### Added
- **National Week of Action flyer** (`assets/week-of-action.jpg`) in the hero. Closed, it's a comic exclamation burst in `--yellow` with an ink outline and offset shadow, tilted a couple of degrees. Hovering pops the burst and unrolls the sheet behind it, growing from 250px to 500px wide. The burst is an SVG path stretched with `preserveAspectRatio="none"` and kept to an even outline weight by `vector-effect="non-scaling-stroke"`.
- It also opens on keyboard focus and on tap. It's a real `<button>` carrying `aria-expanded`, the contents are described in the image alt text, Escape closes it, and a click outside rolls it up. Under `prefers-reduced-motion` the states still change without the animation.
- Opening scrolls it into view: centred, or pinned under the nav when the sheet is taller than the screen, and nothing at all when it already fits. The open height is derived up front so the scroll runs alongside the unroll rather than after it.
- **Days are crossed off as they pass.** Each day gets a green comic tick struck across its tab at midnight ET the morning after. Ticks already earned are drawn on load and any still to come are scheduled, so a page left open overnight crosses the day off by itself. A visually hidden line names the finished days, since the artwork's alt text can't change.
- The flyer retires itself at 11:59 PM ET on Sun 2026-08-23, after which the hero returns to normal without anyone editing the page.

### Changed
- **The flyer artwork is recoloured into the site palette**, done in HSV so every pixel keeps its own brightness and only hue and saturation move, preserving gradients, dot texture and the crow. The saturated pixels sit in two clusters at 11° and 45°; the hues between them are antialiased edges, not a third colour, so hue is remapped through a lookup table that ramps across the gap rather than leaving a fringe. Only the copy in `assets/` is recoloured, so the version posted to social stays as the artist made it.

### Notes
- The rolled band is its own element rather than a crop of the flyer's header: the title and wordmark overlap horizontally (x790 vs x770), so no vertical cut separates them.
- Proportions come from four CSS variables on `.flyer`: `--ar` (sheet ratio), `--roll-h` (band height), `--fw` / `--fw-open`. A different flyer needs `--ar` retuned and the band's two lines edited, nothing else.
- On narrow screens the flyer leaves the absolute position and becomes a centred block above the headline, where it only unrolls rather than growing. That needs `position:relative` rather than `static` (z-index does nothing on a static box), with `top`/`right` cleared alongside it.
- Hover opening is gated on `(hover:hover) and (min-width:861px)`, not pointer type alone. A narrow desktop window gets the phone layout, whose opening is meant to scroll the sheet into view.

## 2026-08-04

### Added
- **Full councilmember contacts for every Cobb city.** Acworth, Austell, Kennesaw, Mableton, Powder Springs and Smyrna join Marietta with name, seat, direct phone and email for the mayor and every councilmember: 40 newly added officials, 48 across all seven cities. Every entry verified against the city's own site on the day of the change.
- **City councils are click-to-expand panels.** The flat "cities" grid became `<details>` accordions, one per city, alphabetical and collapsed by default. The summary keeps the city name, meeting schedule and next-meeting countdown.
- **Ward/district address lookups** for the four cities that elect by ward: Austell (1-4), Mableton (1-6), Powder Springs (1-3), Smyrna (1-7). Same forgiving Nominatim geocoder and client-side point-in-polygon test as the Cobb and Marietta lookups, against four new GeoJSON boundary files. Refresh recipes are in the README.
- **"Which district/ward am I in?"** on the officials bands: the Cobb band returns your commission district and commissioner, the Marietta band your ward and councilmember, and the matching card is highlighted. Addresses outside a jurisdiction get a clear message. No address is stored. Tested across all four districts and all seven wards.
- **Marietta City Council subsection** in Reach Cobb Officials, with the mayor plus all seven ward councilmembers, each verified against their individual mariettaga.gov profile.

### Changed
- Marietta folded into the accordion list, so the whole section reads as one consistent list.
- **Highlight targeting is scoped per city.** Cards use a single `data-seat` attribute and each lookup declares a `scope` container in `CFG`, so five ward lookups coexist without highlighting each other's councilmembers.
- Acworth and Kennesaw get no address lookup and say so: both elect their entire council at large.
- Smyrna's Ward 7 corrected to Rickey N. Oglesby Jr. (elected 2024), from a stale third-party listing.
- Resources → Other Communities: [DeFlock Cherokee](https://deflockcherokee.com/), the campaign in the county directly north of Cobb.
- **Em-dashes removed from the copy again**, having drifted back since the June pass. Six were user-visible, two more in comments. Deliberately kept: the en-dash in the "Flock Off – Cobb" wordmark and the `Jul–Sep` range in a comment.

### Notes
- Acworth's Board of Aldermen meets Thursdays at 7 PM but not on a fixed week, so it has no countdown. The caveat line says this.

## 2026-07-06

### Changed
- Hero art replaced with a new @mind_invader_comics piece (`assets/deflockchicken.jpg`), alt text updated to match.
- The original bird art moved to the footer as a tilted poster: paper-white frame, red offset shadow, straightens on hover, lazy-loaded, and clicking it returns to the top of the page.

## 2026-06-27

### Added
- GoatCounter analytics (no cookies, no IP retention, no cross-site tracking) via a small async beacon. Dashboard at deflockcobb.goatcounter.com.

### Removed
- Resources cleanup: the broken top-level Flock transparency portal, the unowned Google-Docs resource doc, and two links duplicating entries already in the same column.

## 2026-06-26

### Added
- **Deployed to https://deflockcobb.com** (GitHub Pages). `CNAME` added; DNS is four A records to GitHub's Pages IPs (185.199.108-111.153, "DNS only" on Cloudflare) plus a `www` CNAME. HTTPS enforced.
- Floating social cluster (Instagram, TikTok, Facebook group) fixed bottom-right, with a scroll-driven inertial sway. Becomes a bottom bar on mobile, disabled under `prefers-reduced-motion`.
- A 5th step in Join the Campaign, "Follow us on social".
- A teal status note on the Mableton card: newly incorporated, no active Flock contract yet.
- Resources, all links confirmed: EFF on Georgia school-residency searches, Cherokee County ALPR misuse, Atlanta PD ICE searches, the Dunwoody contract, and Georgia's ALPR statute (§ 35-1-22).

### Changed
- Nav wordmark → "DEFLOCK COBB" to match the domain. The hero headline stays "Flock Off – Cobb".
- "Take Action" renamed to "Join the Campaign", with an intro pointing people to deflockcobb@proton.me.
- `<title>`, `og:title`, `canonical` and `og:url` updated to deflockcobb.com. README deploy notes rewritten.
- Trimmed Resources to Georgia plus national pieces, removing items tied to other localities. With no lawsuits left, "Lawsuits & Legal" → "Know the Law".
- Removed all ACLU resources.

## 2026-06-20

### Added
- **Interactive map** with a draggable home pin. A live readout shows how many ALPR cameras sit within 1 mile and the distance to the nearest, with a dashed 1-mile ring. Counts come from the real DeFlock camera data already on the map.
- **Address lookup for the map**: type an address or ZIP to geocode it (OpenStreetMap Nominatim, no API key) and drop the pin there. The readout stays hidden behind a prompt until a pin is placed. Address is not stored.
- **Live "next meeting" countdown** on each city card, computed client-side from each council's recurring rule, locked to America/New_York with DST-correct math, including the Powder Springs July-September "3rd Monday only" exception. No backend and no ongoing maintenance.
- A caveat note under the city grid: countdowns are estimates, confirm via the agenda link.
- Subtle risograph misregistration on Anton headings: red/teal channel split on hover, hover-capable devices only.

### Changed
- Map dataset expanded from the Cobb-area bounding box (2,109 points) to the northern half of Georgia (6,878 points), re-pulled from OpenStreetMap via Overpass. `assets/cobb-cameras.geojson` → `assets/ga-alpr-cameras.geojson`. Canvas renderer (`preferCanvas`) and `minZoom` 7 to stay smooth zoomed out.
- Art credit now reads "Art by Marietta artist @mind_invader_comics".

### Fixed
- **Address lookup is far more forgiving.** It normalises whitespace and stray commas, then falls back through looser variants: strips apartment/unit/suite tokens (which made the geocoder return nothing) and, the big one, handles a street whose mailing city isn't its OSM administrative city (a "Marietta, GA" address actually in unincorporated Cobb). The original query is always tried first, so addresses that already worked are unaffected.
- Cobb Board of Commissioners schedule corrected to "2nd Tuesday at 9 AM and 4th Tuesday at 7 PM" (the 2nd-Tuesday session is a morning meeting).
- Powder Springs City Council corrected to "1st & 3rd Monday, 7 PM" (wrong day of week and a missing meeting).

### Verified (no change needed)
- All five Cobb commissioners' names, districts, phones and emails match the county's official page.
- Council schedules for Austell, Kennesaw, Mableton, Smyrna and Marietta are accurate.
- All 17 outbound links resolve and load.
