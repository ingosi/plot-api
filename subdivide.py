from shapely.geometry import Polygon
from shapely.ops import split
import geopandas as gpd
import numpy as np

def subdivide_polygon_vertical(coords, count):
    poly = Polygon(coords)
    bounds = poly.bounds
    minx, miny, maxx, maxy = bounds

    width = (maxx - minx) / count
    slices = []

    for i in range(count):
        x0 = minx + i * width
        x1 = x0 + width
        rect = Polygon([
            (x0, miny), (x1, miny),
            (x1, maxy), (x0, maxy),
            (x0, miny)
        ])
        part = poly.intersection(rect)
        if not part.is_empty:
            slices.append(part)

    return to_feature_collection(slices)

def subdivide_polygon_horizontal(coords, count):
    poly = Polygon(coords)
    bounds = poly.bounds
    minx, miny, maxx, maxy = bounds

    height = (maxy - miny) / count
    slices = []

    for i in range(count):
        y0 = miny + i * height
        y1 = y0 + height
        rect = Polygon([
            (minx, y0), (maxx, y0),
            (maxx, y1), (minx, y1),
            (minx, y0)
        ])
        part = poly.intersection(rect)
        if not part.is_empty:
            slices.append(part)

    return to_feature_collection(slices)

def to_feature_collection(polygons):
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": g.__geo_interface__,
                "properties": {"id": i + 1}
            }
            for i, g in enumerate(polygons)
        ]
    }
