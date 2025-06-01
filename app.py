
from flask import Flask, request, jsonify
from shapely.geometry import Polygon, LineString, mapping
from shapely.ops import split

app = Flask(__name__)

def subdivide_polygon_auto(coords, n_parts):
    polygon = Polygon(coords)
    bounds = polygon.bounds
    minx, miny, maxx, maxy = bounds
    width = maxx - minx
    height = maxy - miny

    if polygon.is_empty or not polygon.is_valid:
        raise ValueError("Invalid polygon")

    split_lines = []
    if width > height:
        step = width / n_parts
        for i in range(1, n_parts):
            x = minx + i * step
            split_line = LineString([(x, miny - 1), (x, maxy + 1)])
            split_lines.append(split_line)
    else:
        step = height / n_parts
        for i in range(1, n_parts):
            y = miny + i * step
            split_line = LineString([(minx - 1, y), (maxx + 1, y)])
            split_lines.append(split_line)

    for line in split_lines:
        try:
            polygon = split(polygon, line)
        except Exception:
            continue

    if isinstance(polygon, Polygon):
        polygons = [polygon]
    else:
        polygons = list(polygon)

    features = []
    for poly in polygons:
        if poly.area > 0:
            features.append({
                "type": "Feature",
                "geometry": mapping(poly),
                "properties": {"area": poly.area}
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }

@app.route("/")
def index():
    return "Plot Subdivision API (Auto Equal Area) is running"

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
