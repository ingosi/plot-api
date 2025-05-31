from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return {"message": "Plot API is live!"}

@app.route("/geojson")
def get_geojson():
    sample = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[36.89788, -1.53827], [36.89795, -1.53814], [36.89799, -1.53801], [36.89773, -1.53795], [36.89769, -1.53808], [36.89766, -1.53820], [36.89788, -1.53827]]]
                },
                "properties": {"id": 1}
            }
        ]
    }
    return jsonify(sample)
