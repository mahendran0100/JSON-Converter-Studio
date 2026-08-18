# Changelog

## 1.1.2
- Finalized licensing for official QGIS Plugin Repository publication under GPL-2.0-or-later.
- Added explicit QGIS compatibility ceiling at 3.99; QGIS 4 compatibility is not claimed.
- Updated publication documentation and release metadata.

## 1.1.0
- Added live Processing Log with timestamps and severity levels.
- Added Clear Log and Save Log actions.
- Added detailed logging for JSON loading, analysis, coordinate detection, preview, mapping, CSV, Excel, GeoJSON, and QGIS layer creation.
- Improved Add Point Layer validation for invalid and out-of-range coordinates.
- QGIS point layer now uses EPSG:4326 explicitly.
- QGIS layer name is derived from the input JSON filename when possible.
- Added developer credit: S Mahendran.
- Added GPL-2.0-or-later license metadata and publication documentation.
- No external Python package dependencies.

## 1.0.6
- Fixed Analyze compatibility issue.
- Preserved the colorful UI and custom icon.
