#!/usr/bin/env python3
"""
Strategic Coordination Documentation Validator
Author: Whisky, PR Worker

Validates that strategic coordination documentation is complete and accurate.
Tests process documentation quality rather than automation functionality.
"""

import os
import sys
import re
from typing import List, Dict, Tuple

def validate_documentation_file(file_path: str) -> Tuple[bool, List[str]]:
    """Validate strategic coordination documentation completeness"""
    errors = []
    
    if not os.path.exists(file_path):
        errors.append(f"Documentation file not found: {file_path}")
        return False, errors
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Required sections for strategic coordination
    required_sections = [
        "Phase 1 Implementation Sequence",
        "Coordination Protocols and Standards", 
        "Resource Allocation Strategy",
        "Project Milestone Coordination",
        "Immediate Implementation Guide"
    ]
    
    for section in required_sections:
        if section not in content:
            errors.append(f"Missing required section: {section}")
    
    # Check for practical templates
    required_templates = [
        "Issue Assignment",
        "Daily Progress Update",
        "GitHub CLI commands"
    ]
    
    for template in required_templates:
        if template not in content:
            errors.append(f"Missing practical template: {template}")
    
    # Check for measurable success metrics
    metrics_patterns = [
        r"Development Velocity.*libraries.*week",
        r"Quality Standards.*coverage",
        r"Response Time.*hours"
    ]
    
    for pattern in metrics_patterns:
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(f"Missing measurable metric pattern: {pattern}")
    
    # Validate GitHub integration examples
    github_commands = ["gh issue", "gh pr", "gh api"]
    github_found = any(cmd in content for cmd in github_commands)
    if not github_found:
        errors.append("Missing GitHub CLI integration examples")
    
    return len(errors) == 0, errors

def validate_issue_alignment() -> Tuple[bool, List[str]]:
    """Validate alignment with Issue #26 requirements"""
    errors = []
    
    # Issue #26 key requirements
    issue_requirements = [
        "strategic implementation sequence",
        "resource allocation strategy",
        "coordination protocols", 
        "cross-team communication",
        "milestone coordination"
    ]
    
    doc_file = "STRATEGIC_COORDINATION_IMPLEMENTATION.md"
    if not os.path.exists(doc_file):
        errors.append(f"Main coordination document not found: {doc_file}")
        return False, errors
    
    with open(doc_file, 'r', encoding='utf-8') as f:
        content = f.read().lower()
    
    for requirement in issue_requirements:
        if requirement not in content:
            errors.append(f"Issue #26 requirement not addressed: {requirement}")
    
    return len(errors) == 0, errors

def validate_practical_usability() -> Tuple[bool, List[str]]:
    """Validate that documentation provides practical, actionable guidance"""
    errors = []
    
    doc_file = "STRATEGIC_COORDINATION_IMPLEMENTATION.md"
    if not os.path.exists(doc_file):
        errors.append("Cannot validate usability - documentation file missing")
        return False, errors
    
    with open(doc_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for actionable commands
    if "```bash" not in content:
        errors.append("Missing bash command examples for practical implementation")
    
    # Check for specific timelines
    if not re.search(r"\d+-\d+ days", content):
        errors.append("Missing specific timeline estimates")
    
    # Check for agent assignment examples  
    if "Agent A" not in content or "Agent B" not in content:
        errors.append("Missing concrete agent assignment examples")
    
    # Check for success criteria
    if "Success Criteria" not in content:
        errors.append("Missing success criteria definition")
    
    return len(errors) == 0, errors

def generate_validation_report() -> Dict:
    """Generate comprehensive validation report"""
    report = {
        "timestamp": "2025-08-04",
        "validation_results": {},
        "overall_status": "PASS",
        "errors": [],
        "recommendations": []
    }
    
    # Validate main documentation
    doc_valid, doc_errors = validate_documentation_file("STRATEGIC_COORDINATION_IMPLEMENTATION.md")
    report["validation_results"]["documentation_completeness"] = {
        "status": "PASS" if doc_valid else "FAIL",
        "errors": doc_errors
    }
    if not doc_valid:
        report["errors"].extend(doc_errors)
    
    # Validate Issue #26 alignment
    issue_valid, issue_errors = validate_issue_alignment()
    report["validation_results"]["issue_alignment"] = {
        "status": "PASS" if issue_valid else "FAIL", 
        "errors": issue_errors
    }
    if not issue_valid:
        report["errors"].extend(issue_errors)
    
    # Validate practical usability
    usability_valid, usability_errors = validate_practical_usability()
    report["validation_results"]["practical_usability"] = {
        "status": "PASS" if usability_valid else "FAIL",
        "errors": usability_errors  
    }
    if not usability_valid:
        report["errors"].extend(usability_errors)
    
    # Overall status
    if report["errors"]:
        report["overall_status"] = "FAIL"
    
    # Recommendations
    if doc_valid and issue_valid and usability_valid:
        report["recommendations"].append("Documentation is complete and ready for implementation")
    else:
        report["recommendations"].append("Address validation errors before PR approval")
    
    return report

def main():
    """Main validation function"""
    print("Strategic Coordination Documentation Validator")
    print("=" * 50)
    
    report = generate_validation_report()
    
    print(f"Overall Status: {report['overall_status']}")
    print(f"Validation Timestamp: {report['timestamp']}")
    print()
    
    for test_name, result in report['validation_results'].items():
        status_symbol = "✅" if result['status'] == 'PASS' else "❌"
        print(f"{status_symbol} {test_name.replace('_', ' ').title()}: {result['status']}")
        
        if result['errors']:
            for error in result['errors']:
                print(f"   - {error}")
    
    print()
    print("Recommendations:")
    for rec in report['recommendations']:
        print(f"- {rec}")
    
    if report['overall_status'] == 'PASS':
        print("\n✅ Strategic coordination documentation validation PASSED")
        return True
    else:
        print(f"\n❌ Strategic coordination documentation validation FAILED ({len(report['errors'])} errors)")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)