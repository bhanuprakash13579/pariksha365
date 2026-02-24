#!/bin/bash
set -e

echo "=========================================================="
echo "🚀 Pariksha365 Automated Android Production Build Sequence"
echo "=========================================================="

# Ensure we are in the root directory of the project
if [ ! -f "switch_env.sh" ]; then
    echo "❌ Error: Please run this script from the project root directory (pariksha365/)."
    exit 1
fi

echo ">> 1️⃣ Forcing Production Environment"
./switch_env.sh prod

echo ""
echo ">> 2️⃣ Running Code Quality & Syntax Checks"
cd frontend-mobile

# Check if node_modules exists, if not run npm install
if [ ! -d "node_modules" ]; then
    echo "📦 node_modules not found, installing dependencies..."
    npm install
fi

echo "🔍 Running TypeScript Compiler (tsc --noEmit) to catch any broken code..."
npx tsc --noEmit
echo "✅ Code is clean. No syntax or type errors found!"

echo ""
echo ">> 3️⃣ Auto-incrementing Play Store Version Numbers"
node -e "
const fs = require('fs');
const appJsonPath = './app.json';
const appData = JSON.parse(fs.readFileSync(appJsonPath, 'utf8'));

// Increment Android versionCode
appData.expo.android = appData.expo.android || {};
let currentVersionCode = appData.expo.android.versionCode || 1;
appData.expo.android.versionCode = currentVersionCode + 1;

let currentVersion = appData.expo.version || '1.0.0';
let vParts = currentVersion.split('.');
vParts[vParts.length - 1] = parseInt(vParts[vParts.length - 1]) + 1;
appData.expo.version = vParts.join('.');

fs.writeFileSync(appJsonPath, JSON.stringify(appData, null, 2));
console.log('✅ app.json dynamically updated! New Version: ' + appData.expo.version + ' (Android VersionCode: ' + appData.expo.android.versionCode + ')');
"

echo ""
echo ">> 4️⃣ Initiating LOCAL Android Build (.aab)"
echo "🏗️ Building directly on your Mac to bypass cloud queues..."
eas build --platform android --profile production --local --output ~/Downloads/Pariksha365_Production.aab

echo ""
echo "🎉 Build sequence completed successfully!"
echo "📂 Your App Bundle has been saved to: ~/Downloads/Pariksha365_Production.aab"
