#!/bin/bash

echo "🚀 Building BizLLCFinder for Vercel deployment..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Generate static files
echo "🔨 Generating static files..."
python build_static.py

# Copy vercel.json to static_site
echo "📋 Copying Vercel configuration..."
cp vercel.json static_site/

echo "✅ Build completed! Static site ready in 'static_site' directory."
echo "🚀 Ready to deploy to Vercel!"
