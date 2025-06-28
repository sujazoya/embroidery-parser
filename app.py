from flask import Flask, request, jsonify
from flask_cors import CORS
from pyembroidery import read
import os
import tempfile

app = Flask(__name__)
CORS(app)

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

@app.route('/parse_embroidery', methods=['POST'])
def parse_embroidery():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    uploaded_file = request.files['file']

    try:
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dst") as temp:
            uploaded_file.save(temp.name)
            temp_path = temp.name

        # Parse the file
        pattern = read(temp_path)

        # Clean up temporary file
        os.unlink(temp_path)

        width = round(pattern.get_width(), 2)
        height = round(pattern.get_height(), 2)
        stitches = len(pattern.stitches)
        thread_count = len(pattern.threadlist)
        area = classify_machine_area(width, height)

        return jsonify({
            "success": True,
            "design_name": uploaded_file.filename.rsplit('.', 1)[0],
            "width": f"{width:.2f}",
            "height": f"{height:.2f}",
            "stitches": f"{stitches:,}",
            "needle": str(thread_count),
            "formats": "dst",
            "area": area
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
