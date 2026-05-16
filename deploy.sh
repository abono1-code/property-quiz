#!/bin/bash
set -e

REPO_DIR="/home/user/property-quiz"
cd "$REPO_DIR"

REPO_NAME="property-quiz"
BRANCH="main"

# Ensure we're on main branch
if [ "$(git branch --show-current)" != "$BRANCH" ]; then
    git branch -m "$BRANCH" 2>/dev/null || true
fi

# Configure git user if not set
if [ -z "$(git config user.email)" ]; then
    git config user.email "abo1@coze.email"
    git config user.name "Wuye Quiz"
fi

# Add and commit changes
git add -A
if git diff --cached --quiet; then
    echo "No new changes to deploy."
else
    git commit -m "Update: add redo current question button"
fi

# Check if gh CLI is available and authenticated
if command -v gh &> /dev/null && gh auth status &> /dev/null 2>&1; then
    # Create repo if it doesn't exist
    if ! gh repo view "$REPO_NAME" &> /dev/null 2>&1; then
        echo "Creating GitHub repository: $REPO_NAME"
        gh repo create "$REPO_NAME" --public --source=. --push
        echo "Repository created and code pushed!"
    else
        # Set remote if not set
        if ! git remote | grep -q origin; then
            git remote add origin "https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/"
        fi
        git push -u origin "$BRANCH" --force
        echo "Code pushed to GitHub!"
    fi
    
    # Enable GitHub Pages
    echo "Enabling GitHub Pages..."
    gh api "repos/{owner}/$REPO_NAME/pages" -X POST -f source.branch="$BRANCH" -f source.path="/" 2>/dev/null || \
    echo "GitHub Pages may already be enabled or needs manual setup."
else
    echo "=========================================="
    echo "GitHub authentication required!"
    echo "Please run: gh auth login"
    echo "Then re-run this script."
    echo ""
    echo "Alternatively, manually set up the remote:"
    echo "  git remote add origin https://github.com/<username>/property-quiz.git"
    echo "  git push -u origin $BRANCH"
    echo "=========================================="
    
    # If remote is already configured, try pushing
    if git remote | grep -q origin; then
        echo "Found existing remote, attempting push..."
        git push -u origin "$BRANCH" --force && echo "Push succeeded!" || echo "Push failed - authentication needed."
    fi
fi
