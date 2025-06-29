import os
import tempfile
import logging
import hashlib
from functools import wraps
from time import time
from concurrent.futures import ThreadPoolExecutor
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from pyembroidery import read, SUPPORTED_EXTENSIONS
from prometheus_flask_exporter import PrometheusMetrics
from celery import Celery

# ===== Configuration =====
app = Flask(__name__)
CORS(app)
metrics = PrometheusMetrics(app)
jwt = JWTManager(app)

# Security & Performance Settings
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback-secret-key')
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Rate Limiting (Prevent Abuse)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute", "1000 per day"]
)

# Celery for Background Tasks
celery = Celery(
    app.name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['REDIS_URL']
)

# Thread Pool for Async Processing
executor = ThreadPoolExecutor(max_workers=8)

# ===== Helper Functions =====
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in SUPPORTED_EXTENSIONS

def file_checksum(filepath):
    """Generate SHA-256 checksum for file integrity check."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def classify_machine_area(width, height):
    sizes = [
        (100, 100, "4x4"),
        (130, 180, "5x7"),
        (160, 260, "6x10"),
        (200, 300, "8x12"),
        (260, 400, "10x16"),
        (300, 500, "12x20")
    ]
    for max_w, max_h, size in sizes:
        if width <= max_w and height <= max_h:
            return size
    return "Oversized"

def calculate_bounding_box(pattern):
    if not pattern.stitches:
        return None
    xs = [point[0] for point in pattern.stitches if len(point) >= 2]
    ys = [point[1] for point in pattern.stitches if len(point) >= 2]
    return min(xs), min(ys), max(xs), max(ys)

def count_color_changes(pattern):
    return sum(1 for point in pattern.stitches if len(point) > 2 and point[2] == 32) + 1

# ===== API Endpoints =====
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "2.0.0"})

@app.route('/auth/token', methods=['POST'])
def generate_token():
    auth = request.authorization
    if not auth or auth.username != "admin" or auth.password != "secure-password":
        return jsonify({"success": False, "error": "Invalid credentials"}), 401
    token = create_access_token(identity=auth.username)
    return jsonify({"success": True, "token": token})

@app.route('/parse_embroidery', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def parse_embroidery():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    uploaded_file = request.files['file']
    if not allowed_file(uploaded_file.filename):
        return jsonify({"success": False, "error": "Unsupported file type"}), 400

    try:
        start_time = time()
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            uploaded_file.save(temp_file.name)
            temp_path = temp_file.name

        # Process file in background (Celery)
        result = process_embroidery_file.delay(temp_path, uploaded_file.filename).get()

        # Clean up temp file
        try:
            os.unlink(temp_path)
        except Exception as e:
            logging.warning(f"Could not delete temp file: {str(e)}")

        processing_time = round(time() - start_time, 3)
        logging.info(f"Processed {uploaded_file.filename} in {processing_time}s")

        return jsonify({
            "success": True,
            "processing_time": processing_time,
            "design_details": result
        })

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "Internal server error"}), 500

@celery.task(bind=True)
def process_embroidery_file(self, file_path, original_filename):
    try:
        pattern = read(file_path)
        bbox = calculate_bounding_box(pattern)
        if not bbox:
            return {"error": "Could not calculate bounding box"}

        left, top, right, bottom = bbox
        width = round(abs(right - left) / 10, 2)
        height = round(abs(bottom - top) / 10, 2)
        stitches = len(pattern.stitches)
        needle = len(pattern.threadlist) if pattern.threadlist else count_color_changes(pattern)
        area = classify_machine_area(width, height)

        return {
            "design_name": secure_filename(original_filename.rsplit('.', 1)[0]),
            "width": width,
            "height": height,
            "stitches": stitches,
            "needle": needle,
            "formats": ",".join(SUPPORTED_EXTENSIONS),
            "area": area,
            "thread_colors": [str(color) for color in pattern.threadlist] if pattern.threadlist else [],
            "file_checksum": file_checksum(file_path)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
