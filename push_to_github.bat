@echo off
echo 🚀 Pushing BizLLCFinder to GitHub...

REM Add all files
git add .

REM Commit changes
git commit -m "🔧 EXACT RAMZAN APPROACH - Using csv.DictReader and environment detection"

REM Push to GitHub
git push origin master

echo ✅ Push complete!
echo.
echo 🎯 Next steps:
echo 1. Go to Vercel dashboard
echo 2. Redeploy the project
echo 3. The 500 error should be fixed
pause
