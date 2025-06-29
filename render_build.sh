#!/bin/bash
echo "---- Installing Python Dependencies ----"
pip install -r requirements.txt

echo "---- Skipping prestart.py (file not found) ----"

echo "---- Checking Redis Connection ----"
python -c "
import os
import redis
try:
    r = redis.Redis.from_url(os.getenv('REDIS_URL'))
    print('Redis ping:', r.ping())
except Exception as e:
    print('Redis connection failed:', e)
"
