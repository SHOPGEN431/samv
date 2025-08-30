#!/bin/bash
echo "Building BizLLCFinder for Vercel deployment..."

# Create static directory if it doesn't exist
mkdir -p static/css
mkdir -p static/js

# Copy any static files if they exist
if [ -d "static" ]; then
    echo "Static files found"
else
    echo "Creating static directory structure"
    mkdir -p static/css static/js
fi

echo "Build complete!"
