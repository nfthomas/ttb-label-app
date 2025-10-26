#!/bin/bash

# Configuration
API_URL="http://localhost:8000/api/verify"
# API_URL="https://nfthomas-ttb-label-app-api.onrender.com/api/verify"
IMAGE_PATH="$1"  # First argument should be the path to your image file

# Check if image path is provided
if [ -z "$IMAGE_PATH" ]; then
    echo "Error: Please provide the path to your image file"
    echo "Usage: ./test_api.sh /path/to/your/image.jpg"
    exit 1
fi

# Check if file exists
if [ ! -f "$IMAGE_PATH" ]; then
    echo "Error: File not found: $IMAGE_PATH"
    exit 1
fi

# Make the API call
echo "Testing label verification API..."
echo "Using image: $IMAGE_PATH"

 curl -X POST "${API_URL}" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "image=@${IMAGE_PATH}" \
     -F "brand_name=Old Tom Distillery" \
     -F "product_type=Whiskey" \
     -F "alcohol_content=45" \
     -F "net_contents=750 mL" \
     -F "fuzzy_match=false" \
     | json_pp

echo -e "\nTest completed!"