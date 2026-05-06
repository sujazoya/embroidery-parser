app = Flask(__name__)
CORS(app)

# Home route (IMPORTANT for Render)
@app.route("/")
def home():
    return {
        "status": "running",
        "message": "Embroidery Parser API is live 🚀"
    }

# Define hoop size categories
def classify_machine_area(width, height):
    if width <= 100 and height <= 100:
@@ -23,7 +31,6 @@ def classify_machine_area(width, height):
        return "12x20"
    return "Oversized"

# Calculate bounding box from stitches
def calculate_bounding_box(pattern):
    if not pattern.stitches:
        return None
@@ -33,9 +40,7 @@ def calculate_bounding_box(pattern):
        return None
    return min(xs), min(ys), max(xs), max(ys)

# Fallback: count color changes manually
def count_color_changes(pattern):
    # Color change command = 0x20 (decimal 32)
    return sum(1 for point in pattern.stitches if point[2] == 32) + 1

@app.route('/parse_embroidery', methods=['POST'])
@@ -52,23 +57,19 @@ def parse_embroidery():

        pattern = read(temp_path)

        # Calculate bounding box and convert to mm
        bbox = calculate_bounding_box(pattern)
        if not bbox:
            os.unlink(temp_path)
            return jsonify({"success": False, "error": "Could not calculate bounding box"}), 500

        left, top, right, bottom = bbox
        width = round(abs(right - left) / 10, 2)  # Convert from 1/10 mm
        width = round(abs(right - left) / 10, 2)
        height = round(abs(bottom - top) / 10, 2)
        stitches = len(pattern.stitches)

        # Determine thread count (needle) safely
        needle = len(pattern.threadlist) if pattern.threadlist else count_color_changes(pattern)

        area = classify_machine_area(width, height)

        # Clean up temp file
        os.unlink(temp_path)

        return jsonify({
@@ -85,19 +86,7 @@ def parse_embroidery():
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return {
        "status": "running",
        "message": "Embroidery Parser API is live 🚀"
    }
