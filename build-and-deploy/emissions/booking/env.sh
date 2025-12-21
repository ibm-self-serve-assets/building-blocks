#!/bin/sh
# Runtime environment variable injection for React apps in Docker
# This script replaces environment variable placeholders in the built JS files

# Function to replace environment variables in files
replace_env_vars() {
    local file=$1

    # Replace REACT_APP_ENVIZI_API_KEY
    if [ ! -z "$REACT_APP_ENVIZI_API_KEY" ]; then
        sed -i "s|REPLACE_REACT_APP_ENVIZI_API_KEY|$REACT_APP_ENVIZI_API_KEY|g" $file
    fi

    # Replace REACT_APP_ENVIZI_API_URL
    if [ ! -z "$REACT_APP_ENVIZI_API_URL" ]; then
        sed -i "s|REPLACE_REACT_APP_ENVIZI_API_URL|$REACT_APP_ENVIZI_API_URL|g" $file
    fi
}

# Find and process all JS files in the build
for file in /usr/share/nginx/html/static/js/*.js; do
    if [ -f "$file" ]; then
        replace_env_vars $file
    fi
done

echo "Environment variables injected successfully"
