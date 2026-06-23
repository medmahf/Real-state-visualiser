"""Dissout le cadastre parcellaire du 94 en 47 contours de communes, simplifie,
bouche les trous internes -> backend/data/communes_94.geojson (couche carte legere)."""
import collections
import json
import sys

from shapely import make_valid, simplify, union_all
from shapely.geometry import MultiPolygon, Polygon, mapping, shape

IN = sys.argv[1] if len(sys.argv) > 1 else "data/raw/cadastre_94_val_de_marne.geojson"
OUT = sys.argv[2] if len(sys.argv) > 2 else "../backend/data/communes_94.geojson"
TOL = 0.0004  # tolerance de simplification (degres)


def fill_and_clean(geom):
    parts = geom.geoms if isinstance(geom, MultiPolygon) else [geom]
    polys = [Polygon(p.exterior) for p in parts if p.area > 1e-6]  # boucher les trous
    return simplify(union_all(polys), tolerance=TOL, preserve_topology=True) if polys else geom


def main():
    gj = json.load(open(IN))
    groups, cont = collections.defaultdict(list), collections.defaultdict(float)
    for ft in gj["features"]:
        g = shape(ft["geometry"])
        g = g if g.is_valid else make_valid(g)
        c = ft["properties"]["commune"]
        groups[c].append(g)
        try:
            cont[c] += float(ft["properties"]["contenance"])
        except (TypeError, ValueError):
            pass

    out = {"type": "FeatureCollection", "name": "communes_94", "features": []}
    for c, geoms in sorted(groups.items()):
        merged = union_all([g.buffer(0) for g in geoms])
        out["features"].append({
            "type": "Feature",
            "properties": {"code_commune": c, "nb_parcelles": len(geoms),
                           "surface_cadastrale_m2": round(cont[c])},
            "geometry": mapping(fill_and_clean(merged)),
        })
    json.dump(out, open(OUT, "w"), separators=(",", ":"))
    print(f"{len(out['features'])} communes -> {OUT}")


if __name__ == "__main__":
    main()
