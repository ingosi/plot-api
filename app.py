from flask import Flask, request, jsonify
from shapely.geometry import Polygon, LineString, mapping
from shapely.ops import split
from shapely import geometry
from pyproj import Geod

app = Flask(__name__)
geod = Geod(ellps="WGS84")  # for accurate area in m²

def calculate_area_m2(polygon: Polygon) -> float:
    lon, lat = polygon.exterior.coords.xy
    return abs(geod.geometry_area_perimeter(geometry.Polygon(zip(lon, lat)))[0])

def subdivide_polygon_auto(coords, n_parts):
    from shapely.geometry import GeometryCollection

    polygon = Polygon(coords)
    bounds = polygon.bounds
    minx, miny, maxx, maxy = bounds
    width = maxx - minx
    height = maxy - miny

    if polygon.is_empty or not polygon.is_valid:
        raise ValueError("Invalid polygon")

    result = polygon
    split_lines = []

    # Determine dominant axis and generate split lines
    if width > height:
        step = width / n_parts
        for i in range(1, n_parts):
            x = minx + i * step
            split_lines.append(LineString([(x, miny - 1), (x, maxy + 1)]))
    else:
        step = height / n_parts
        for i in range(1, n_parts):
            y = miny + i * step
            split_lines.append(LineString([(minx - 1, y), (maxx + 1, y)]))

    # Apply splits one by one
    for line in split_lines:
        try:
            result = split(result, line)
            # if result is a GeometryCollection, ensure it's processed correctly
            if isinstance(result, GeometryCollection):
                result = [geom for geom in result if isinstance(geom, Polygon)]
                result = GeometryCollection(result)
        except Exception as e:
            print(f"Split failed: {e}")

    # Ensure we only return polygons
    polygons = []
    if isinstance(result, GeometryCollection):
        polygons = [geom for geom in result.geoms if isinstance(geom, Polygon)]
    elif isinstance(result, Polygon):
        polygons = [result]

    features = []
    for poly in polygons:
        if poly.area > 0:
            features.append({
                "type": "Feature",
                "geometry": mapping(poly),
                "properties": {
                    "area": round(poly.area, 2)
                }
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }


@app.route("/")
def index():
    return "Plot Subdivision API (Auto Equal Area + Area Calculation) is running"

@app.route("/subdivide", methods=["POST"])
def subdivide():
    data = request.get_json()
    coords = data.get("coordinates")
    count = data.get("count")
    if not coords or not count:
        return jsonify({"error": "Missing 'coordinates' or 'count'"}), 400
    try:
        geojson = subdivide_polygon_auto(coords, int(count))
        return jsonify(geojson)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
