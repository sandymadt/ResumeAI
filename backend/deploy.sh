#!/bin/bash

# 🚀 Backend Deployment Script
# This script automates the deployment process

set -e  # Exit on error

echo "========================================="
echo "🔥 Resume Analyzer Backend Deployment"
echo "========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "firebase.json" ]; then
    echo "❌ Error: firebase.json not found"
    echo "📁 Please run this script from the backend/ directory"
    exit 1
fi

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found"
    echo "📦 Install with: npm install -g firebase-tools"
    exit 1
fi

# Check if logged in
echo "🔐 Checking Firebase authentication..."
firebase login:list || {
    echo "❌ Not logged in to Firebase"
    echo "🔑 Please run: firebase login"
    exit 1
}

# Check if dependencies are installed
if [ ! -d "functions/node_modules" ]; then
    echo "📦 Installing dependencies..."
    cd functions
    npm install
    cd ..
else
    echo "✅ Dependencies already installed"
fi

# Check if OpenAI key is configured
echo "🔑 Checking OpenAI API key configuration..."
OPENAI_KEY=$(firebase functions:config:get openai.key 2>/dev/null || echo "")

if [ -z "$OPENAI_KEY" ] || [ "$OPENAI_KEY" = "{}" ]; then
    echo ""
    echo "⚠️  OpenAI API key not configured!"
    echo ""
    echo "Please set your OpenAI API key:"
    read -p "Enter your OpenAI API key (sk-...): " api_key
    
    if [ -z "$api_key" ]; then
        echo "❌ No API key provided. Exiting."
        exit 1
    fi
    
    echo "🔧 Setting OpenAI API key..."
    firebase functions:config:set openai.key="$api_key"
    echo "✅ API key configured"
else
    echo "✅ OpenAI API key is configured"
fi

# Deploy functions
echo ""
echo "🚀 Deploying Cloud Functions..."
firebase deploy --only functions

echo ""
echo "========================================="
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "========================================="
echo ""
echo "📊 Next steps:"
echo "  1. Check logs: firebase functions:log"
echo "  2. Test from frontend"
echo "  3. Monitor usage in Firebase Console"
echo ""
