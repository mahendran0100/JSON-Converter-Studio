# JSON Converter Studio
# Copyright (C) 2026 S Mahendran
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the LICENSE file for details.

import json

def _num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def build_geojson(rows, lat_column, lon_column):
    features = []

    for row in rows:
        lat = _num(row.get(lat_column))
        lon = _num(row.get(lon_column))
        if lat is None or lon is None:
            continue

        properties = {
            k: v for k, v in row.items()
            if k not in (lat_column, lon_column)
        }

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": properties
        })

    return {"type": "FeatureCollection", "features": features}

def export_geojson(rows, lat_column, lon_column, path):
    data = build_geojson(rows, lat_column, lon_column)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return len(data["features"])
