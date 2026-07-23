from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEOJSON_PATH = ROOT / "data" / "geo" / "morocco_regions.geojson"
BACKUP_PATH = ROOT / "data" / "geo" / "morocco_regions.source_12_regions.geojson"

SOUTH_SOURCE_NAMES = {
    "Laayoune-Saguia Hamra",
    "Dakhla-Oued Eddahab",
    "Guelmim-Oued Noun",
}

REGION_RENAMES = {
    "Rabat-Sale-Kenitra": "Rabat-Salé-Kénitra",
    "Beni Mellal-Khenifra": "Béni Mellal-Khénifra",
    "Tanger-Tetouan-Hoceima": "Tanger-Tétouan-Al Hoceïma",
    "Daraa-Tafilelt": "Drâa-Tafilalet",
    "Fes-Meknes": "Fès-Meknès",
    "Souss Massa": "Souss-Massa",
}


def coordinate_depth(value):
    depth = 0
    while isinstance(value, list):
        depth += 1
        if not value:
            return depth
        value = value[0]
    return depth


def iter_positions(coords):
    if isinstance(coords[0], (int, float)):
        yield coords
    else:
        for item in coords:
            yield from iter_positions(item)


def validate_feature(feature):
    geometry = feature.get("geometry", {})
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    depth = coordinate_depth(coordinates)
    expected = 3 if geometry_type == "Polygon" else 4 if geometry_type == "MultiPolygon" else None
    name = feature.get("properties", {}).get("region")

    if expected is None or depth != expected or depth == 1:
        raise ValueError(f"Invalid geometry nesting for {name}: {geometry_type}, depth={depth}, expected={expected}")

    points = list(iter_positions(coordinates))
    lon_values = [point[0] for point in points]
    lat_values = [point[1] for point in points]
    if not all(-18.5 <= lon <= 0.5 for lon in lon_values):
        raise ValueError(f"Longitude range looks wrong for {name}: {min(lon_values)}..{max(lon_values)}")
    if not all(20.0 <= lat <= 36.5 for lat in lat_values):
        raise ValueError(f"Latitude range looks wrong for {name}: {min(lat_values)}..{max(lat_values)}")


def as_multipolygon_coordinates(feature):
    geometry = feature["geometry"]
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiPolygon":
        return geometry["coordinates"]
    raise ValueError(f"Unsupported geometry type: {geometry['type']}")


def main():
    geojson = json.loads(GEOJSON_PATH.read_text(encoding="utf-8"))
    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(json.dumps(geojson, ensure_ascii=False, indent=2), encoding="utf-8")

    output_features = []
    south_polygons = []

    for feature in geojson["features"]:
        feature = deepcopy(feature)
        raw_name = feature["properties"].get("region", "")
        validate_feature(feature)

        if raw_name in SOUTH_SOURCE_NAMES or raw_name == "Régions du Sud":
            south_polygons.extend(as_multipolygon_coordinates(feature))
            continue

        feature["properties"] = {"region": REGION_RENAMES.get(raw_name, raw_name)}
        output_features.append(feature)

    if not south_polygons:
        raise ValueError("No southern polygons found to merge")

    south_feature = {
        "type": "Feature",
        "properties": {"region": "Régions du Sud"},
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": south_polygons,
        },
    }
    validate_feature(south_feature)
    output_features.append(south_feature)

    fixed = {
        "type": "FeatureCollection",
        "features": output_features,
    }
    for feature in fixed["features"]:
        validate_feature(feature)

    GEOJSON_PATH.write_text(json.dumps(fixed, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {GEOJSON_PATH}")
    print(f"Features: {len(output_features)}")
    print("Regions:", sorted(feature["properties"]["region"] for feature in output_features))


if __name__ == "__main__":
    main()
