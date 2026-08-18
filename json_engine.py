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
from pathlib import Path

PREFERRED_KEYS = [
    "results", "data", "items", "records", "features",
    "places", "stores", "locations", "rows"
]

def load_json_records(path):
    with Path(path).open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in PREFERRED_KEYS:
            value = data.get(key)
            if isinstance(value, list):
                return value

        for value in data.values():
            if isinstance(value, list) and value:
                return value

        return [data]

    return [{"value": data}]

def flatten_value(value, prefix=""):
    result = {}

    if isinstance(value, dict):
        for key, child in value.items():
            key = str(key)
            new_key = f"{prefix}.{key}" if prefix else key
            result.update(flatten_value(child, new_key))
    elif isinstance(value, list):
        if not value:
            result[prefix] = ""
        elif all(not isinstance(x, (dict, list)) for x in value):
            result[prefix] = ", ".join("" if x is None else str(x) for x in value)
        else:
            for i, child in enumerate(value):
                result.update(flatten_value(child, f"{prefix}[{i}]"))
    else:
        result[prefix] = value

    return result

def flatten_records(records, flatten=True, remove_duplicates=False):
    output = []

    for record in records:
        row = flatten_value(record) if isinstance(record, dict) and flatten else (
            dict(record) if isinstance(record, dict) else {"value": record}
        )

        for key, value in list(row.items()):
            if isinstance(value, (dict, list)):
                row[key] = json.dumps(value, ensure_ascii=False, default=str)

        output.append(row)

    if remove_duplicates:
        seen = set()
        unique = []
        for row in output:
            sig = json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)
            if sig not in seen:
                seen.add(sig)
                unique.append(row)
        output = unique

    columns = []
    seen = set()
    for row in output:
        for key in row:
            if key not in seen:
                seen.add(key)
                columns.append(key)

    return output, columns

def apply_mapping(rows, columns, mapping):
    new_columns = [mapping.get(c, c) for c in columns]
    new_rows = []
    for row in rows:
        new_rows.append({
            new: row.get(old, "")
            for old, new in zip(columns, new_columns)
        })
    return new_rows, new_columns

def detect_coordinates(columns):
    low = {str(c).lower(): c for c in columns}

    lat_names = ["latitude", "lat", "location.latitude", "location.lat", "y"]
    lon_names = ["longitude", "lng", "lon", "location.longitude", "location.lng", "x"]

    lat = next((low[x] for x in lat_names if x in low), None)
    lon = next((low[x] for x in lon_names if x in low), None)
    return lat, lon
