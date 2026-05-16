#!/bin/bash
set -e

REPO_DIR="/home/user/property-quiz"
cd "$REPO_DIR"

# Check if remote is configured
if ! git remote | grep -q origin; then
    echo "Error: No git remote 'origin' configured."
    echo "Please add a remote first: git remote add origin <your-github-repo-url>"
    exit 1
fi

# Add and commit changes
git add -A
if git diff --cached --quiet; then
    echo "No changes to deploy."
else
    git commit -m "Update: add redo current question button"
fi

# Push to GitHub Pages (main branch)
BRANCH=$(git branch --show-current)
echo "Pushing to origin/$BRANCH..."
git push origin "$BRANCH"

echo "Deploy completed successfully!"
