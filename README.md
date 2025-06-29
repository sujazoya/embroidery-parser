# Advanced Embroidery Parser API

A high-performance microservice for parsing embroidery files (DST, EMB, PES, etc.) with enhanced features and security.

## Features

- Supports multiple file formats: DST, EMB, EXP, PES, VP3, XXX
- Detailed metadata extraction
- API key authentication
- Rate limiting
- Health monitoring
- Async processing
- Docker support

## API Endpoints

### `POST /parse_embroidery`

**Headers:**
- `X-API-KEY: your-api-key`

**Form Data:**
- `file`: Embroidery file to parse

**Response:**
```json
{
  "success": true,
  "processing_time_seconds": 0.123,
  "design_details": {
    "design_name": "sample",
    "width": "95.20",
    "height": "83.10",
    "stitches": "5,321",
    "needle": "4",
    "formats": "dst,emb,exp,pes,vp3,xxx",
    "area": "4x4",
    "thread_colors": ["#FF0000", "#00FF00"]
  }
}
