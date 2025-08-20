# HoudiniGIS — HDA Quick Install

**Easiest setup** — copy this `houdini20.5/` folder into your Houdini user prefs and start Houdini.
On first launch, `scripts/456.py` auto-creates `HoudiniGIS.hda` and registers the node under **Tab → HoudiniGIS**.

## Paths
- Windows: `C:\Users\<you>\Documents\houdini20.5\`
- macOS/Linux: `~/houdini20.5/`

## Dependencies
- Required: `pyshp`
- Optional (for reprojection): `pyproj`

Install:
- macOS/Linux:
  ```bash
  python3 -m pip install --target "$HOME/houdini20.5/python3.11libs" pyshp pyproj
  ```
- Windows (PowerShell):
  ```powershell
  python -m pip install --target "$env:USERPROFILE\Documents\houdini20.5\python3.11libs" pyshp pyproj
  ```

## Use
- Dive into a **Geometry** node, press **Tab**, select **HoudiniGIS → HGIS Shapefile Import**.
- Pick your `.shp` file. Optionally set `Target CRS (EPSG)` (needs a `.prj` next to the `.shp`).
- Enable `Swap Y/Z` if your shapefile uses a different up-axis.

## Notes
- For polygon holes, subtract group `hgis_hole` from `hgis_exterior` with a **Boolean** SOP.
