from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pyembroidery import read_dst
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/parse_embroidery', methods=['POST'])
def parse_embroidery():
    if 'emb_file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded.'}), 400

    file = request.files['emb_file']
    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()

    if file_ext != '.dst':
        return jsonify({'success': False, 'error': 'Only .dst files are supported.'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        pattern = read_dst(file_path)
        stitches = len(pattern.stitches)
        colors = len(pattern.threadlist)

        # Manual bounding box calculation
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')

        for stitch in pattern.stitches:
            x, y = stitch[0], stitch[1]
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

        width = round(max_x - min_x, 2)
        height = round(max_y - min_y, 2)

        # Machine Area logic
        if width >= 400:
            machine_area = 400
        elif width <= 300:
            machine_area = 300
        else:
            machine_area = width  # between 300–400

        response = {
    'success': True,
    'design_details': {
        'width': f"{round(width, 2):,.2f}",        # e.g. "390.00"
        'height': f"{round(height, 2):,.2f}",
        'stitches': f"{stitches:,}",               # e.g. "48,272"
        'needles_from_colors': f"{colors}",        # Usually small int, no formatting
        'machine_area': f"{machine_area:,.0f} mm", # e.g. "400 mm"
        'formats': 'DST',
        'design_name': os.path.splitext(filename)[0]
    }
}

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        os.remove(file_path)

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
