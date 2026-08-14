# Flock Off, Cobb

A single-page action site to remove Flock Safety license plate readers from Cobb County, GA.
Modeled on gettheflockout.org, built from the "Flock Off – Cobb" action toolkit.

Plain HTML/CSS/JS — no build step, no dependencies.

## Files
- `index.html` — the entire site (styles + scripts are inline)
- `assets/deflockchicken.jpg` — hero art by @mind_invader_comics
- `assets/img0.jpeg` — original campaign art by @mind_invader_comics, now in the footer
- `assets/ga-alpr-cameras.geojson` — ALPR camera points for the map (northern half of GA)
- `assets/cobb-districts.geojson` — Cobb commission district polygons (from Cobb County GIS)
- `assets/marietta-wards.geojson` — Marietta ward polygons (from City of Marietta GIS)
- `assets/austell-wards.geojson` — Austell ward polygons (wards 1–4)
- `assets/mableton-districts.geojson` — Mableton council district polygons (districts 1–6)
- `assets/powder-springs-wards.geojson` — Powder Springs ward polygons (wards 1–3)
- `assets/smyrna-wards.geojson` — Smyrna ward polygons (wards 1–7)
- `assets/week-of-action.jpg` — the Week of Action flyer shown in the hero

## The hero flyer
The empty space in the hero holds the Week of Action flyer. Closed, it is a comic
exclamation burst naming the event; hovering (on a wide screen), tapping, or tabbing to
it pops the burst and unrolls the whole sheet. It is a `<button>`, so it works from the
keyboard, and the schedule is spelled out in the image `alt` text for screen readers.

The burst (`.flyer-burst`) is its own element rather than a crop of the flyer's own
header. A crop was the obvious approach and it does not work: on this flyer "WEEK OF
ACTION" ends at x790 and the "deflock Cobb" wordmark starts at x770, so no vertical cut
separates the title from the logo and the megaphone. Keeping it separate also means the
closed state can say whatever the next action needs.

It sits outside `.flyer-window`, which clips, so its spikes are not cut off, and before
it in the DOM, so the sheet and its artwork paint over it. The shape is a plain `<path>`
with `preserveAspectRatio="none"` so it stretches to its box, plus
`vector-effect="non-scaling-stroke"` so the outline keeps an even weight while it does.

**The burst is the flyer's edge in both states.** It is not a decoration that gets out of
the way: the same path draws the jagged silhouette while rolled, the sheet's rectangular
frame when open, and every shape in between — see "Morphing the edge" below. So the
window itself never draws a frame at all. Its `border` is a transparent 4px spacer whose
only job is insetting the artwork off the outline; giving it a real one would double the
frame at the end of the unroll and give away that two different things had been drawn.

Everything lives in the `.flyer` rules in the `<style>` block and one short IIFE at the
end of the first `<script>`. The CSS variables on `.flyer` do the work:

| variable | meaning |
| --- | --- |
| `--ar` | the flyer image's width ÷ height (1080×1350 → `.8`) |
| `--roll-h` | height of the burst, and of the closed window behind it |
| `--fw-roll` | rolled width |
| `--fw-open` | unrolled width |
| `--fw` | the current width: `--fw-roll`, re-declared to `--fw-open` in the open state |
| `--dur` / `--ease` | the one clock and curve every part of the unroll runs on |
| `--open-d` | the outline's open shape; see "Morphing the edge" |
| `--plate-w` / `--plate-s` | derived; see below |

To swap in a different flyer, drop the image at `assets/week-of-action.jpg`, set `--ar`
to its ratio, and edit the two lines of text inside `.flyer-burst`. Update the `alt`
text to describe the new schedule too, since that text is the only version a screen
reader gets.

The flyer hides itself once the week is over: the IIFE compares the clock against
`ENDS`, set to 11:59 PM ET on the Sunday after the week, and simply never unhides it
after that. To run it again for a later action, change `ENDS` and the image.

### Morphing the edge
The spikes retract into the sheet's four edges. They do not fade out while a rectangle
fades in underneath, which is what this replaces and which read as a jolt right at the
moment the shape changed. One `<path>` interpolates from the burst to the frame via the
CSS `d` property, so there is only ever one outline on screen.

Three things had to line up for that to work:

- **Matching point counts.** `d` only interpolates between paths with the same commands
  in the same order. The open shape therefore carries the same 32 points as the burst,
  each one being that spike's own point projected straight out onto the rectangle, so
  every spike retracts along its own ray instead of the shape twisting on its way there.
  Nothing lands on a corner by chance, so the nearest point to each of the four is
  snapped onto it — otherwise the "rectangle" ends up with chamfered corners.
  `dev/morph.py` generates both paths; rerun it if the rolled shape ever changes.
- **The burst's box is the window's box.** Not an oversized one of its own, which is what
  it had while it was only a decoration. That way the viewBox maps onto the sheet exactly
  and the open path is simply the viewBox rectangle. The spikes overhang by leaving the
  viewBox, which `overflow:visible` renders.
- **No filter on it.** The shape is redrawn every frame now, and a `drop-shadow` over the
  whole open sheet is the one thing here expensive enough to make that stutter. The
  offset shadow is a second copy of the path painted behind and translated 6px in CSS
  pixels — which also keeps it a true 6px, matching `--shadow`, rather than being
  squeezed by the non-uniform stretch as the box goes from a wide band to a tall sheet.

The sheet also stops square at the bottom now. There used to be a 10px shaded strip under
it standing in for the paper curling where it had unwound from, which made sense while
opening was a literal unroll; with the outline morphing straight into the frame there is
nothing to have unrolled from, and it read as a bar stuck to the bottom. Four
replacements were tried in `dev/curl-options.html` — a properly barrel-shaded roll,
peeling corners, a hanging wave along the bottom edge — and none earned their place.

**The artwork is clipped to the same shape.** `.flyer-window` carries
`clip-path: url(#flyerEdge)`, a `<clipPath clipPathUnits="objectBoundingBox">` holding the
same two shapes again in 0–1 units, morphing on the same clock. That is why the sheet can
be revealed *through* the burst as the spikes retract. Without it the artwork is a
rectangle inside a jagged outline, so it has to wait until the shape is nearly rectangular
before it dares fade in at all — it used to start at 260ms of a 500ms open and not finish
until 470ms, which is why it felt like it arrived after everything else was over. It now
starts at 60ms and is full by 250ms. So there are **three** copies of the shape to keep in
step: the outline, its shadow, and this clip. `dev/morph.py` emits all of them.

The clip is normalised against the border box, which is exactly the box the outline's
viewBox maps onto, so the two register without fudging. It lives inside `.flyer` so it
inherits `--open-dn` and the open-state selectors reach it — as a sibling it would get
neither.

**The rolled shape is also a plain `d` attribute on each of the three paths, and that is
load-bearing.** WebKit does not implement the CSS `d` property, so geometry declared only
in the stylesheet is no geometry at all on an iPhone: the burst had nothing to draw and
the clipPath was empty, and an empty clipPath clips everything, so the poster went with
it. All that survived was the burst's label and the droplets, both plain HTML — which is
exactly what it looks like when someone reports "the flyer is gone on my phone". The
attribute is the floor every browser gets; CSS only ever moves it.

**The morph itself is done in script where the property is missing**, so an iPhone gets
the same thing everything else does. The two shapes carry the same 32 points in the same
order — the condition that made them interpolable to CSS at all — so doing it by hand is
that same arithmetic written out. Each path's rolled shape is read off its own `d`
attribute and its open shape off the custom property the CSS rule would have used, so
there is still exactly one definition of each and `dev/morph.py` stays the only thing
that writes them. The loop sets `js-morph`, which undoes the fallback below.

Worth understanding before touching it: **the loop reads its position back from the
window's height each frame** instead of running a clock beside the stylesheet's. A height
is a fact about what is on screen, not a prediction, so it cannot drift — the open, the
quiet close, the pop with its 125ms hold, and reduced motion collapsing the lot are each
only a different way for that height to move, and every one of them comes out right
without being handled separately. Add a state and there is nothing to update here. The
one derived value is the open height, taken as `plate.offsetWidth + 8` over `--ar`,
because `--fw-open` can be a `min()` that computed style hands back unresolved while the
plate is already laid out at exactly that width.

Where the property is missing **and script never arrives**, `@supports not (d: path(…))`
puts the flyer back the way
it was before the morph rather than leaving it half-drawn: a real frame on the window
(painted only when open, or the rolled state is a paper rectangle over the burst), the
burst pinned at its rolled size and fading out as the sheet unrolls, and no clip. Nothing
else changes — the pop, the droplets, the dwell and the dismiss latch are class and HTML
work. `dev/no-d.html` renders that branch in Chrome; read the gotcha in it before
trusting a measurement.

The `:hover` halves of those fallback rules sit behind the same
`@media(hover:hover) and (min-width:861px)` guard as the real open-state rules, and that
is not decoration. iOS keeps `:hover` stuck on whatever was tapped last, so unguarded
they matched a flyer that was closed — the sheet stayed shut, its own open rules being
inside the media query, while the burst was pinned at opacity 0 and the empty window kept
its frame, leaving a bordered box where the button should be on every tap after the
first. **Anything keyed on `:hover` belongs behind that guard.** Real WebKit is the only
thing that catches this; `npx playwright install webkit` and drive it with
`playwright-core` at `devices['iPhone 13']`, which also reports `CSS.supports('d', …)`
false and so exercises the fallback for real.

The label is pinned to the rolled band rather than centred in the burst, or
it would ride the middle of the sheet downward as the box grows; it fades in the first
30%. It carries no shadow of its own on purpose: the old filter sat on the whole burst,
where the opaque star was the silhouette casting it and the text inside contributed
nothing to that alpha. Put the same filter on the text alone and every glyph casts one.

### Keeping the unroll smooth
Two things made the first version chop. The obvious one is that a 1080×1350 JPEG laid
out at the rolled width and grown to the open width has to be rescaled by the browser on
every single frame. So the sheet is laid out the other way round: `.flyer-plate` is
always `--plate-w` wide (the open width, less the window's two 4px borders) and is
scaled *down* while rolled by `--plate-s`. Same picture, but the image is rastered once
and the compositor does the scaling. Because the scale is `(--fw - 8px) / --plate-w` and
both it and the width run on the same `--dur`/`--ease`, the sheet stays flush inside the
window for the whole unroll rather than drifting against its frame. The second was the
burst redrawing at a new width every frame, fixed by pinning it to `--fw-roll` above.

The rest is timing. Everything used to run on its own duration and curve, which reads as
choppy even when no frames are dropped, so width, height, sheet and burst all take
`var(--dur) var(--ease)`, and the open state declares `--dur: .5s`.

### The tilt does not live on the hover target
`.flyer` decides `:hover`, and **its hit region must never shrink when it opens**, or the
flyer fights itself. The box growing is fine — it only ever gets bigger, leftward and
downward from a fixed top-right anchor, so a point that hovers while closed still hovers
while open. The tilt is the problem, and it caused two separate-looking bugs:

- **Flicker on the edge.** Rotating the closed box about its top-right corner swings the
  right edge ~5px further right than the open box ever reaches. A cursor parked in that
  sliver hovers while closed and misses once open: open, shut, open. Measured against a
  fixed sample grid it was 320 points, all at x 472–476.
- **A shrink instead of a pop when leaving downward onto the hero buttons.** Closing
  snaps the geometry at 100ms but animates the tilt for 260ms, so for the first 100ms a
  *full-size* box is rotating back to −2.2°, and its bottom edge sweeps down over a band
  about 9px deep across the whole width — right where those buttons are. The cursor you
  just left with gets covered again, `mouseenter` fires, `unpop()` strips `.is-popping`,
  and the close falls back to the plain transitions, which is a shrink.

So the tilt sits on `.flyer-btn`, and `.flyer::before` — unrotated, inset −12px, always
larger than the rotated button in either state — is what actually decides `:hover`. 12px
clears the worst bulge (7.3px along the bottom-left while closed) with room to spare.
Both scans read 0 afterwards. `dev/hover-stability.js` reruns them.

The habit worth keeping: anything that changes the flyer's shape belongs on the button or
below, never on `.flyer`.

### Popping it shut
Closing is not the unroll in reverse, and deliberately not an explosion either. It is a
bubble going: the sheet is simply gone, leaving a fine mist of droplets off its perimeter
that flicks outward and vanishes, and the rolled burst is back underneath. There is no
outline, no burst shape and no colour in it at all — 26 ink dots between 4 and 10px, none
travelling further than about 35px from the edge, the whole thing over in a third of a
second. Nothing shrinks and nothing bounces on the way in; both read as retreating, which
is the opposite of a pop.

Two louder treatments were tried first and thrown out, which is worth knowing before
reaching for one again: a comic starburst over the sheet (far too loud, and it fought the
artwork), and the sheet's own frame lifting off as a swelling skin (better, still too
much event for what is only a panel closing).

**The sheet is not part of the pop.** Artwork, frame and shadow all leave on the frame it
closes, and the droplets play over the space they occupied. Nothing is ever seen getting
smaller, because by the time anything moves there is nothing left to see.

**But the space it occupied recedes over .25s rather than in one frame.** That box is
empty by then — no frame, no background, artwork already at opacity 0 — so collapsing it
slowly is invisible in itself, and it is what keeps the pop anchored. On a phone the flyer
sits in the document flow, so an instant collapse yanks everything below it up ~300px
while the droplets are still tracing the sheet's outline, stranding the mist over whatever
slid into its place. The droplet layer is deliberately fixed (anchored right, sized off
`--fw-open`), so the fix is for the page to move at the same pace as the mist rather than
ahead of it.

**And it waits 125ms before it starts.** For that beat the droplets trace an outline
around a space that is still open. Beginning the instant the sheet vanished read as the
surroundings being in a hurry to get on with it; an eighth of a second of nothing first
makes the gap feel vacated rather than reclaimed. The button's width and tilt wait on the
same beat, which puts the geometry home at 385ms — still comfortably ahead of the burst
fading back in at 600ms, and that ordering is the constraint to preserve if either number
is ever changed. `.is-soft-close` overrides the delay: a quiet close has no droplets to
wait for and shouldn't hesitate.

**Clicking it pops it on a desktop too.** Hover has usually opened the sheet already by
the time the click lands, so "open" here is the `is-open` class *or* a live hover — test
only the class and the first click changes nothing on screen and it takes two. The
pointer is also still on the flyer afterwards, so `.is-dismissed` latches the hover rules
off until it leaves; without that the sheet springs back the instant `.is-popping` lifts
and the click reads as having done nothing. Keyboard focus still opens a dismissed flyer
on purpose, and the latch is only set when the pointer is really there, so Enter on a
focused button doesn't switch hover off for a pointer that never arrived.

A click skips the dwell, on the desktop path only, and that is not just tidiness: clicking
a `<button>` focuses it, `focusin` fires before `click` and calls `markOpen()`, so the
click that closes the flyer resets the dwell clock a moment before the handler reads it.
250ms of hover then a click soft-closed every time until the exemption went in — the same
shape of bug that stopped taps working on a phone. A phone keeps its dwell, where a tap is
both the open and the close and the opening tap has already taken the focus.

**Only letting go of the flyer pops it.** The pointer leaving it, or a tap on the flyer
itself. Escape and a tap elsewhere on the page dismiss it with the quiet .25s close
instead — a burst of droplets across the hero in response to a tap somewhere else reads as
something misfiring rather than as the flyer closing.

That is stronger than it first looks. An earlier version faded the sheet at full size
over 90ms and snapped the geometry at 100ms behind that cover, which does avoid a shrink,
but it leaves the poster hanging around for the first third of its own pop and reads as a
fade rather than a burst. If a future change makes something linger on the way out, this
is the rule it is breaking.

The droplet layer is anchored by `right` and sized off `--fw-open`, that being the edge
which stays put while the button collapses, so it doesn't budge while `--fw` runs home.
The droplets themselves are positioned as percentages of the sheet, so they ride whatever
width the clamp lands on, and each carries a `--d` diameter and a `--dx`/`--dy` flick
outward along its edge's normal (diagonally at the corners), plus a few ms of stagger.
They don't fade up in place: each pops into being just off the edge, out to a quarter of
its travel at full size in the first 60ms, then away and gone.

They were generated by `dev/pop-options.html` (option C, seed 21, 26 points), scaled up by
the ratio between that mock sheet and the real one so the proportions match what was
picked. That page is the bench this pop was chosen on: it plays four candidate treatments
side by side on a mock sheet at the flyer's proportions, with a slow-motion toggle, and it
is not part of the site. To redo the droplets, change the seed or count there and rescale
by `open sheet width ÷ 184`.

**Which direction owns which timings.** A transition reads its timing from the state it
is heading *into*, so the closed rules are the closing behaviour and the open ones are
the opening behaviour. That split is deliberate and load-bearing: everything above —
fading at full size, the geometry snapping at 100ms, nothing ever seen getting smaller —
lives in the resting state, where a close reads it whether anything else happens or not.

It used to hang off the `.is-popping` class instead, and that was a real bug. The class
had to land before the first style flush after `:hover` dropped, or the close fell back
to the ordinary transitions and the sheet visibly shrank behind the droplets. Leaving the
flyer downward onto the hero buttons did exactly that, reproducibly, while closing by tap
or by Escape was fine — those change a class, so both changes land in one recalc. Chasing
which listener flushed style first was the wrong fix. The timings simply should not have
depended on a class arriving in time, and now they don't. Closing with the class never
added at all gives identical timings to closing with it.

### Two things a tap does that a hover doesn't
Both of these made tapping on a phone fail to pop, and neither shows up on desktop.

- **A tap focuses the button.** `:focus-within` was therefore true after any tap, which
  held the sheet open and made `stillOpen()` refuse to pop — the second tap removed
  `is-open` and *nothing moved*. The open state now keys off `:has(:focus-visible)` and
  the script off `btn.matches(':focus-visible')`, which is the distinction the platform
  already draws: keyboard focus is focus-visible, a pointer tap is not. Same specificity,
  since `:has()` takes its most specific argument, so nothing else shifted.
- **A tap fires `mouseover`/`mouseenter` immediately before `click`.** Real touch hardware
  does this too, not just the preview. `mouseenter` was calling `markOpen()`, so the tap
  that closes the flyer reset the dwell clock to zero a moment before the click handler
  read it — the dwell could never be satisfied by tapping and every tap-close came out as
  a soft close. `markOpen()` now runs from `mouseenter` only when `hoverable.matches`,
  i.e. only where hovering is the thing that opens it; on touch the click handler marks it.

**A close only counts as a pop if the sheet was open for 250ms.** A brush past on the way
to something else shouldn't fire the whole performance. Under that dwell the flyer takes
`.is-soft-close` instead and simply runs the unroll backwards over .25s — the rectangle
returning to a burst, the artwork fading, the label coming back — with no droplets and
the button back at once rather than after the pop's wait. The clock starts when it
began opening, that being the span the reader actually spent on it. This is also why the
hint's delayed return sits on `.is-popping` rather than in the closed state: a quiet close
needs its caption back with the button, not half a second later.

That soft close is the one place a class carries closing timings, and it is deliberately
safe in the direction that matters. The resting state is still the instant vanish, so if
the class ever fails to land before the style flush the close is merely abrupt. The
reverse arrangement — gentle by default, instant on the pop class — is exactly what used
to leave the sheet shrinking in view behind the droplets.

**The flyer is inert while the pop plays.** Every open-state selector is gated on
`:not(.is-popping)`, so for that half second hover, focus and tap all do nothing — the
button is not on screen yet, and without the gate, sweeping back over the space it is
about to occupy springs the whole sheet open out of nothing. A tap in that window is
ignored outright rather than queued, so nothing expands a beat later in response to a
click on empty space. The moment the class lifts, the flyer opens on its own if the
pointer is over it, so nothing is lost. `popShut()` also refuses to run while a pop is
already going: waving the cursor across the gap used to replay the droplets over a sheet
that had already left.

**The button waits .6s before reforming, then fades in over 160ms.** The droplets are clear by ~345ms, and the
space then sits empty for a beat before the burst fades back in over .22s. That pause is
the point: without it the whole thing is over in a third of a second and reads as a blink
rather than as something having popped. The hint below it waits on the same clock, or a
caption is left floating under nothing. Coming back during the gap cancels it and the
button returns immediately, so the wait never costs responsiveness.

Two things are pinned to that pause and will break quietly if it changes: the safety
timeout in `popShut()` has to outlast the whole sequence (it removes the class, so
anything under ~800ms cuts the button off mid-return), and the hint needs its *opening*
transition declared separately in the open-state rules or it inherits the .5s delay and
sits over the sheet for most of the unroll.

Otherwise `.is-popping` does one job: hold the rolled burst back, and add the droplets. It is still a class rather than a bare CSS rule because the
collapsed state is also the state the page loads in, and a bare rule would fire the
droplets on every page load. Three separate things can hold the flyer open (hover,
keyboard focus, the `is-open` class), so `stillOpen()` checks all three before anything
counts as a close.

### Crossing the days off
Each day gets a green marker tick once it is over, at midnight ET the following
morning, from the `DONE_AT` instants in the same IIFE. Ticks already earned are drawn
on load; any still to come get a `setTimeout`, so a page left open overnight crosses
the day off by itself.

The ticks are positioned as percentages of the artwork, so they hold at any size. The
day tabs were measured off the image: 264px wide starting at x128, 136px tall, the
first at y385 and one every 162px. In percentages that is `left:15.1%` with tab centres
at `33.56%` and every 12% after. They live in `.flyer-plate` alongside the image rather
than in `.flyer-window`, because the window's height is animated and clipping, so
percentages against it would drift as the sheet unrolls.

Re-measure if the artwork changes. The tabs are hard to find by colour alone (the white
day names break each tab into pieces, and "Wednesday" is wide enough to reach the strip
of tab left of the text) so the reliable route is to find the first two tabs, take the
pitch between them, and step down.

## The map
The "Cameras Are Already Here" section is a self-hosted Leaflet map centered on
Marietta, with red dots from `assets/ga-alpr-cameras.geojson` (sourced from
OpenStreetMap, the same data DeFlock uses). It covers the northern half of Georgia
(lat 32.5–35.05) so the Cobb cluster reads in regional context. It is a snapshot, not
live. To refresh it, re-query the Overpass API for ALPR-tagged nodes in that bbox:
```
cat > /tmp/q.ql <<'EOF'
[out:json][timeout:120];
( node["man_made"="surveillance"]["surveillance:type"="ALPR"](32.5,-85.75,35.05,-80.8); );
out body;
EOF
curl -s -A "flock-off-cobb/1.0" --data-urlencode "data@/tmp/q.ql" \
  https://overpass-api.de/api/interpreter -o /tmp/alpr.json
node -e '
const fs=require("fs"),d=JSON.parse(fs.readFileSync("/tmp/alpr.json","utf8")),r=x=>Math.round(x*1e6)/1e6;
const feats=d.elements.filter(e=>e.type==="node"&&e.lat!=null).map(e=>({type:"Feature",
  geometry:{type:"Point",coordinates:[r(e.lon),r(e.lat)]},
  properties:{brand:(e.tags&&(e.tags.manufacturer||e.tags.brand||e.tags.operator))||""}}));
fs.writeFileSync("assets/ga-alpr-cameras.geojson",JSON.stringify({type:"FeatureCollection",features:feats}));
console.log(feats.length,"cameras");'
```

## District / ward lookup
The Reach Cobb Officials section has six address boxes that tell a resident which
Cobb commission district (1–4) or city ward/district they're in, and highlight the
matching contact card. It geocodes the address with OpenStreetMap Nominatim (the same
forgiving lookup the map uses), then runs a client-side point-in-polygon test against
the boundary file for that jurisdiction. No address is stored.

Acworth and Kennesaw have no lookup: both elect their entire council at large, so
there are no ward polygons and every member represents every resident.

Each lookup is one entry in the `CFG` object in the lookup IIFE, with a `scope`
selector naming the container whose `[data-seat]` cards it may highlight. Scoping
matters — five ward-based lookups share the page, and an unscoped attribute selector
would highlight matching seat numbers in every city at once.

To refresh the boundaries, re-query the source ArcGIS services (all simplified with
`maxAllowableOffset=0.0003`, `geometryPrecision=5`, `outSR=4326`, `f=geojson`):
```
# Cobb commission districts (layer 2; fields COMM_D, COMMISSION)
curl -s "https://services.arcgis.com/HYLRafMc4Ux6DA8c/arcgis/rest/services/Commissioner_Districts/FeatureServer/2/query?where=1%3D1&outFields=COMM_D&outSR=4326&maxAllowableOffset=0.0003&geometryPrecision=5&f=geojson"
# Marietta wards (MapServer layer 9; field WARD, split into subwards — drop the null-WARD sliver)
curl -s "https://secure.mariettaga.gov/server/rest/services/HubContent/AGOL_OpenData/MapServer/9/query?where=1%3D1&outFields=WARD&outSR=4326&maxAllowableOffset=0.0003&geometryPrecision=5&f=geojson"
# Powder Springs wards (Cobb County GIS "Municipal_Wards" layer 0; field DISTRICT — layer 1 is Marietta)
curl -s "https://services.arcgis.com/HYLRafMc4Ux6DA8c/arcgis/rest/services/Municipal_Wards/FeatureServer/0/query?where=1%3D1&outFields=DISTRICT&outSR=4326&maxAllowableOffset=0.0003&geometryPrecision=5&f=geojson"
# Mableton council districts (Cobb County GIS; layer 7, field DISTRICT is zero-padded "001".."006")
curl -s "https://services.arcgis.com/HYLRafMc4Ux6DA8c/arcgis/rest/services/Mableton_City_Council_Dec2022_FS/FeatureServer/7/query?where=1%3D1&outFields=DISTRICT&outSR=4326&maxAllowableOffset=0.0003&geometryPrecision=5&f=geojson"
# Smyrna wards (City of Smyrna's own ArcGIS org; field ward)
curl -s "https://services2.arcgis.com/hE9igMm8RoNeQRbh/arcgis/rest/services/Smyrna_Wards/FeatureServer/0/query?where=1%3D1&outFields=ward&outSR=4326&maxAllowableOffset=0.0003&geometryPrecision=5&f=geojson"
# Austell wards (field WARD)
curl -s "https://services9.arcgis.com/IMamNnsZ837vvWmt/arcgis/rest/services/Austell_Wards/FeatureServer/0/query?where=1%3D1&outFields=WARD&outSR=4326&maxAllowableOffset=0.0003&geometryPrecision=5&f=geojson"
```
Then normalize each feature's property to `district` / `ward` (integers, so Mableton's
`"001"` becomes `1`) and drop any feature with a blank value or null geometry before
saving. Some wards are multi-part, which is expected — Powder Springs ward 2 and
Smyrna ward 3 both arrive as separate pieces.

## Preview locally
```
cd "flock-off-cobb"
python3 -m http.server 8777
```
Then open http://localhost:8777/ in a browser.
(Opening index.html directly also works.)

## Deploy
**Live at https://deflockcobb.com** via GitHub Pages
(repo `CoolpantsMcBadass/flock-off-cobb`). The `CNAME` file in this folder holds the
custom domain; DNS is four A records to GitHub's Pages IPs (185.199.108–111.153, set
to "DNS only"/grey cloud on Cloudflare) plus a `www` CNAME to `coolpantsmcbadass.github.io`.

To redeploy: push to `main` and Pages rebuilds automatically. To move hosts, the same
folder works on Netlify/Vercel with no build step (publish directory is the folder itself).

## To edit
- **Letter text:** the `#letterText` block in `index.html`. The "Copy letter" button
  copies whatever is in that block, so edits flow through automatically.
- **Officials:** the `#cobb-officials` block for the county commissioners, and the
  `<details class="city">` panels inside `.cities` for each city council. To add or
  correct a councilmember, edit their `.official` card; if they hold a ward seat, keep
  the card's `data-seat` number and the matching entry in the `NAMES` object in the
  lookup IIFE in sync.
- **Meeting countdowns:** the `SCHED` object in the countdown IIFE, keyed by the
  `data-city` value on each `.countdown` span. `wd` is the weekday (0=Sun), `weeks` the
  ordinal weeks of the month, and an optional `summer` overrides `weeks` for Jul–Sep.
  Omit a city from `SCHED` and its countdown hides itself (that's how Acworth works).
- **Colors/fonts:** the `:root` CSS variables at the top of the `<style>` block.
