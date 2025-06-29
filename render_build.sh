#!/bin/bash
set -e

echo "---- Installing Python Dependencies ----"
pip install -r requirements.txt

echo "---- Skipping prestart.py (not needed) ----"

echo "---- (Optional) Checking Redis Connection ----"
python -c "
import os
try:
    import redis
    url = os.getenv('REDIS_URL')
    print(f'REDIS_URL: {url}')
    if url:
        r = redis.Redis.from_url(url)
        r.ping()
        print('✅ Redis ping successful')
    else:
        print('⚠️ REDIS_URL is not set.')
except Exception as e:
    print('⚠️ Redis connection failed (but continuing anyway):', e)
"
