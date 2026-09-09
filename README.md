# Victoria disability-housing vacancy map

A heatmap/pins view of every current SDA/SIL vacancy listed by Life Without Barriers, Scope, Aruma, possAbility and Melba across Victoria, built from the same scrape behind Joel Dignam's (Summer Foundation) full multi-provider vacancy spreadsheet.

Live at: https://jd-summer-foundation.github.io/vic-vacancy-map/

This README is written so a **fresh Claude Code session with no prior context** (or a human) can pick this repo up cold, understand the whole pipeline, and safely make an update. Read this in full before changing anything.

## What this site is, in one paragraph

Joel maintains a spreadsheet ("Disability Provider Vacancies.xlsx") listing every current SDA/SIL housing vacancy across several Australian disability providers, scraped from each provider's own website. A colleague wanted the Victorian subset shown on a map as a heatmap. This repo is that map: a static, no-build-step HTML/CSS/JS site, deployed via GitHub Pages, that reads a small JSON file (`vic_data.json`) derived from the spreadsheet. There is no server and no database — updating the map means regenerating `vic_data.json` from the latest spreadsheet, regenerating `index.html` from `render.py` (only needed if the *set of providers* changed), and pushing.

## Where the source data comes from

The vacancy spreadsheet is maintained across Claude sessions attached to Joel's claude.ai Project **"SDA & Housing Supply"**. That project contains a document, `claude/vacancy-database-method.md`, which is the authoritative, detailed record of exactly how each provider's data was scraped, what every spreadsheet column means, and every known data-quality caveat (typos on a provider's own site, boilerplate excerpt text, approximate vs. exact coordinates, etc.). **Read that doc before trusting or debugging anything about the underlying data** — this repo's README only covers the map itself, not the scrape.

If you (a fresh Claude Code session) have been asked to update this map with a new or refreshed provider:
1. Check whether the person has already updated the master spreadsheet / `all_rows.json` export. If not, that work needs to happen first — either in a session attached to the "SDA & Housing Supply" project (which has the full scraping method and can regenerate the workbook), or by asking Joel for the current export.
2. Once you have an up-to-date `all_rows.json` (see below for exactly what shape it must be), everything in this repo is mechanical: run `build_data.py`, run `render.py` if the provider list changed, commit, push.

## The pipeline

```
Disability Provider Vacancies.xlsx  (master spreadsheet, "Vacancies" sheet, one row per vacancy, all states)
            │
            │  xlsx_to_json.py  (only needed if you have the .xlsx but not a JSON export)
            ▼
     all_rows.json   (gitignored — regenerate locally, don't commit; it's the full
                       cross-provider, cross-state export, not VIC-only)
            │
            │  build_data.py   (filters to State == 'VIC', resolves coordinates,
            │                   maps spreadsheet columns → the map's compact schema)
            ▼
     vic_data.json    (tracked in git — this is what the deployed site fetches at runtime)
            │
            │  render.py   (only needs re-running if the SET OF PROVIDERS changed —
            │               it bakes the provider list and legend colours into index.html)
            ▼
       index.html      (tracked in git — the deployed page; fetches ./vic_data.json client-side)
```

**Key point:** `vic_data.json` can be regenerated and pushed on its own for a routine data refresh (new listings, filled vacancies, updated bedroom counts) as long as the *set of providers* hasn't changed — `index.html` doesn't need to be touched. You only need to re-run `render.py` when a provider is **added or removed** (because the legend colours and the `PROVIDERS` array are baked into `index.html` at generation time, not computed at runtime).

### Regenerating everything from a spreadsheet export

```bash
# If you only have the .xlsx, not all_rows.json:
python3 xlsx_to_json.py "Disability Provider Vacancies.xlsx"

# Filter to VIC and build the map's data file:
python3 build_data.py

# Only if the provider list changed (a provider added/removed since the last deploy):
python3 render.py
```

Then commit and push `vic_data.json` (and `index.html` if you ran `render.py`) — GitHub Pages redeploys automatically on push to the default branch, usually within a minute or two.

### Adding a new provider

If a 6th (or later) provider is added to the spreadsheet and has VIC listings:

1. Regenerate `all_rows.json` and run `build_data.py` as above — `vic_data.json` will include the new provider automatically as long as its rows have `State == 'VIC'` and either a `Latitude`/`Longitude` or a suburb already in `build_data.py`'s `FALLBACK` dict. If some of its VIC listings don't publish per-listing coordinates and are in a new suburb, add that suburb's approximate centroid to `FALLBACK` (look it up, don't guess) or those rows will be silently dropped (`build_data.py` prints `total VIC placed: X of Y` — check X == Y).
2. Open `render.py` and:
   - Add the new provider's name to the `PROVIDER_LIST` passed to `HTML.replace('__PROVIDER_LIST__', ...)` at the bottom of the file (order matters — it determines legend order and which `--pN` colour each provider gets).
   - Add a new `--pN` CSS colour variable in **all three** places colours are defined (search for `--p1`): the light `:root` block, the `@media (prefers-color-scheme: dark)` block, and the `:root[data-theme="dark"]` block. Pick a colour distinct from the existing providers (currently: blue, orange, green, amber, purple) — check `providerColorVar()`'s array (`['--p1','--p2','--p3','--p4','--p5']`) has an entry for every provider's index and extend it too.
   - Update the static intro sentence (`<p class="sub">Every current SDA/SIL vacancy listed by ...`) to name the new provider.
3. Run `render.py`, then **test locally before pushing** (see below) — specifically check the legend shows the right colour/count for the new provider and the stats bar's "Providers shown" count is correct.
4. Update the byline's "N of M locations use an approximate suburb centroid" figures if they changed (`build_data.py`'s own console output tells you the new numbers).

### Testing locally

Map tiles and Google Fonts will fail to load in most cloud/CI sandboxes (no network egress to those hosts) — that's expected and not a bug; everything else (data loading, filters, legend, table view, dark mode) can and should still be verified. Serve over HTTP, not `file://` (the page uses `fetch('./vic_data.json')`, which `file://` blocks via CORS):

```bash
python3 -m http.server 8080
# then open http://127.0.0.1:8080/index.html, or drive it with Playwright/similar
```

Check: the stats bar's vacancy/provider/suburb counts look sane, the legend lists every provider with a distinct colour and a correct count, switching Heatmap/Pins/Table works, and the browser console shows no `pageerror`s (network errors for tile/font hosts are fine).

## Files in this repo

- `index.html` — the deployed page. Generated by `render.py`; don't hand-edit the parts that come from the `HTML = """..."""` template in `render.py` (your edit will be lost next regeneration) — either edit `render.py` and regenerate, or hand-edit `index.html` directly for a one-off fix and accept that `render.py` will need the same fix applied to stay in sync.
- `vic_data.json` — the map's data, one record per VIC vacancy (provider, title, suburb, lat/lon, approx flag, bedrooms, bathrooms, building type, service type, vacancy count, listing URL). Generated by `build_data.py`. Tracked in git — this is what makes the deployed site show current data without a rebuild step.
- `render.py` — generates `index.html` from an inline HTML/CSS/JS template. Edit this (not `index.html` directly) for anything beyond a one-off emergency fix.
- `build_data.py` — generates `vic_data.json` from `all_rows.json` (VIC filter + coordinate resolution + column mapping).
- `xlsx_to_json.py` — one-off helper: converts the master `.xlsx`'s "Vacancies" sheet into `all_rows.json`, for when you have the spreadsheet but not a JSON export already.
- `all_rows.json` — gitignored. The full, all-provider, all-state export that `build_data.py` reads. Regenerate it locally (via `xlsx_to_json.py`, or obtain directly from a Claude session/Project with the current data) rather than committing it — it duplicates the master spreadsheet and would drift out of sync silently if checked in.
- `vendor/` — Leaflet and Leaflet.heat, vendored (not loaded from a CDN) so the page has no runtime CDN dependency. Only touch these if upgrading the mapping library itself.
- `package.json` / `package-lock.json` / `node_modules/` — gitignored, exist only locally as the mechanism used to fetch `vendor/`'s files (`npm install leaflet leaflet.heat`, then copy `dist/` files across). Not needed to view or deploy the site; only needed if re-vendoring after a library upgrade.

## What the map shows

- **Heatmap** view: a density heatmap of current vacancies, weighted per unique location and calibrated so the colour scale reflects the actual range of clustering currently on screen (not a fixed scale that saturates everywhere) — points are pre-clustered by rounded coordinate and fed `sqrt(count)` as intensity so the colour scale isn't dominated by a few very dense clusters.
- **Pins** view: individual listings, clustered where several vacancies share a location, coloured by provider (grey = a cluster mixing more than one provider).
- Filters by provider and bedroom count; a full sortable table view as an accessible alternative to the map.
- Light/dark mode follows the viewer's system setting. Map tiles themselves stay light-toned regardless (raster tiles can't be re-themed) — this is called out on the page itself so it doesn't read as a bug.

## Tech

Static HTML/CSS/JS, no build step, no framework. Leaflet + Leaflet.heat are vendored under `vendor/` (see above). Map tiles are OpenStreetMap's standard raster tile server, loaded live at runtime and requiring the attribution shown on the page (do not remove it — it's an OSM usage requirement, not decoration). Deployed via GitHub Pages serving directly from this repo's default branch — there is no separate build/deploy step beyond pushing.

## Known limitations / things worth knowing before you "fix" them

- **Approximate coordinates**: some listings (currently 19 of 238) don't publish exact coordinates on the provider's own site, so `build_data.py` falls back to an approximate suburb centroid (see its `FALLBACK` dict). These are flagged in the data (`"approx": true`) and in the page's byline text — this is a known, documented limitation, not a bug to silently "fix" by inventing more precise coordinates.
- **No street addresses anywhere**: intentional, for resident privacy. Every provider's own site stops at suburb-level location, and so does this map.
- **The provider→colour mapping is baked in at generation time**, not computed from the data at runtime (see "Adding a new provider" above). This is a deliberate simplicity trade-off for a small, slow-changing provider list — don't rebuild it as a dynamic runtime palette without discussing that scope change first.
- **A colleague's feedback thread on the map's design (heatmap contrast, tile choice, etc.) may still be active in Joel's main working conversation** — if you're a fresh session picking this up from only this README, it's worth checking with Joel whether there's pending design feedback beyond a routine data refresh before making visual changes.
