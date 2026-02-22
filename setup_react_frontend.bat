@echo off
echo ============================================
echo   Setting up React Frontend
echo ============================================
echo.

cd /d "%~dp0"

echo Creating React app with Vite...
npm create vite@latest frontend -- --template react

cd frontend

echo.
echo Installing dependencies...
npm install

echo.
echo Installing Tailwind CSS...
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

echo.
echo Installing additional packages...
npm install framer-motion
npm install lucide-react
npm install axios
npm install react-router-dom
npm install recharts
npm install @headlessui/react

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. cd frontend
echo 2. Copy the React components
echo 3. npm run dev
echo.
pause
