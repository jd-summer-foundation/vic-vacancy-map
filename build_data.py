"""
Build vic_data.json (the map's data file) from all_rows.json (the full,
all-provider, all-state export of the vacancy database -- see xlsx_to_json.py
to produce it from the master .xlsx, or get all_rows.json directly from the
Claude session/project that maintains the spreadsheet).

Usage:
    python3 build_data.py [all_rows.json]

Writes ./vic_data.json. Then run render.py to bake the same set of providers
into index.html's colour legend (see README.md - "Adding a new provider").
"""
import json
import sys
from collections import Counter

SRC = sys.argv[1] if len(sys.argv) > 1 else "all_rows.json"
rows = json.load(open(SRC))
vic = [r for r in rows if r.get('State') == 'VIC']

# Suburb-centroid fallback coordinates for VIC suburbs where the source site
# doesn't expose per-listing coordinates (all current cases are possAbility
# listings, plus 2 Scope short-term-respite listings -- see the "Method &
# Notes" sheet in the spreadsheet for why). Approximate town/suburb centroids
# only -- consistent with the rest of the dataset, which never has
# street-level addresses (resident privacy). Add an entry here if a future
# provider also lacks per-listing coordinates for some of its VIC rows.
FALLBACK = {
    "Ararat": (-37.2833, 142.9333),
    "Bacchus Marsh": (-37.6667, 144.4333),
    "Ballarat East": (-37.5600, 143.8720),
    "Bayswater": (-37.8398, 145.2680),
    "Burwood": (-37.8481, 145.1147),
    "Melton": (-37.6833, 144.5833),
    "Melton South": (-37.7167, 144.5667),
    "North Bendigo": (-36.7333, 144.2833),
    "Stawell": (-37.0667, 142.7667),
    "Strathdale": (-36.7667, 144.3000),
    "Sunbury": (-37.5833, 144.7167),
    "Wheelers Hill": (-37.8833, 145.1833),
    "Woodend": (-37.3500, 144.5333),
}

out = []
geocode_used = 0
for r in vic:
    lat = r.get("Latitude")
    lon = r.get("Longitude")
    approx = False
    if not lat or not lon:
        suburb = r.get("Suburb (from title)", "").strip()
        if suburb in FALLBACK:
            lat, lon = FALLBACK[suburb]
            approx = True
            geocode_used += 1
        else:
            continue  # can't place it -- no coordinates and no fallback centroid

    def to_int(v):
        try:
            return int(str(v).strip())
        except (ValueError, TypeError):
            return None

    out.append({
        "provider": r["Provider"],
        "title": r["Title"],
        "suburb": r.get("Suburb (from title)", ""),
        "lat": round(float(lat), 5),
        "lon": round(float(lon), 5),
        "approx": approx,
        "bedrooms": to_int(r.get("Bedrooms")),
        "bathrooms": to_int(r.get("Bathrooms")),
        "buildingType": r.get("Building Type") or "",
        "serviceType": r.get("Service Type") or "",
        "vacancies": r.get("Vacancies Available") or "",
        "url": r.get("Listing URL", ""),
    })

print("total VIC placed:", len(out), "of", len(vic))
print("approx-geocoded (suburb centroid fallback):", geocode_used)
print(Counter(o["provider"] for o in out))

json.dump(out, open('vic_data.json', 'w'))
print("wrote vic_data.json")
