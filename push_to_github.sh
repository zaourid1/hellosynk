#!/bin/bash
# Helper script to push to GitHub with Personal Access Token

echo "🚀 Pushing HelloSynk to GitHub..."
echo ""
echo "You'll be prompted for:"
echo "  - Username: Your GitHub username"
echo "  - Password: Your Personal Access Token (NOT your GitHub password)"
echo ""

# Push to GitHub
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "📦 Repository: https://github.com/zaourid1/hellosynk"
else
    echo ""
    echo "❌ Push failed. Please check:"
    echo "   1. You have a valid Personal Access Token"
    echo "   2. The token has 'repo' scope"
    echo "   3. Your internet connection is working"
fi

