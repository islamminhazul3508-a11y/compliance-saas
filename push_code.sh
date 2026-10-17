#!/bin/bash
clear
echo "=========================================="
echo "      GitHub One-Click Code Pusher        "
echo "=========================================="
echo ""
echo -n "Paste your GitHub Token (ghp_...) here: "
read -r GITHUB_TOKEN

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: Token cannot be empty!"
    exit 1
fi

echo ""
echo "[*] Connecting to GitHub repository..."
git remote remove origin 2>/dev/null
git remote add origin "https://${GITHUB_TOKEN}@github.com/islamminhazul3508-a11y/compliance-saas.git"
git branch -M main

echo "[*] Uploading project files..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "[SUCCESS] Project uploaded successfully to GitHub!"
else
    echo ""
    echo "[ERROR] Upload failed. Please check token or internet connection."
fi
