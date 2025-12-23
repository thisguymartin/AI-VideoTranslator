#!/bin/bash

# LibreTranslate Setup Verification Script
# This script verifies that LibreTranslate is properly installed and running

set -e

echo "=========================================="
echo "LibreTranslate Setup Verification"
echo "=========================================="
echo ""

# Check if Docker is installed
echo "1. Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "   ❌ Docker is not installed"
    echo "   Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "   ✅ Docker is installed: $(docker --version)"

# Check if Docker Compose is installed
echo ""
echo "2. Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "   ❌ Docker Compose is not installed"
    echo "   Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
echo "   ✅ Docker Compose is installed"

# Check if docker-compose.yml exists
echo ""
echo "3. Checking docker-compose.yml..."
if [ ! -f "docker-compose.yml" ]; then
    echo "   ❌ docker-compose.yml not found"
    exit 1
fi
echo "   ✅ docker-compose.yml found"

# Check if LibreTranslate container is running
echo ""
echo "4. Checking LibreTranslate container status..."
if docker ps --format '{{.Names}}' | grep -q "videotranslator-libretranslate"; then
    echo "   ✅ LibreTranslate container is running"
else
    echo "   ⚠️  LibreTranslate container is not running"
    echo "   Starting LibreTranslate..."
    docker-compose up -d
    echo "   Waiting for LibreTranslate to start (30 seconds)..."
    sleep 30
fi

# Check LibreTranslate health endpoint
echo ""
echo "5. Checking LibreTranslate health..."
MAX_RETRIES=5
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo "   ✅ LibreTranslate is healthy and responding"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            echo "   ❌ LibreTranslate is not responding"
            echo "   Check logs with: docker-compose logs libretranslate"
            exit 1
        fi
        echo "   ⏳ Waiting for LibreTranslate to be ready (attempt $RETRY_COUNT/$MAX_RETRIES)..."
        sleep 10
    fi
done

# Test languages endpoint
echo ""
echo "6. Testing languages endpoint..."
LANG_COUNT=$(curl -s http://localhost:5000/languages | grep -o '"code"' | wc -l)
if [ "$LANG_COUNT" -gt 0 ]; then
    echo "   ✅ Languages endpoint working ($LANG_COUNT languages available)"
else
    echo "   ❌ Languages endpoint failed"
    exit 1
fi

# Test translation
echo ""
echo "7. Testing translation (English to Spanish)..."
TRANSLATION=$(curl -s -X POST http://localhost:5000/translate \
    -H "Content-Type: application/json" \
    -d '{"q":"Hello, world!","source":"en","target":"es","format":"text"}' \
    | grep -o '"translatedText":"[^"]*"' | cut -d'"' -f4)

if [ -n "$TRANSLATION" ]; then
    echo "   ✅ Translation successful: '$TRANSLATION'"
else
    echo "   ❌ Translation failed"
    exit 1
fi

# Check Python dependencies
echo ""
echo "8. Checking Python dependencies..."
if command -v python3 &> /dev/null; then
    echo "   ✅ Python 3 is installed: $(python3 --version)"

    # Check if httpx is installed
    if python3 -c "import httpx" 2>/dev/null; then
        echo "   ✅ httpx library is installed"
    else
        echo "   ⚠️  httpx library not found"
        echo "   Install with: uv pip install httpx"
    fi
else
    echo "   ⚠️  Python 3 is not installed"
fi

echo ""
echo "=========================================="
echo "✅ All checks passed!"
echo "=========================================="
echo ""
echo "LibreTranslate is ready to use at: http://localhost:5000"
echo ""
echo "Next steps:"
echo "  1. Run example script: python examples/translate_example.py"
echo "  2. Open web UI: http://localhost:5000"
echo "  3. Check documentation: TRANSLATION_GUIDE.md"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f libretranslate"
echo "  - Stop service: docker-compose stop"
echo "  - Restart: docker-compose restart libretranslate"
echo ""
