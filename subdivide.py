from shapely.geometry import Polygon, LineString, mapping
from shapely.ops import split

def subdivide_polygon(coords, count):
    polygon = Polygon(coords)

    bounds = polygon.bounds  # (minx, miny, maxx, maxy)
    minx, miny, maxx, maxy = bounds
    step = (maxx - minx) / count

    lines = []
    for i in range(1, count):
        x = minx + i * step
        line = LineString([(x, miny - 1), (x, maxy + 1)])
        lines.append(line)

    result = polygon
    for line in lines:
        result = split(result, line)

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"id": i + 1},
                "geometry": mapping(geom)
            }
            for i, geom in enumerate(result.geoms)
        ]
    }
