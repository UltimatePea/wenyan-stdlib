#!/bin/bash

# GitHub Authentication Setup Script
# Sets up GitHub CLI and environment variables for agents to use

echo "Setting up GitHub authentication..."

# Get fresh token
GITHUB_TOKEN=$(python3 github_auth.py --get-token)
export GITHUB_TOKEN

echo "Token obtained and exported."

# Verify authentication
echo "Testing GitHub authentication..."
if gh auth status 2>/dev/null; then
    echo "GitHub CLI authentication successful!"
else
    echo "GitHub CLI authentication may have issues, but Python script works."
fi

# Test Python script access
echo "Testing Python script access..."
if python3 github_auth.py --test-auth >/dev/null 2>&1; then
    echo "Python GitHub API access: ✓ Working"
else
    echo "Python GitHub API access: ✗ Failed"
fi

echo ""
echo "GitHub authentication setup complete!"
echo ""
echo "Available tools:"
echo "  - Python script: python3 github_auth.py --help"
echo "  - GitHub CLI: gh (may have limitations)"
echo ""
echo "To use in your session, run:"
echo "  source ./setup_github_auth.sh"