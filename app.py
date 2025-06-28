from flask import Flask, request, jsonify
from flask_cors import CORS
from pyembroidery import read_dst
import os

app = Flask(__name__)
CORS(app)

def format_number(value, decimal_places=2, comma=True):
    try:
        if decimal_places == 0:
            value = int(round(float(value)))
            return f"{value:,}" if comma else str(value)
        else:
            formatted = f"{float(value):,.{decimal_places}f}" if comma else f"{float(value):.{decimal_places}f}"
            return formatted
    except Exception:
        return str(value)

@app.route('/parse_embroidery', methods=['POST'])
def parse_dst():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded', 'success': False}), 400

    file = request.files['file']
    filename = file.filename

    if not filename.lower().endswith('.dst'):
        return jsonify({'error': 'Only .dst files are supported', 'success': False}), 400

    try:
        pattern = read_dst(file)

        # Get bounding box or fallbacks
        try:
            bbox = pattern.bounding_box()
            width_mm = (bbox[2] - bbox[0]) / 10.0
            height_mm = (bbox[3] - bbox[1]) / 10.0
        except Exception:
            width_mm = height_mm = 0

        # Get design data
        design_name = filename.rsplit('.', 1)[0]
        stitches = len(pattern.stitches)
        colors = len(pattern.threadlist)
        machine_area = "Large" if width_mm > 250 or height_mm > 250 else "Standard"
        formats = "dst"
        needles = colors

        return jsonify({
            'success': True,
            'design_name': design_name,
            'width': format_number(width_mm),
            'height': format_number(height_mm),
            'stitches': format_number(stitches, 0),
            'needle': format_number(needles, 0),
            'formats': formats,
            'area': machine_area
        })

    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ✅ Render-compatible host and port
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
