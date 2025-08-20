# HGIS
HGIS - Houdini GIS

Simple Houdini Digital Asset for importing ESRI Shapefiles. The node wraps a
Python implementation inspired by the
[houdini-sop-shapefile](https://github.com/ttvd/houdini-sop-shapefile)
project. It relies on the [`pyshp`](https://pypi.org/project/pyshp/) library
and optionally [`pyproj`](https://pypi.org/project/pyproj/) for reprojection.

Features
- Create points, polylines and polygons with attributes.
- Optional reprojection using EPSG codes when a `.prj` file is present.
- `Swap Y/Z` toggle to flip axes for Y-up shapefiles.
