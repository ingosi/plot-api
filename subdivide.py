from flask import Flask, request, jsonify
from shapely.geometry import Polygon, box, mapping
from shapely.ops import unary_union
import geopandas as gpd
import pyproj

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
        direction = data.get("direction", "vertical").lower()

        # Create the original polygon in WGS84
        polygon = Polygon(coords)
        gdf = gpd.GeoDataFrame(index=[0], crs="EPSG:4326", geometry=[polygon])

        # Project to UTM (Kenya is usually EPSG:32736)
        utm_gdf = gdf.to_crs(epsg=32736)
        utm_poly = utm_gdf.geometry.iloc[0]

        minx, miny, maxx, maxy = utm_poly.bounds
        width = (maxx - minx) / count if direction == "vertical" else (maxy - miny) / count

        slices = []
        for i in range(count):
            if direction == "vertical":
                slice_box = box(minx + i * width, miny, minx + (i + 1) * width, maxy)
            else:
                slice_box = box(minx, miny + i * width, maxx, miny + (i + 1) * width)
            slices.append(slice_box.intersection(utm_poly))

        # Filter valid slices
        slices = [s for s in slices if not s.is_empty]

        # Convert back to WGS84
        result_gdf = gpd.GeoDataFrame(geometry=slices, crs="EPSG:32736").to_crs(epsg=4326)

        # Return as GeoJSON FeatureCollection
        features = []
        for poly in result_gdf.geometry:
            features.append({
                "type": "Feature",
                "geometry": mapping(poly),
                "properties": {}
            })

        return jsonify({
            "type": "FeatureCollection",
            "features": features
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
