# Flock Off, Cobb

A single-page action site to remove Flock Safety license plate readers from Cobb County, GA.
Modeled on gettheflockout.org, built from the "Flock Off – Cobb" action toolkit.

Plain HTML/CSS/JS — no build step, no dependencies.

## Files
- `index.html` — the entire site (styles + scripts are inline)
- `assets/img0.jpeg` — campaign art by Justin (@mind_invader_comics)
- `assets/cobb-cameras.geojson` — Cobb-area ALPR camera points for the map

## The map
The "Cameras Are Already Here" section is a self-hosted Leaflet map centered on
Marietta, with red dots from `assets/cobb-cameras.geojson` (sourced from DeFlock /
OpenStreetMap). It is a snapshot, not live. To refresh it, download the national data
and re-filter to the Cobb-area bounding box:
```
curl -L -H "Referer: https://maps.deflock.org/" \
  "https://data.dontgetflocked.com/cameras.geojson.gz" -o cams.json
python3 - <<'PY'
import json
d=json.load(open("cams.json")); W,E,S,N=-84.95,-84.25,33.65,34.20
out=[{"type":"Feature","geometry":{"type":"Point","coordinates":[round(c[0],6),round(c[1],6)]},
      "properties":{"brand":(f.get("properties") or {}).get("brand","")}}
     for f in d["features"]
     for c in [ (f.get("geometry") or {}).get("coordinates") ]
     if c and (f["geometry"]["type"]=="Point") and W<=c[0]<=E and S<=c[1]<=N]
json.dump({"type":"FeatureCollection","features":out}, open("assets/cobb-cameras.geojson","w"))
print(len(out),"cameras")
PY
```

## Preview locally
```
cd "flock-off-cobb"
python3 -m http.server 8777
```
Then open http://localhost:8777/ in a browser.
(Opening index.html directly also works.)

## Deploy
**GitHub Pages:** push this folder to a repo, then Settings → Pages → deploy from the
`main` branch root. Site goes live at `https://<user>.github.io/<repo>/`.

**Netlify/Vercel:** drag the folder into the dashboard, or connect the repo — no build
command needed, publish directory is the folder itself.

A custom domain (e.g. flockoffcobb.org) can be pointed at either host.

## To edit
- **Letter text:** the `#letterText` block in `index.html`. The "Copy letter" button
  copies whatever is in that block, so edits flow through automatically.
- **Officials:** the `.officials` and `.cities` blocks. City council emails are still
  placeholders in the source toolkit — drop them in as you collect them.
- **Colors/fonts:** the `:root` CSS variables at the top of the `<style>` block.
