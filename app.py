from flask import Flask, request, jsonify
from subdivide import subdivide_polygon_vertical, subdivide_polygon_horizontal

app = Flask(__name__)

@app.route("/")
def home():
    return "Subdivision API is running!"

@app.route("/subdivide", methods=["POST"])
def subdivide():
    data = request.get_json()

    if not data or "coordinates" not in data or "count" not in data:
        return jsonify({"error": "Missing 'coordinates' or 'count'"}), 400

    try:
        coords = data["coordinates"]
        count = int(data["count"])
        direction = data.get("direction", "vertical")

        if direction == "horizontal":
            geojson_result = subdivide_polygon_horizontal(coords, count)
        else:
            geojson_result = subdivide_polygon_vertical(coords, count)

        return jsonify(geojson_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
