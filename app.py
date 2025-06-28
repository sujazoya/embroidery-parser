from flask import Flask, request, jsonify
from flask_cors import CORS
from pyembroidery import read
import os
import tempfile

app = Flask(__name__)
CORS(app)

# Classify hoop size
def classify_machine_area(width, height):
    if width <= 100 and height <= 100:
        return "4x4"
    elif width <= 130 and height <= 180:
        return "5x7"
    elif width <= 160 and height <= 260:
        return "6x10"
    elif width <= 200 and height <= 300:
        return "8x12"
    elif width <= 260 and height <= 400:
        return "10x16"
    elif width <= 300 and height <= 500:
        return "12x20"
    return "Custom"

# Calculate bounding box manually
def calculate_bounding_box(pattern):
    if not pattern.stitches or len(pattern.stitches) == 0:
        return None

    xs = [point[0] for point in pattern.stitches]
    ys = [point[1] for point in pattern.stitches]

    if not xs or not ys:
        return None

    return min(xs), min(ys), max(xs), max(ys)

@app.route('/parse_embroidery', methods=['POST'])
def parse_embroidery():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    uploaded_file = request.files['file']

    try:
        # Save file to temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dst") as temp_file:
            uploaded_file.save(temp_file.name)
            temp_path = temp_file.name

        # Read pattern
        pattern = read(temp_path)

        # Calculate bounding box
        bbox = calculate_bounding_box(pattern)
        if not bbox:
            os.unlink(temp_path)
            return jsonify({"success": False, "error": "Could not calculate bounding box"}), 500

        left, top, right, bottom = bbox
        width = round(abs(right - left), 2)
        height = round(abs(bottom - top), 2)
        stitches = len(pattern.stitches)
        needle = len(pattern.threadlist)
        area = classify_machine_area(width, height)

        os.unlink(temp_path)

        return jsonify({
            "success": True,
            "design_name": uploaded_file.filename.rsplit('.', 1)[0],
            "width": f"{width:.2f}",
            "height": f"{height:.2f}",
            "stitches": f"{stitches:,}",
            "needle": str(needle),
            "formats": "dst",
            "area": area
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
