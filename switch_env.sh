#!/bin/bash

# A simple script to switch between local and production environments
# Usage: ./switch_env.sh local  OR  ./switch_env.sh prod

ENV=$1

LOCAL_URL="http://localhost:8000/api/v1"
# For testing the mobile app on a physical device, you might need to change localhost to your computer's local IP address, e.g., 192.168.1.x
MOBILE_LOCAL_URL="http://127.0.0.1:8000/api/v1" 

PROD_URL="https://pariksha365-production-v2.up.railway.app/api/v1"

if [ "$ENV" == "local" ]; then
    echo "🔄 Switching to LOCAL environment..."
    
    # Frontend Web
    echo "VITE_API_URL=$LOCAL_URL" > frontend-web/.env
    echo "✅ Updated frontend-web to $LOCAL_URL"
    
    # Frontend Mobile
    echo "EXPO_PUBLIC_API_URL=$MOBILE_LOCAL_URL" > frontend-mobile/.env
    echo "✅ Updated frontend-mobile to $MOBILE_LOCAL_URL"
    
    echo "--------------------------------------------------------"
    echo "Done! Remember to clear the cache if you are running the bundlers:"
    echo "  Mobile: npx expo start -c"
    echo "  Web:    npm run dev"

elif [ "$ENV" == "prod" ] || [ "$ENV" == "production" ]; then
    echo "🚀 Switching to PRODUCTION environment..."
    
    # Frontend Web
    echo "VITE_API_URL=$PROD_URL" > frontend-web/.env
    echo "✅ Updated frontend-web to $PROD_URL"
    
    # Frontend Mobile
    echo "EXPO_PUBLIC_API_URL=$PROD_URL" > frontend-mobile/.env
    echo "✅ Updated frontend-mobile to $PROD_URL"
    
    echo "--------------------------------------------------------"
    echo "Done! Remember to clear the cache if you are running the bundlers:"
    echo "  Mobile: npx expo start -c"
    echo "  Web:    npm run dev"
    
else
    echo "Usage: ./switch_env.sh [local|prod]"
    echo "Example: ./switch_env.sh local"
    exit 1
fi
