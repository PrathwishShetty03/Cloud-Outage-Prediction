#!/usr/bin/env bash
# Stress Server A endpoint via API or CPU load

TARGET_HOST=${1:-"http://localhost:5001"}
STRESS_TYPE=${2:-"cpu"}

echo "⚡ Triggering $STRESS_TYPE stress on target $TARGET_HOST..."

if [ "$STRESS_TYPE" == "cpu" ]; then
    curl -X POST "$TARGET_HOST/stress/cpu" -H "Content-Type: application/json" -d '{"enable": true}'
elif [ "$STRESS_TYPE" == "ram" ]; then
    curl -X POST "$TARGET_HOST/stress/ram" -H "Content-Type: application/json" -d '{"mb": 400}'
elif [ "$STRESS_TYPE" == "latency" ]; then
    curl -X POST "$TARGET_HOST/stress/latency" -H "Content-Type: application/json" -d '{"seconds": 5.5}'
elif [ "$STRESS_TYPE" == "outage" ]; then
    curl -X POST "$TARGET_HOST/simulate/outage"
elif [ "$STRESS_TYPE" == "recover" ]; then
    curl -X POST "$TARGET_HOST/simulate/recover"
else
    echo "Unknown stress type: $STRESS_TYPE"
fi

echo ""
echo "Done."
