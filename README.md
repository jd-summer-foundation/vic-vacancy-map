# Victoria disability-housing vacancy map

A heatmap/pins view of every current SDA/SIL vacancy listed by Life Without Barriers, Scope, Aruma and possAbility across Victoria, built from the same scrape behind the [full 4-provider vacancy spreadsheet](../../).

Live at: https://jd-summer-foundation.github.io/vic-vacancy-map/

## What it shows

- **Heatmap** view: a density heatmap of current vacancies, weighted per unique location and calibrated so the colour scale reflects the actual range of clustering currently on screen (not a fixed scale that saturates everywhere).
- **Pins** view: individual listings, clustered where several vacancies share a location, coloured by provider.
- Filters by provider and bedroom count; a full sortable table view as an accessible alternative to the map.

## Data

`vic_data.json` holds one record per Victorian vacancy (provider, title, suburb, coordinates, bedrooms/bathrooms, building type, listing URL). 19 of 211 locations use an approximate suburb-centroid coordinate where the source site (possAbility, plus 2 Scope short-term-respite listings) doesn't publish per-listing coordinates.

## Tech

Static HTML/CSS/JS, no build step. Leaflet + Leaflet.heat are vendored under `vendor/` (no CDN dependency at runtime). Map tiles are OpenStreetMap's standard raster tiles, loaded live and requiring attribution (included on the page).

To update the data, regenerate `vic_data.json` from the vacancy spreadsheet and redeploy (GitHub Pages serves directly from this repo).
