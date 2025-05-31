from flask import Flask, request, jsonify
from subdivide import subdivide_polygon

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
        geojson_result = subdivide_polygon(coords, count)
        return jsonify(geojson_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
