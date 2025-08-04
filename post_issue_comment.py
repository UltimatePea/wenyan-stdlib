#!/usr/bin/env python3
"""
Post a comment to a GitHub issue
Author: Whisky, PR Worker
"""

import json
import requests
import sys
from github_auth import get_installation_token

def post_issue_comment(issue_number, comment_body):
    """Post a comment to a specific GitHub issue"""
    token = get_installation_token()
    if not token:
        print("Failed to get installation token")
        return False
    
    url = f"https://api.github.com/repos/UltimatePea/wenyan-stdlib/issues/{issue_number}/comments"
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    
    data = {
        'body': comment_body
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Successfully posted comment to issue #{issue_number}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to post comment to issue #{issue_number}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 post_issue_comment.py <issue_number> <comment_body>")
        sys.exit(1)
    
    issue_number = int(sys.argv[1])
    comment_body = sys.argv[2]
    
    success = post_issue_comment(issue_number, comment_body)
    sys.exit(0 if success else 1)