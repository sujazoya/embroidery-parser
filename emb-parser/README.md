# Embroidery Parser API (EMB/DST Parser)

This is a Flask-based microservice that parses `.emb` and `.dst` embroidery files and returns structured metadata such as:

- Width (mm)
- Height (mm)
- Stitches
- Needles (colors)
- Machine Area
- Design Formats
- Design Name

## 🧠 Tech Stack

- Python
- Flask
- [PyEmbroidery](https://github.com/EmbroidePy/pyembroidery)

## 🚀 API Usage

### `POST /parse_embroidery`

Upload an embroidery file via form-data:

**Form Key:** `emb_file`  
**File Types Supported:** `.emb`, `.dst`

#### ✅ Example Response

```json
{
  "success": true,
  "design_details": {
    "width": 95.2,
    "height": 83.1,
    "stitches": 5321,
    "needles_from_colors": 4,
    "machine_area": 300,
    "formats": "EMB-W6, EMB-E4, DST",
    "design_name": "flower_vintage"
  }
}
