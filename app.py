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
    polygon = Polygon(coords)
    if polygon.is_empty or not polygon.is_valid:
        raise ValueError("Invalid polygon")

    minx, miny, maxx, maxy = polygon.bounds
    width, height = maxx - minx, maxy - miny

    # Auto choose direction
    step = (width if width > height else height) / n_parts
    lines = []
    for i in range(1, n_parts):
        if width > height:
            x = minx + i * step
            lines.append(LineString([(x, miny - 1), (x, maxy + 1)]))
        else:
            y = miny + i * step
            lines.append(LineString([(minx - 1, y), (maxx + 1, y)]))

    result = polygon
    for line in lines:
        try:
            result = split(result, line)
        except Exception:
            continue

    polygons = list(result) if not isinstance(result, Polygon) else [result]

    features = []
    for poly in polygons:
        if poly.area > 0:
            area_m2 = calculate_area_m2(poly)
            features.append({
                "type": "Feature",
                "geometry": mapping(poly),
                "properties": {"area_m2": round(area_m2, 2)}
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
