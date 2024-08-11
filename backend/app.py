from flask import Flask, request, jsonify, send_file
import cv2
import numpy as np
from flask_cors import CORS
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
from scipy.spatial import KDTree
from sklearn.cluster import DBSCAN
from sklearn.linear_model import LinearRegression
from shapely.geometry import LineString
from svgpathtools import svg2paths2
from shapely.geometry import LineString, Point, MultiLineString
from shapely.ops import linemerge
from scipy.spatial import cKDTree
import io

app = Flask(__name__)

# Enable CORS
CORS(app)

@app.route('/')
def home():
    return "<p>Hello, World!</p>"

@app.route('/regularization_csv', methods=['POST'])
def detect_and_regularize_shapes():
    csv_file = request.files["file"]
    try:
        # Read CSV file directly from memory
        csv_data = csv_file.read()
        path_XYs = read_csv(csv_data)
        regularized_paths = regularize_shapes(path_XYs)
        fig, ax = plot(regularized_paths)

        # Convert the plot to a PNG image
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
    
        return send_file(buf, mimetype='image/png')
    
    except Exception as e:
        return jsonify({"error": str(e)})

def read_csv(csv_data):
    np_path_XYs = np.genfromtxt(io.BytesIO(csv_data), delimiter=',')
    path_XYs = []

    unique_paths = np.unique(np_path_XYs[:, 0])
    for i in unique_paths:
        npXYs = np_path_XYs[np_path_XYs[:, 0] == i][:, 1:]
        XYs = []
        unique_segments = np.unique(npXYs[:, 0])
        for j in unique_segments:
            XY = npXYs[npXYs[:, 0] == j][:, 1:]
            XYs.append(XY)
        path_XYs.append(XYs)

    return path_XYs

def plot(path_XYs, colors=['r']):
    fig, ax = plt.subplots(tight_layout=True, figsize=(8, 8))
    for i, XYs in enumerate(path_XYs):
        c = colors[i % len(colors)]
        for XY in XYs:
            # Flip the Y-axis by multiplying Y coordinates by -1
            flipped_XY = XY.copy()
            flipped_XY[:, 1] = -flipped_XY[:, 1]
            ax.plot(flipped_XY[:, 0], flipped_XY[:, 1], c=c, linewidth=2)
    ax.set_aspect('equal')
    return fig, ax

def regularize_shapes(path_XYs):
    def is_circle(XY):
        center = np.mean(XY, axis=0)
        distances = [euclidean(point, center) for point in XY]
        avg_distance = np.mean(distances)
        return all(abs(dist - avg_distance) < avg_distance * 0.1 for dist in distances)
    
    def regularize_circle(XY):
        center = np.mean(XY, axis=0)
        radius = np.mean([euclidean(point, center) for point in XY])
        angle_step = 2 * np.pi / len(XY)
        return np.array([[center[0] + radius * np.cos(i * angle_step),
                          center[1] + radius * np.sin(i * angle_step)] for i in range(len(XY))])

    def is_rectangle(XY):
        if len(XY) != 4:
            return False
        angles = []
        for i in range(len(XY)):
            p1 = XY[i]
            p2 = XY[(i + 1) % 4]
            p3 = XY[(i + 2) % 4]
            angle = np.arctan2(p2[1] - p1[1], p2[0] - p1[0]) - np.arctan2(p3[1] - p2[1], p3[0] - p2[0])
            angles.append(np.abs(angle))
        return all(np.isclose(angle, np.pi/2, atol=np.pi/36) for angle in angles)

    def regularize_rectangle(XY):
        center = np.mean(XY, axis=0)
        # Sort points by their angles around the center
        angles = np.arctan2(XY[:, 1] - center[1], XY[:, 0] - center[0])
        sorted_indices = np.argsort(angles)
        sorted_XY = XY[sorted_indices]
        width = np.linalg.norm(sorted_XY[0] - sorted_XY[1])
        height = np.linalg.norm(sorted_XY[1] - sorted_XY[2])
        width_angle = np.arctan2(sorted_XY[1][1] - sorted_XY[0][1], sorted_XY[1][0] - sorted_XY[0][0])
        height_angle = width_angle + np.pi / 2
        
        new_points = []
        for i in range(4):
            angle = width_angle if i % 2 == 0 else height_angle
            distance = width if i % 2 == 0 else height
            new_points.append([center[0] + distance / 2 * np.cos(angle), center[1] + distance / 2 * np.sin(angle)])
            width_angle += np.pi / 2
            height_angle += np.pi / 2
            
        return np.array(new_points)

    def is_star(XY):
        if len(XY) != 10:
            return False
        return True

    def regularize_star(XY):
        center = np.mean(XY, axis=0)
        angles = np.arctan2(XY[:, 1] - center[1], XY[:, 0] - center[0])
        sorted_indices = np.argsort(angles)
        sorted_XY = XY[sorted_indices]
        
        radius1 = np.mean(np.linalg.norm(sorted_XY[0::2] - center, axis=1))
        radius2 = np.mean(np.linalg.norm(sorted_XY[1::2] - center, axis=1))
        
        angle_step = np.pi / 5
        star_points = []
        for i in range(10):
            angle = i * angle_step
            radius = radius1 if i % 2 == 0 else radius2
            star_points.append([center[0] + radius * np.cos(angle), center[1] + radius * np.sin(angle)])
        
        return np.array(star_points)

    def is_regular_polygon(XY, sides):
        if len(XY) != sides:
            return False
        center = np.mean(XY, axis=0)
        angles = [np.arctan2(point[1] - center[1], point[0] - center[0]) for point in XY]
        angles.sort()
        angle_diff = np.diff(angles + [angles[0] + 2 * np.pi])
        return np.all(np.isclose(angle_diff, 2 * np.pi / sides, atol=np.pi/36))

    def regularize_polygon(XY, sides):
        center = np.mean(XY, axis=0)
        angle_step = 2 * np.pi / sides
        radius = np.mean([np.linalg.norm(point - center) for point in XY])
        return np.array([[center[0] + radius * np.cos(i * angle_step),
                          center[1] + radius * np.sin(i * angle_step)] for i in range(sides)])

    regularized_paths = []
    for XYs in path_XYs:
        for XY in XYs:
            if is_circle(XY):
                regularized_paths.append([regularize_circle(XY)])
            elif is_rectangle(XY):
                regularized_paths.append([regularize_rectangle(XY)])
            elif is_star(XY):
                regularized_paths.append([regularize_star(XY)])
            elif is_regular_polygon(XY, 3):  # Triangle
                regularized_paths.append([regularize_polygon(XY, 3)])
            elif is_regular_polygon(XY, 4):  # Rectangle (or Square)
                regularized_paths.append([regularize_polygon(XY, 4)])
            elif is_regular_polygon(XY, 5):  # Pentagon
                regularized_paths.append([regularize_polygon(XY, 5)])
            elif is_regular_polygon(XY, 6):  # Hexagon
                regularized_paths.append([regularize_polygon(XY, 6)])
            else:
                regularized_paths.append([XY])

    return regularized_paths
# New functions for regularization_png route

def fit_line(points):
    X = points[:, 0].reshape(-1, 1)
    y = points[:, 1]
    model = LinearRegression()
    model.fit(X, y)
    slope = model.coef_[0]
    intercept = model.intercept_

    return slope, intercept

def draw_shape(image, shape_type, points):
    if shape_type == "line":
        pt1 = tuple(points[0][0])
        pt2 = tuple(points[1][0])
        cv2.line(image, pt1, pt2, 255, 2)
    elif shape_type == "rectangle":
        x, y, w, h = cv2.boundingRect(points)
        top_left = (x, y)
        bottom_right = (x + w, y + h)
        cv2.rectangle(image, top_left, bottom_right, 255, 2)
    elif shape_type == "circle":
        (x, y), radius = cv2.minEnclosingCircle(points)
        center = (int(x), int(y))
        radius = int(radius)
        cv2.circle(image, center, radius, 255, 2)
    elif shape_type == "polygon":
        cv2.polylines(image, [points], isClosed=True, color=255, thickness=2)

def draw_fitted_line(image, slope, intercept, color):
    height, width = image.shape
    x1, y1 = 0, int(intercept)
    x2, y2 = width, int(slope * width + intercept)

    cv2.line(image, (x1, y1), (x2, y2), color, 2)

def plot_polylines(paths_XYs, save_path=None):
    fig, ax = plt.subplots(tight_layout=True, figsize=(4, 4))
    for i, XYs in enumerate(paths_XYs):
        for XY in XYs:
            ax.plot(XY[:, 0], XY[:, 1], linewidth=2, label=f'Polyline {i}')
    ax.set_aspect("equal")
    ax.axis('off')

    if save_path:
        plt.savefig(save_path, format='jpg')

    plt.show()

def get_shape_name(approx):
    if len(approx) == 2:
        shape_name = "line"
    elif len(approx) == 3:
        shape_name = "triangle"
    elif len(approx) == 4 or len(approx) == 5:
        shape_name = "rectangle"
    elif len(approx) == 10:
        shape_name = "star"
    elif len(approx) > 12:
        shape_name = "circle"
    else:
        shape_name = "polygon"
    return shape_name

@app.route('/regularization_png', methods=['POST'])
def regularization_png():
    image = request.files["file"]
    # image_name = image.filename
    # try:
    #     image.save("./images/" + image_name)
    #     print("Image saved successfully")
    # except Exception as e:
    #     return jsonify({"error": str(e)})
    
    # image_path = "./images/" + image_name
    # img = cv2.imread(image_path)
    try:
        img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
    except Exception as e:
        return jsonify({"error": str(e)})
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 50, 150)
    kernel = np.ones((4, 4), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    shape_image = np.zeros_like(img)

    for i, cont in enumerate(contours):
        if cv2.contourArea(cont) > 100:
            epsilon = 0.0095 * cv2.arcLength(cont, True)
            approx = cv2.approxPolyDP(cont, epsilon, True)
            
            colors = [(0, 0, 255), (0, 128, 255), (0, 255, 255), (0, 255, 0), (255, 0, 0)]
            cv2.drawContours(img, [cont], 0, colors[i % len(colors)], 2)

            M = cv2.moments(cont)
            if M['m00'] != 0.0:
                x = int(M['m10'] / M['m00'])
                y = int(M['m01'] / M['m00'])

            shape_name = get_shape_name(approx)
            x, y, w, h = cv2.boundingRect(cont)
            print("shape is detected as", shape_name)
            cv2.putText(img, shape_name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            if shape_name == 'line':
                draw_shape(shape_image, 'line', approx)
            elif shape_name == 'rectangle':
                draw_shape(shape_image, 'rectangle', approx)
            elif shape_name == 'circle':
                draw_shape(shape_image, 'circle', approx)
            elif shape_name == 'polygon':
                draw_shape(shape_image, 'polygon', approx)
            elif shape_name == 'star':
                draw_shape(shape_image, 'polygon', approx)

    _, buffer = cv2.imencode('.png', shape_image)
    response_image = io.BytesIO(buffer)
    response_image.seek(0)

    return send_file(response_image, mimetype='image/png')

@app.route('/detect_symmetry_png', methods=['POST'])
def detect_and_draw_symmetry():
    image = request.files["file"]
    try:
        # Read image directly from memory
        img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({"error": "Image not found."})

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            x, y, w, h = cv2.boundingRect(cnt)
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
            else:
                cx, cy = x + w // 2, y + h // 2

            cv2.drawContours(img, [cnt], -1, (0, 255, 0), 2)
            num_vertices = len(approx)

            if num_vertices == 3:  # Triangle
                for i in range(3):
                    pt1 = tuple(approx[i][0])
                    pt2 = tuple(approx[(i+1) % 3][0])
                    midpoint = ((pt1[0] + pt2[0]) // 2, (pt1[1] + pt2[1]) // 2)
                    cv2.line(img, midpoint, (cx, cy), (255, 0, 0), 2)
            elif num_vertices == 4:  # Square or Rectangle
                aspect_ratio = float(w) / h
                if 0.9 <= aspect_ratio <= 1.1:  # Square
                    cv2.line(img, (cx, y), (cx, y + h), (255, 0, 0), 2)
                    cv2.line(img, (x, cy), (x + w, cy), (255, 0, 0), 2)
                else:  # Rectangle
                    if w > h:
                        cv2.line(img, (cx, y), (cx, y + h), (255, 0, 0), 2)
                    else:
                        cv2.line(img, (x, cy), (x + w, cy), (255, 0, 0), 2)
            elif num_vertices > 8:  # Circle or Ellipse
                aspect_ratio = float(w) / h
                if 0.9 <= aspect_ratio <= 1.1:  # Circle
                    cv2.line(img, (cx, y), (cx, y + h), (255, 0, 0), 2)
                    cv2.line(img, (x, cy), (x + w, cy), (255, 0, 0), 2)
                else:  # Ellipse
                    cv2.line(img, (cx, y), (cx, y + h), (255, 0, 0), 2)
                    cv2.line(img, (x, cy), (x + w, cy), (255, 0, 0), 2)
            elif num_vertices == 5:  # Pentagon
                cv2.line(img, (cx, y), (cx, y + h), (255, 0, 0), 2)
            elif num_vertices == 6:  # Hexagon
                for i in range(num_vertices):
                    cv2.line(img, (approx[i][0][0], approx[i][0][1]), (cx, cy), (255, 0, 0), 2)
            elif num_vertices == 8:  # Octagon
                for i in range(0, num_vertices, 2):
                    cv2.line(img, (approx[i][0][0], approx[i][0][1]), (cx, cy), (255, 0, 0), 2)

        _, buffer = cv2.imencode('.png', img)
        response_image = io.BytesIO(buffer)
        response_image.seek(0)
    
        return send_file(response_image, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)})

def svg_to_paths(svg_file):
    paths, _, _ = svg2paths2(svg_file)
    return paths

def path_to_line(path, num_points=100):
    t = np.linspace(0, 1, num_points)
    points = np.array([path.point(ti) for ti in t])
    return LineString([(float(p.real), float(p.imag)) for p in points])

def complete_curves(paths, max_distance=5):
    lines = [path_to_line(path) for path in paths]
    
    # Extract all endpoints
    endpoints = []
    for line in lines:
        endpoints.extend([Point(line.coords[0]), Point(line.coords[-1])])
    
    # Build KD-tree for efficient nearest neighbor search
    tree = cKDTree([(p.x, p.y) for p in endpoints])
    
    connections = []
    for i, p in enumerate(endpoints):
        distances, indices = tree.query((p.x, p.y), k=2)  # Find the nearest point (excluding self)
        nearest_index = indices[1]
        nearest_distance = distances[1]
        
        if nearest_distance <= max_distance:
            nearest_point = endpoints[nearest_index]
            connection = LineString([p, nearest_point])
            if not any(existing_line.crosses(connection) for existing_line in lines):
                connections.append(connection)
    
    # Merge original lines and new connections
    all_lines = lines + connections
    merged = linemerge(all_lines)
    
    # Ensure merged is always a list of LineStrings
    if isinstance(merged, LineString):
        merged = [merged]
    elif isinstance(merged, MultiLineString):
        merged = list(merged.geoms)
    
    # Final step: close any nearly closed curves
    final_curves = []
    for curve in merged:
        if not curve.is_ring:
            start, end = Point(curve.coords[0]), Point(curve.coords[-1])
            if start.distance(end) <= max_distance:
                curve = LineString(list(curve.coords) + [curve.coords[0]])
        final_curves.append(curve)
    
    return final_curves

@app.route('/complete_curves_png', methods=['POST'])
def complete_curves_png():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if file and file.filename.endswith('.svg'):
        # Process SVG file
        paths = svg_to_paths(file)
        completed_curves = complete_curves(paths, max_distance=10)

        # Create a BytesIO buffer for the plot
        buf = io.BytesIO()
        plt.figure(figsize=(10, 10))

        # Plot original curves
        for path in paths:
            line = path_to_line(path)
            x, y = line.xy
            plt.plot(x, y, color='blue', linewidth=1, alpha=0.5)

        # Plot completed curves
        for curve in completed_curves:
            x, y = curve.xy
            plt.plot(x, y, color='red', linewidth=2)

        plt.axis('equal')
        plt.title("Completed Curves")
        plt.savefig(buf, format='png')
        buf.seek(0)

        return send_file(buf, mimetype='image/png', as_attachment=True, download_name='completed_curves.png')
    
    return 'Invalid file format', 400

if __name__ == "__main__":
    app.run(debug=True)
