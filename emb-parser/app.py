from flask import Flask, request, jsonify
from pyembroidery import read_dst, read_emb
import os

app = Flask(__name__)

@app.route('/parse_embroidery', methods=['POST'])
def parse_embroidery():
    if 'emb_file' not in request.files:
        return jsonify(success=False, error="No file uploaded"), 400

    file = request.files['emb_file']
    filename = file.filename.lower()
    filepath = f"/tmp/{filename}"
    file.save(filepath)

    try:
        if filename.endswith('.dst'):
            design = read_dst(filepath)
        elif filename.endswith('.emb'):
            design = read_emb(filepath)
        else:
            return jsonify(success=False, error="Unsupported file type"), 400

        stitches = design.count_stitches()
        width = round(design.extents()[2] - design.extents()[0], 2)
        height = round(design.extents()[3] - design.extents()[1], 2)
        needles = len(design.get_threadlist())
        formats = "DST, EMB"
        machine_area = width if 300 < width < 400 else 300 if width <= 300 else 400

        return jsonify(success=True, design_details={
            "design_name": os.path.splitext(filename)[0],
            "stitches": stitches,
            "width": width,
            "height": height,
            "formats": formats,
            "needles_from_colors": needles,
            "machine_area": machine_area
        })

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500
