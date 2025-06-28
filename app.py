from flask import Flask, request, jsonify
from flask_cors import CORS
from pyembroidery import read_dst

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return 'Embroidery Parser API is running.'

@app.route('/parse_embroidery', methods=['POST'])
def parse_embroidery():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400

    uploaded_file = request.files['file']

    try:
        pattern = read_dst(uploaded_file)

        # Total stitches (excluding stops, trims, etc.)
        total_stitches = len([s for s in pattern.stitches if s[1] == 0])

        # Needle/colors
        total_colors = len(pattern.threadlist)
        needle = total_colors

        # Get bounding box (raw units)
        min_x = min(point[0] for point in pattern.stitches)
        max_x = max(point[0] for point in pattern.stitches)
        min_y = min(point[1] for point in pattern.stitches)
        max_y = max(point[1] for point in pattern.stitches)

        # Convert to mm (1 unit = 0.1mm)
        width_mm = (max_x - min_x) / 10.0
        height_mm = (max_y - min_y) / 10.0

        # Format as 2 decimal places
        width = f"{width_mm:.2f}"
        height = f"{height_mm:.2f}"
        stitches = f"{total_stitches:,}"
        needle = str(needle)
        formats = "dst"
        area = f"{width} x {height}"

        return jsonify({
            'success': True,
            'stitches': stitches,
            'width': width,
            'height': height,
            'needle': needle,
            'formats': formats,
            'area': area
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
