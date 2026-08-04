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
