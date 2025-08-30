#!/bin/bash

# BizLLCFinder Deployment Script
echo "🚀 Starting BizLLCFinder deployment..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    git remote add origin https://github.com/SHOPGEN431/samv.git
fi

# Add all files
echo "📦 Adding files to git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "🚀 Deploy BizLLCFinder v1.0.0 - Complete LLC Formation Directory

✨ Features:
- 80+ business categories
- State-specific pages for all 50 states + DC
- Top 3 LLC services with detailed pricing
- Interactive cost calculators
- Local business directory
- SEO optimized with XML sitemap
- Mobile responsive design
- Legal pages (Privacy, Disclosure, Terms)
- Contact form with Google Forms integration

🔧 Technical:
- Flask backend with Python
- Bootstrap 5 frontend
- Vercel deployment ready
- Comprehensive documentation

📅 Date: $(date)"

# Push to GitHub
echo "🌐 Pushing to GitHub..."
git push -u origin main

echo "✅ Deployment complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Go to https://vercel.com"
echo "2. Import your GitHub repository: https://github.com/SHOPGEN431/samv"
echo "3. Vercel will automatically detect the Python project"
echo "4. Deploy and get your live URL!"
echo ""
echo "🌍 Your site will be live at: https://bizllcfinder.site"
