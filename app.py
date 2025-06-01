
from flask import Flask, request, jsonify
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.ops import split
from shapely import affinity
import json

app = Flask(__name__)

def create_polygon(coords):
    return Polygon(coords)

def subdivide_polygon_equal_area(polygon, count, direction):
    total_area = polygon.area
    target_area = total_area / count

    minx, miny, maxx, maxy = polygon.bounds
    slices = []

    if direction == 'vertical':
        width = maxx - minx
        x_start = minx
        step = width / count
        for i in range(count):
            x0 = x_start + i * step
            x1 = x0 + step
            slice_poly = Polygon([
                (x0, miny), (x1, miny), (x1, maxy), (x0, maxy), (x0, miny)
            ])
            intersected = polygon.intersection(slice_poly)
            slices.append(intersected)

    elif direction == 'horizontal':
        height = maxy - miny
        y_start = miny
        step = height / count
        for i in range(count):
            y0 = y_start + i * step
            y1 = y0 + step
            slice_poly = Polygon([
                (minx, y0), (maxx, y0), (maxx, y1), (minx, y1), (minx, y0)
            ])
            intersected = polygon.intersection(slice_poly)
            slices.append(intersected)

    return slices

@app.route('/subdivide', methods=['POST'])
def subdivide():
    data = request.get_json()
    count = int(data['count'])
    direction = data['direction']
    coords = data['coordinates']

    polygon = create_polygon(coords)
    subplots = subdivide_polygon_equal_area(polygon, count, direction)

    features = []
    for poly in subplots:
        if not poly.is_empty:
            coords = list(poly.exterior.coords)
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                },
                "properties": {}
            })

    return jsonify({
        "type": "FeatureCollection",
        "features": features
    })

if __name__ == '__main__':
    app.run(debug=True)
