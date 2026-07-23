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
The Reach Cobb Officials section has two address boxes that tell a resident which
Cobb commission district (1–4) or Marietta ward (1–7) they're in, and highlight the
matching contact card. It geocodes the address with OpenStreetMap Nominatim (the same
forgiving lookup the map uses), then runs a client-side point-in-polygon test against
`assets/cobb-districts.geojson` and `assets/marietta-wards.geojson`. No address is
stored. To refresh the boundaries, re-query the source ArcGIS services (simplified with
`maxAllowableOffset=0.0003`, `geometryPrecision=5`, `outSR=4326`, `f=geojson`):
```
# Cobb commission districts (layer 2; fields COMM_D, COMMISSION)
curl -s "https://services.arcgis.com/HYLRafMc4Ux6DA8c/arcgis/rest/services/Commissioner_Districts/FeatureServer/2/query?where=1%3D1&outFields=COMM_D&outSR=4326&maxAllowableOffset=0.0003&geometryPrecision=5&f=geojson"
# Marietta wards (MapServer layer 9; field WARD, split into subwards — drop the null-WARD sliver)
curl -s "https://secure.mariettaga.gov/server/rest/services/HubContent/AGOL_OpenData/MapServer/9/query?where=1%3D1&outFields=WARD&outSR=4326&maxAllowableOffset=0.0003&geometryPrecision=5&f=geojson"
```
Then normalize each feature's property to `district` / `ward` (integers) before saving.

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
- **Officials:** the `.officials` and `.cities` blocks. City council emails are still
  placeholders in the source toolkit — drop them in as you collect them.
- **Colors/fonts:** the `:root` CSS variables at the top of the `<style>` block.
