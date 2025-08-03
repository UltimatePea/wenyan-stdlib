#!/usr/bin/env python3
"""
GitHub Access Validation Script
Tests all GitHub authentication and API access functionality
"""

import sys
from github_auth import (
    get_installation_token, 
    github_api_request, 
    get_prs,
    get_issue_details
)

def test_authentication():
    """Test basic authentication"""
    print("🔐 Testing GitHub authentication...")
    try:
        token = get_installation_token()
        print(f"✅ Authentication successful! Token: {token[:10]}...")
        return True
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def test_issues_access():
    """Test issues API access"""
    print("\n📋 Testing Issues API access...")
    try:
        response = github_api_request('/repos/UltimatePea/wenyan-stdlib/issues')
        if response.status_code == 200:
            issues = response.json()
            print(f"✅ Issues API working! Found {len(issues)} issues")
            return True
        else:
            print(f"❌ Issues API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Issues API error: {e}")
        return False

def test_pull_requests():
    """Test pull requests access"""
    print("\n🔄 Testing Pull Requests access...")
    try:
        prs = get_prs()
        print(f"✅ Pull Requests working! Found {len(prs)} open PRs")
        return True
    except Exception as e:
        print(f"❌ Pull Requests error: {e}")
        return False

def test_issue_details():
    """Test getting specific issue details"""
    print("\n🔍 Testing Issue Details access...")
    try:
        issue = get_issue_details(1)
        if issue:
            print(f"✅ Issue Details working! Retrieved issue #{issue['number']}")
            return True
        else:
            print("❌ Issue Details failed: No issue returned")
            return False
    except Exception as e:
        print(f"❌ Issue Details error: {e}")
        return False

def main():
    """Run all validation tests"""
    print("GitHub Access Validation")
    print("=" * 50)
    
    tests = [
        test_authentication,
        test_issues_access,
        test_pull_requests,
        test_issue_details
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All GitHub access functionality is working!")
        print("\n✅ Multi-agent collaboration can proceed")
        print("✅ Issues and PRs can be managed")
        print("✅ API access is properly authenticated")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed")
        print("🔧 Some functionality may be limited")
        return 1

if __name__ == '__main__':
    sys.exit(main())