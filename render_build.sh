#!/bin/bash
echo "---- Installing Python Dependencies ----"
pip install -r requirements.txt

echo "---- Running Prestart ----"
python prestart.py

echo "---- Checking Redis Connection ----"
python -c "
import os
import redis
r = redis.Redis.from_url(os.getenv('REDIS_URL'))
print('Redis ping:', r.ping())
"
