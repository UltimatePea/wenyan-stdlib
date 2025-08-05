#!/usr/bin/env python3

import jwt
import time
import requests
import json
import sys
import argparse
from datetime import datetime, timezone

# GitHub App configuration
APP_ID = 1595512
INSTALLATION_ID = 75590650
PRIVATE_KEY_PATH = "/home/zc/worktrees/claudeai-v1.pem"

def load_private_key():
    """Load the private key from file"""
    try:
        with open(PRIVATE_KEY_PATH, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Private key file not found at {PRIVATE_KEY_PATH}")
        sys.exit(1)

def generate_jwt():
    """Generate JWT token for GitHub App authentication"""
    private_key = load_private_key()
    
    now = int(time.time())
    payload = {
        'iat': now - 60,  # Issued at time (with 60 second buffer)
        'exp': now + (10 * 60),  # Expiration time (10 minutes from now)
        'iss': str(APP_ID)  # GitHub App ID
    }
    
    return jwt.encode(payload, private_key, algorithm='RS256')

def get_installation_token():
    """Get installation token using JWT"""
    jwt_token = generate_jwt()
    
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    response = requests.post(
        f'https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens',
        headers=headers
    )
    
    if response.status_code == 201:
        return response.json()['token']
    else:
        print(f"Error getting installation token: {response.status_code}")
        print(response.text)
        sys.exit(1)

def github_api_request(endpoint, method='GET', data=None):
    """Make authenticated GitHub API request"""
    token = get_installation_token()
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    url = f'https://api.github.com{endpoint}'
    
    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=data)
    elif method == 'PATCH':
        response = requests.patch(url, headers=headers, json=data)
    elif method == 'PUT':
        response = requests.put(url, headers=headers, json=data)
    else:
        print(f"Unsupported method: {method}")
        sys.exit(1)
    
    return response

def get_prs():
    """Get open pull requests from the repository"""
    response = github_api_request('/repos/UltimatePea/wenyan-stdlib/pulls?state=open')
    
    if response.status_code == 200:
        prs = response.json()
        if not prs:
            print("No open pull requests found.")
            return []
        
        for pr in prs:
            print(f"PR #{pr['number']}: {pr['title']}")
            print(f"  Created by: {pr['user']['login']}")
            print(f"  State: {pr['state']}")
            print(f"  URL: {pr['html_url']}")
            print(f"  Branch: {pr['head']['ref']}")
            print()
        return prs
    else:
        print(f"Error getting PRs: {response.status_code}")
        print(response.text)
        return []

def get_issues():
    """Get open issues from the repository"""
    response = github_api_request('/repos/UltimatePea/wenyan-stdlib/issues?state=open')
    
    if response.status_code == 200:
        issues = response.json()
        if not issues:
            print("No open issues found.")
            return []
        
        for issue in issues:
            # Skip pull requests (GitHub treats PRs as issues)
            if 'pull_request' in issue:
                continue
            print(f"Issue #{issue['number']}: {issue['title']}")
            print(f"  Created by: {issue['user']['login']}")
            print(f"  State: {issue['state']}")
            print(f"  Created: {issue['created_at']}")
            print(f"  URL: {issue['html_url']}")
            if issue.get('labels'):
                labels = [label['name'] for label in issue['labels']]
                print(f"  Labels: {', '.join(labels)}")
            print()
        return [issue for issue in issues if 'pull_request' not in issue]
    else:
        print(f"Error getting issues: {response.status_code}")
        print(response.text)
        return []

def create_pr(title, body, head_branch, base_branch='main'):
    """Create a new pull request"""
    data = {
        'title': title,
        'body': body,
        'head': head_branch,
        'base': base_branch
    }
    
    response = github_api_request('/repos/UltimatePea/wenyan-stdlib/pulls', method='POST', data=data)
    
    if response.status_code == 201:
        pr = response.json()
        print(f"Pull request created successfully!")
        print(f"PR #{pr['number']}: {pr['title']}")
        print(f"URL: {pr['html_url']}")
        return pr
    else:
        print(f"Error creating PR: {response.status_code}")
        print(response.text)
        return None

def create_issue(repo, title, body):
    """Create a new issue"""
    data = {
        'title': title,
        'body': body
    }
    
    response = github_api_request(f'/repos/{repo}/issues', method='POST', data=data)
    
    if response.status_code == 201:
        issue = response.json()
        print(f"Issue created successfully!")
        print(f"Issue #{issue['number']}: {issue['title']}")
        print(f"URL: {issue['html_url']}")
        return issue
    else:
        print(f"Error creating issue: {response.status_code}")
        print(response.text)
        return None

def get_issue_details(issue_number, repo='UltimatePea/wenyan-stdlib'):
    """Get detailed information about a specific issue"""
    response = github_api_request(f'/repos/{repo}/issues/{issue_number}')
    
    if response.status_code == 200:
        issue = response.json()
        print(f"Issue #{issue['number']}: {issue['title']}")
        print(f"  Created by: {issue['user']['login']}")
        print(f"  State: {issue['state']}")
        print(f"  Created: {issue['created_at']}")
        print(f"  Updated: {issue['updated_at']}")
        print(f"  URL: {issue['html_url']}")
        print(f"  Body: {issue['body']}")
        
        # Get comments
        comments_response = github_api_request(f'/repos/{repo}/issues/{issue_number}/comments')
        if comments_response.status_code == 200:
            comments = comments_response.json()
            if comments:
                print(f"  Comments ({len(comments)}):")
                for comment in comments:
                    print(f"    - {comment['user']['login']} ({comment['created_at']}):")
                    print(f"      {comment['body']}")
            else:
                print("  No comments")
        print()
        return issue
    else:
        print(f"Error getting issue: {response.status_code}")
        print(response.text)
        return None

def create_pr_comment(pr_number, body, repo='UltimatePea/wenyan-stdlib'):
    """Create a comment on a pull request"""
    data = {
        'body': body
    }
    
    response = github_api_request(f'/repos/{repo}/issues/{pr_number}/comments', method='POST', data=data)
    
    if response.status_code == 201:
        comment = response.json()
        print(f"Comment created successfully on PR #{pr_number}")
        print(f"Comment URL: {comment['html_url']}")
        return comment
    else:
        print(f"Error creating PR comment: {response.status_code}")
        print(response.text)
        return None

def main():
    parser = argparse.ArgumentParser(description='GitHub API access tool')
    parser.add_argument('--get-prs', action='store_true', help='Get open pull requests')
    parser.add_argument('--get-issues', action='store_true', help='Get open issues')
    parser.add_argument('--get-issue-details', type=int, help='Get detailed information about specific issue by number')
    parser.add_argument('--create-issue', nargs=3, metavar=('REPO', 'TITLE', 'BODY'), help='Create new issue with repo, title, and body')
    parser.add_argument('--create-pr', nargs=3, metavar=('TITLE', 'BODY', 'HEAD_BRANCH'), help='Create new PR with title, body, and head branch')
    parser.add_argument('--create-pr-comment', nargs=2, metavar=('PR_NUMBER', 'BODY'), help='Create comment on PR')
    parser.add_argument('--test-auth', action='store_true', help='Test authentication')
    parser.add_argument('--get-token', action='store_true', help='Get installation token')
    
    args = parser.parse_args()
    
    if args.get_prs:
        get_prs()
    elif args.get_issues:
        get_issues()
    elif args.get_issue_details:
        get_issue_details(args.get_issue_details)
    elif args.create_issue:
        create_issue(args.create_issue[0], args.create_issue[1], args.create_issue[2])
    elif args.create_pr:
        create_pr(args.create_pr[0], args.create_pr[1], args.create_pr[2])
    elif args.create_pr_comment:
        create_pr_comment(int(args.create_pr_comment[0]), args.create_pr_comment[1])
    elif args.test_auth:
        try:
            token = get_installation_token()
            print("Authentication successful!")
            print(f"Token starts with: {token[:10]}...")
        except Exception as e:
            print(f"Authentication failed: {e}")
    elif args.get_token:
        try:
            token = get_installation_token()
            print(token)
        except Exception as e:
            print(f"Error getting token: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()