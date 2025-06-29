#!/bin/bash
set -eo pipefail

# Function to log messages with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle errors
error_handler() {
    local exit_code=$?
    local line_number=$1
    local command=$2
    log "❌ Error occurred at line ${line_number}: command '${command}' exited with status ${exit_code}"
    exit ${exit_code}
}

# Trap errors
trap 'error_handler ${LINENO} "${BASH_COMMAND}"' ERR

log "---- Installing Python Dependencies ----"
if [ -f "requirements.txt" ]; then
    pip install --no-cache-dir -r requirements.txt || {
        log "⚠️ Failed to install some dependencies, but continuing..."
    }
else
    log "⚠️ requirements.txt not found, skipping Python dependencies installation"
fi

log "---- Skipping prestart.py (not needed) ----"

log "---- (Optional) Checking Redis Connection ----"
python3 <<'EOF'
import os
import sys
import redis
from urllib.parse import urlparse

def check_redis_connection():
    url = os.getenv('REDIS_URL')
    print(f'REDIS_URL: {url}')
    
    if not url:
        print('⚠️ REDIS_URL is not set.')
        return
        
    try:
        # Validate URL format
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError(f"Invalid Redis URL format: {url}")
            
        # Attempt connection
        r = redis.Redis.from_url(url, socket_timeout=5, socket_connect_timeout=5)
        
        # Test connection
        if not r.ping():
            raise ConnectionError("Redis ping failed")
            
        print('✅ Redis ping successful')
        return True
        
    except redis.exceptions.RedisError as e:
        print(f'⚠️ Redis connection failed (but continuing anyway): {str(e)}')
        return False
    except Exception as e:
        print(f'⚠️ Unexpected error checking Redis (but continuing anyway): {str(e)}')
        return False

check_redis_connection()
EOF

log "---- Setup Completed Successfully ----"
