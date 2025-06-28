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
        bounds = pattern.bounding_box()  # This replaces `.width` and `.height`

        width = round(bounds[2] - bounds[0], 2)  # max_x - min_x
        height = round(bounds[3] - bounds[1], 2)  # max_y - min_y

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
                'width': width,
                'height': height,
                'stitches': stitches,
                'needles_from_colors': colors,
                'machine_area': machine_area,
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
