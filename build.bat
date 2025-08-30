@echo off
echo 🚀 Building BizLLCFinder for Vercel deployment...

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Generate static files
echo 🔨 Generating static files...
python build_static.py

REM Copy vercel.json to static_site
echo 📋 Copying Vercel configuration...
copy vercel.json static_site\

echo ✅ Build completed! Static site ready in 'static_site' directory.
echo 🚀 Ready to deploy to Vercel!
pause
