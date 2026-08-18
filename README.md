# JSON Converter Studio

**JSON Converter Studio** is a native QGIS Python plugin developed by **S Mahendran** for converting JSON data into tabular and GIS-ready formats.

## Features

- JSON file import
- JSON folder / batch import
- Nested JSON flattening
- Duplicate removal
- Column mapping / renaming
- Preview first 100 records
- Search in preview
- Latitude/Longitude auto detection
- CSV export
- Excel XLSX export
- GeoJSON export
- Add validated Point Layer directly to QGIS
- EPSG:4326 point creation
- Invalid/out-of-range coordinate reporting
- Live Processing Log
- Save Processing Log
- No external Python package dependencies

## Processing workflow

JSON
→ Load
→ Analyze
→ Flatten
→ Deduplicate
→ Map fields
→ Detect coordinates
→ Preview
→ Export or Add Point Layer

## Point Layer

`Add Point Layer` creates a QGIS memory Point layer using EPSG:4326.

Coordinates are validated:
- Longitude must be between -180 and 180.
- Latitude must be between -90 and 90.
- Missing or invalid coordinates are skipped and reported in the Processing Log.

## Processing Log

The log records:
- File loading
- Record counts
- Duplicate processing
- Column mapping
- Coordinate detection
- Preview refresh
- CSV/Excel/GeoJSON exports
- QGIS layer creation
- Invalid coordinate counts
- Errors

Logs can be cleared or saved as a text file.

## License

GNU General Public License v2.0 or later. See `LICENSE`.

## Credits

Developed by **S Mahendran**.

## QGIS compatibility

Targeted for QGIS 3.28 through QGIS 3.99 and tested for the QGIS 3.44/Python 3.12 environment used during development.

## Publication

See `PUBLISHING_CHECKLIST.md` before uploading to the official QGIS Plugin Repository.


## Project Links

Source code and issue tracking are available on the project's GitHub repository.
