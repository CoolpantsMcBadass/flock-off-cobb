import re, math

SRC = "M110.0,6.0 L125.0,18.6 L150.3,8.1 L152.2,24.6 L182.4,20.2 L174.4,34.3 L202.3,36.6 L185.0,47.8 L213.3,55.0 L188.5,62.5 L201.7,73.3 L171.4,74.7 L180.2,88.8 L154.6,87.1 L149.7,101.1 L123.8,88.3 L110.0,105.9 L94.0,93.8 L70.4,101.0 L66.8,86.1 L39.5,88.9 L51.7,73.8 L15.3,73.9 L40.6,61.6 L10.0,55.0 L38.4,48.1 L18.7,36.8 L46.9,34.7 L38.0,20.3 L65.2,22.7 L70.8,9.5 L94.8,18.1 Z"

pts = [(float(a), float(b)) for a, b in re.findall(r'([-\d.]+),([-\d.]+)', SRC)]
W, H = 220.0, 110.0

# The burst box moves from (band + spike allowance) to exactly the window's box, so the
# path is re-expressed in that frame: old box 216x120 at (-13,-11), new box 190x104.
def remap(p):
    return (p[0]*216/190 - 13*220/190, p[1]*120/104 - 11*110/104)
star = [remap(p) for p in pts]
cx, cy = remap((110.0, 55.0))

# Each star point retracts straight back along its own ray onto the rectangle, so the
# spikes flatten into the edges instead of the shape twisting on its way there.
def onto_rect(p):
    dx, dy = p[0]-cx, p[1]-cy
    ts = []
    if dx > 0: ts.append((W-cx)/dx)
    elif dx < 0: ts.append((0-cx)/dx)
    if dy > 0: ts.append((H-cy)/dy)
    elif dy < 0: ts.append((0-cy)/dy)
    t = min(ts)
    return (cx+dx*t, cy+dy*t)
rect = [onto_rect(p) for p in star]

# Nothing lands exactly on a corner by chance, which would leave the "rectangle" with
# chamfered corners, so the nearest point to each corner is snapped onto it.
for corner in [(0,0), (W,0), (W,H), (0,H)]:
    i = min(range(len(rect)), key=lambda j: (rect[j][0]-corner[0])**2 + (rect[j][1]-corner[1])**2)
    rect[i] = corner

def z(v):
    # "-0.0" is valid path data but makes the file diff against this script's output,
    # and these strings are compared literally to check the three copies haven't drifted.
    return v + 0.0 if v != 0 else 0.0

def path(ps):
    ps = [(z(x), z(y)) for x, y in ps]
    return "M%.1f,%.1f " % ps[0] + " ".join("L%.1f,%.1f" % q for q in ps[1:]) + " Z"

# The same two shapes again as fractions of the box, for the clipPath that keeps the
# artwork inside the outline (clipPathUnits="objectBoundingBox"). Three copies of the
# shape live in index.html — outline, its shadow, and this clip — so regenerate together.
def path_norm(ps):
    n = [(z(round(x / W, 4)), z(round(y / H, 4))) for x, y in ps]
    return "M%.4f,%.4f " % n[0] + " ".join("L%.4f,%.4f" % q for q in n[1:]) + " Z"

print("POINTS:", len(pts))
print("\nSTAR (.flyer-burst path, base):\n" + path(star))
print("\nRECT (--open-d):\n" + path(rect))
print("\nSTAR normalised (#flyerEdge path, base):\n" + path_norm(star))
print("\nRECT normalised (--open-dn):\n" + path_norm(rect))
