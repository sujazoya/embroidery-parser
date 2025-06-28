from flask import Flask, request, jsonify
from flask_cors import CORS
from pyembroidery import read, EmbPattern

app = Flask(__name__)
CORS(app)

def classify_machine_area(width, height):
    # Custom logic for common machine areas
    w, h = width, height
    if w <= 100 and h <= 100:
        return "4x4"
    elif w <= 130 and h <= 180:
        return "5x7"
    elif w <= 160 and h <= 260:
        return "6x10"
    elif w <= 200 and h <= 300:
        return "8x12"
    elif w <= 260 and h <= 400:
        return "10x16"
    elif w <= 300 and h <= 500:
        return "12x20"
    return "Custom"

@app.route('/parse_embroidery', methods=['POST'])
def parse_embroidery():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    f = request.files['file']
    try:
        pattern = read(f)

        # Get basic values
        width = round(pattern.get_width(), 2)
        height = round(pattern.get_height(), 2)
        stitches = len(pattern.stitches)
        thread_count = len(pattern.threadlist)

        area = classify_machine_area(width, height)

        return jsonify({
            "success": True,
            "design_name": f.filename.split('.')[0],
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
