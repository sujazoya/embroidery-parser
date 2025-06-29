#!/bin/bash
set -eo pipefail

# Initialize success flag (0 means success)
SCRIPT_SUCCESS=0

# Function to log messages with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle non-critical errors
soft_fail() {
    local message=$1
    log "⚠️ $message (continuing anyway)"
    SCRIPT_SUCCESS=1  # Mark as soft failure
}

log "---- Starting Render Build Script ----"

log "---- Installing Python Dependencies ----"
if [ -f "requirements.txt" ]; then
    if pip install --no-cache-dir -r requirements.txt; then
        log "✅ Dependencies installed successfully"
    else
        soft_fail "Failed to install some dependencies"
    fi
else
    soft_fail "requirements.txt not found"
fi

log "---- Skipping prestart.py (not needed) ----"

log "---- (Optional) Checking Redis Connection ----"
if ! python3 -c '
import os, sys, redis
from urllib.parse import urlparse

def check_redis():
    url = os.getenv("REDIS_URL")
    if not url:
        print("ℹ️ REDIS_URL not set - skipping Redis check")
        return True
    
    try:
        r = redis.Redis.from_url(
            url,
            socket_timeout=5,
            socket_connect_timeout=5,
            health_check_interval=30
        )
        if r.ping():
            print("✅ Redis connection successful")
            return True
        print("⚠️ Redis ping failed")
        return False
    except Exception as e:
        print(f"⚠️ Redis connection check failed: {str(e)}")
        return False

sys.exit(0 if check_redis() else 1)
'; then
    soft_fail "Redis connection check failed"
fi

log "---- Render Build Script Completed ----"
exit $SCRIPT_SUCCESS
