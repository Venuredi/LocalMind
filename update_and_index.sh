#!/bin/bash

# Update and Index Script
# Pulls latest code from git and re-indexes

REPO_PATH="$1"

if [ -z "$REPO_PATH" ]; then
    echo "Usage: ./update_and_index.sh /path/to/repo"
    exit 1
fi

echo "📦 Updating repository..."
cd "$REPO_PATH" || exit 1

# Pull latest changes
git pull origin main

echo ""
echo "🔍 Re-indexing repository..."
cd - > /dev/null

# Re-index using CLI
python3 -m code_intelligence index --repo "$REPO_PATH"

echo ""
echo "✅ Done! Repository updated and re-indexed."
