#!/bin/bash

echo "========== CAMPUS NETWORK HEALTH CHECK =========="

check_container() {
    CONTAINER=$1

    if [ "$(sudo docker inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null)" = "true" ]; then
        echo "PASS: $CONTAINER is running"
    else
        echo "FAIL: $CONTAINER is not running"
    fi
}

check_container campus-api
check_container campus-redis
check_container campus-router

echo
echo "========== API HEALTH CHECK =========="

if curl -k -s -f https://localhost:8000/health > /dev/null; then
    echo "PASS: API health endpoint is responding"
else
    echo "FAIL: API health endpoint is unavailable"
fi

echo
echo "========== HEALTH CHECK COMPLETE =========="
