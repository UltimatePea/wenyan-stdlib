#!/usr/bin/env python3
"""
GitHub Workflow Integration for Strategic Coordination
Author: Whisky, PR Worker

Provides automated GitHub workflow integration for strategic coordination actions.
This script can be run as a cron job or GitHub Action to maintain continuous coordination.
"""

import json
import time
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from strategic_coordinator import StrategicCoordinator
from github_auth import github_api_request

class CoordinationWorkflow:
    """Automated workflow system for strategic coordination"""
    
    def __init__(self):
        self.coordinator = StrategicCoordinator()
        self.workflow_log = []
    
    def log_action(self, action: str, details: str, success: bool = True):
        """Log workflow actions for tracking"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details,
            'success': success
        }
        self.workflow_log.append(entry)
        print(f"[{entry['timestamp']}] {action}: {details} - {'SUCCESS' if success else 'FAILED'}")
    
    def check_stale_assignments(self, days_threshold: int = 3) -> List[int]:
        """Check for assignments that haven't been updated in specified days"""
        stale_issues = []
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        # Check GitHub for last activity on assigned issues
        for issue_number, issue in self.coordinator.issues.items():
            if issue.assigned_agent and issue.state == 'open':
                # Get issue comments to check last activity
                response = github_api_request(f'/repos/UltimatePea/wenyan-stdlib/issues/{issue_number}')
                if response.status_code == 200:
                    issue_data = response.json()
                    updated_at = datetime.fromisoformat(issue_data['updated_at'].replace('Z', '+00:00'))
                    
                    # Make cutoff_date timezone-aware to match updated_at
                    cutoff_date_aware = cutoff_date.replace(tzinfo=updated_at.tzinfo)
                    
                    if updated_at < cutoff_date_aware:
                        stale_issues.append(issue_number)
                        self.log_action(
                            'stale_detection',
                            f"Issue #{issue_number} assigned to {issue.assigned_agent} stale for {days_threshold}+ days"
                        )
        
        return stale_issues
    
    def send_stale_reminders(self, stale_issues: List[int]):
        """Send reminder comments for stale issues"""
        for issue_number in stale_issues:
            issue = self.coordinator.issues[issue_number]
            
            reminder_body = f"""## Stale Assignment Reminder

**Assigned Agent**: {issue.assigned_agent}
**Days Since Last Update**: 3+

This issue has been assigned but hasn't seen activity recently. Please provide a progress update including:

- Current status and progress percentage
- Any blockers encountered
- Estimated completion timeline
- Whether reassignment is needed

If no response within 24 hours, this issue may be reassigned to maintain project momentum.

**Author: Whisky, PR Worker - Automated Workflow System**
"""
            
            response = github_api_request(
                f'/repos/UltimatePea/wenyan-stdlib/issues/{issue_number}/comments',
                method='POST',
                data={'body': reminder_body}
            )
            
            success = response.status_code == 201
            self.log_action(
                'stale_reminder',
                f"Sent reminder for issue #{issue_number} to {issue.assigned_agent}",
                success
            )
    
    def auto_reassign_abandoned_issues(self, days_threshold: int = 7) -> List[int]:
        """Automatically reassign issues abandoned for too long"""
        reassigned_issues = []
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        for issue_number, issue in self.coordinator.issues.items():
            if issue.assigned_agent and issue.state == 'open':
                # Check if issue has been stale for reassignment threshold
                response = github_api_request(f'/repos/UltimatePea/wenyan-stdlib/issues/{issue_number}')
                if response.status_code == 200:
                    issue_data = response.json()
                    updated_at = datetime.fromisoformat(issue_data['updated_at'].replace('Z', '+00:00'))
                    
                    # Make cutoff_date timezone-aware to match updated_at
                    cutoff_date_aware = cutoff_date.replace(tzinfo=updated_at.tzinfo)
                    
                    if updated_at < cutoff_date_aware:
                        # Remove from current agent
                        old_agent = issue.assigned_agent
                        if old_agent in self.coordinator.agents:
                            if issue_number in self.coordinator.agents[old_agent].current_issues:
                                self.coordinator.agents[old_agent].current_issues.remove(issue_number)
                        
                        # Clear assignment
                        issue.assigned_agent = None
                        
                        # Try to reassign
                        if self.coordinator.assign_issue(issue_number):
                            reassigned_issues.append(issue_number)
                            self.log_action(
                                'auto_reassign',
                                f"Reassigned issue #{issue_number} from {old_agent} to {issue.assigned_agent}"
                            )
                            
                            # Post reassignment comment
                            self.post_reassignment_comment(issue_number, old_agent, issue.assigned_agent)
        
        return reassigned_issues
    
    def post_reassignment_comment(self, issue_number: int, old_agent: str, new_agent: str):
        """Post comment about automatic reassignment"""
        comment_body = f"""## Automatic Reassignment

This issue has been automatically reassigned due to inactivity.

**Previous Agent**: {old_agent}
**New Agent**: {new_agent}
**Reason**: No activity for 7+ days

The new agent should:
1. Review all previous work and comments
2. Assess current state and requirements
3. Provide updated timeline estimate
4. Begin active development with daily updates

**Author: Whisky, PR Worker - Automated Workflow System**
"""
        
        github_api_request(
            f'/repos/UltimatePea/wenyan-stdlib/issues/{issue_number}/comments',
            method='POST',
            data={'body': comment_body}
        )
    
    def monitor_pr_status(self) -> Dict[str, List[int]]:
        """Monitor pull request status for assigned issues"""
        pr_status = {
            'ready_for_review': [],
            'merge_conflicts': [],
            'ci_failures': [],
            'approved': []
        }
        
        # Get all open PRs
        response = github_api_request('/repos/UltimatePea/wenyan-stdlib/pulls?state=open')
        if response.status_code != 200:
            self.log_action('pr_monitoring', 'Failed to fetch PRs', False)
            return pr_status
        
        prs = response.json()
        
        for pr in prs:
            pr_number = pr['number']
            
            # Check if PR has associated issue (look for "Fix #N" in title/body)
            associated_issues = self.extract_issue_numbers_from_text(pr['title'] + ' ' + (pr['body'] or ''))
            
            # Check mergeable status
            mergeable_state = pr.get('mergeable_state', 'unknown')
            if mergeable_state == 'dirty':
                pr_status['merge_conflicts'].append(pr_number)
                self.log_action('pr_monitoring', f"PR #{pr_number} has merge conflicts")
            
            # Check CI status
            if mergeable_state == 'unstable':
                pr_status['ci_failures'].append(pr_number)
                self.log_action('pr_monitoring', f"PR #{pr_number} has CI failures")
            
            # Check review status
            reviews_response = github_api_request(f'/repos/UltimatePea/wenyan-stdlib/pulls/{pr_number}/reviews')
            if reviews_response.status_code == 200:
                reviews = reviews_response.json()
                approved_reviews = [r for r in reviews if r.get('state') == 'APPROVED']
                if approved_reviews:
                    pr_status['approved'].append(pr_number)
                elif not reviews:  # No reviews yet
                    pr_status['ready_for_review'].append(pr_number)
        
        return pr_status
    
    def extract_issue_numbers_from_text(self, text: str) -> List[int]:
        """Extract issue numbers from text using patterns like 'Fix #123' or 'Closes #123'"""
        import re
        patterns = [
            r'[Ff]ix #(\d+)',
            r'[Cc]loses #(\d+)',
            r'[Rr]esolves #(\d+)',
            r'#(\d+)'
        ]
        
        issue_numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            issue_numbers.extend([int(match) for match in matches])
        
        return list(set(issue_numbers))  # Remove duplicates
    
    def generate_daily_status_report(self) -> Dict:
        """Generate daily status report for project coordination"""
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'resource_allocation': self.coordinator.generate_resource_allocation_report(),
            'stale_assignments': self.check_stale_assignments(),
            'pr_status': self.monitor_pr_status(),
            'workflow_actions': len(self.workflow_log),
            'recommendations': []
        }
        
        # Generate actionable recommendations
        if report['stale_assignments']:
            report['recommendations'].append(
                f"Send reminders to {len(report['stale_assignments'])} stale assignments"
            )
        
        if report['pr_status']['merge_conflicts']:
            report['recommendations'].append(
                f"Resolve merge conflicts in {len(report['pr_status']['merge_conflicts'])} PRs"
            )
        
        if report['pr_status']['ci_failures']:
            report['recommendations'].append(
                f"Fix CI failures in {len(report['pr_status']['ci_failures'])} PRs"
            )
        
        if report['resource_allocation']['resource_utilization'] < 0.5:
            report['recommendations'].append("Low resource utilization - consider assigning more issues")
        
        return report
    
    def post_daily_report_comment(self, report: Dict):
        """Post daily coordination report as GitHub issue comment"""
        # Find or create coordination tracking issue
        coordination_issue = self.find_or_create_coordination_issue()
        
        if not coordination_issue:
            self.log_action('daily_report', 'Could not find/create coordination issue', False)
            return
        
        report_body = f"""## Daily Coordination Report - {report['date']}

### Resource Allocation
- **Utilization**: {report['resource_allocation']['resource_utilization']:.1%}
- **Assigned Issues**: {report['resource_allocation']['issues']['assigned']}
- **Unassigned Issues**: {report['resource_allocation']['issues']['unassigned']}

### Issue Status
- **Stale Assignments**: {len(report['stale_assignments'])}
- **Active PRs**: {len(report['pr_status']['ready_for_review']) + len(report['pr_status']['approved'])}
- **PRs with Issues**: {len(report['pr_status']['merge_conflicts']) + len(report['pr_status']['ci_failures'])}

### Recommendations
{chr(10).join(f'- {rec}' for rec in report['recommendations']) if report['recommendations'] else '- No critical actions needed'}

### Agent Status
"""
        
        for agent_name, agent_data in report['resource_allocation']['agents'].items():
            report_body += f"- **{agent_name}**: {agent_data['current_workload']}/{agent_data['max_capacity']} issues ({agent_data['utilization']:.1%} utilized)\\n"
        
        report_body += "\\n**Author: Whisky, PR Worker - Daily Coordination Report**"
        
        response = github_api_request(
            f'/repos/UltimatePea/wenyan-stdlib/issues/{coordination_issue}/comments',
            method='POST',
            data={'body': report_body}
        )
        
        success = response.status_code == 201
        self.log_action('daily_report', f'Posted daily report to issue #{coordination_issue}', success)
    
    def find_or_create_coordination_issue(self) -> Optional[int]:
        """Find existing coordination tracking issue or create one"""
        # Search for existing coordination issue
        search_response = github_api_request('/repos/UltimatePea/wenyan-stdlib/issues?labels=coordination&state=open')
        
        if search_response.status_code == 200:
            issues = search_response.json()
            coordination_issues = [
                issue for issue in issues 
                if 'coordination' in issue['title'].lower() or 'strategic' in issue['title'].lower()
            ]
            
            if coordination_issues:
                return coordination_issues[0]['number']
        
        # Create new coordination tracking issue
        issue_data = {
            'title': 'Strategic Coordination Tracking',
            'body': '''## Strategic Coordination Tracking Issue

This issue tracks daily coordination reports and strategic development coordination activities.

**Purpose**: 
- Daily status reports and resource allocation updates  
- Agent assignment and progress tracking
- Automated workflow notifications

**Author: Whisky, PR Worker - Strategic Coordination System**
''',
            'labels': ['coordination', 'tracking', 'automated']
        }
        
        response = github_api_request(
            '/repos/UltimatePea/wenyan-stdlib/issues',
            method='POST',
            data=issue_data
        )
        
        if response.status_code == 201:
            return response.json()['number']
        
        return None
    
    def run_daily_workflow(self):
        """Run complete daily coordination workflow"""
        print(f"Starting daily coordination workflow at {datetime.now()}")
        
        # 1. Sync with GitHub
        self.coordinator.sync_with_github()
        self.log_action('sync', 'Synced with GitHub issues and PRs')
        
        # 2. Auto-assign unassigned issues
        assigned = self.coordinator.auto_assign_unassigned_issues()
        if assigned:
            self.log_action('auto_assign', f'Auto-assigned {len(assigned)} issues: {assigned}')
        
        # 3. Check for stale assignments and send reminders
        stale_issues = self.check_stale_assignments(days_threshold=3)
        if stale_issues:
            self.send_stale_reminders(stale_issues)
        
        # 4. Reassign truly abandoned issues
        reassigned = self.auto_reassign_abandoned_issues(days_threshold=7)
        if reassigned:
            self.log_action('reassign', f'Reassigned {len(reassigned)} abandoned issues')
        
        # 5. Monitor PR status
        pr_status = self.monitor_pr_status()
        self.log_action('pr_monitor', f'Monitored {sum(len(v) for v in pr_status.values())} PRs')
        
        # 6. Generate and post daily report
        report = self.generate_daily_status_report()
        self.post_daily_report_comment(report)
        
        # 7. Save workflow log
        self.save_workflow_log()
        
        print(f"Daily workflow completed with {len(self.workflow_log)} actions")
        return report
    
    def save_workflow_log(self):
        """Save workflow execution log"""
        log_file = f"coordination_log_{datetime.now().strftime('%Y%m%d')}.json"
        with open(log_file, 'w') as f:
            json.dump(self.workflow_log, f, indent=2, default=str)

def main():
    """Command-line interface for coordination workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Strategic Coordination Workflow')
    parser.add_argument('--daily', action='store_true', help='Run daily coordination workflow')
    parser.add_argument('--check-stale', type=int, default=3, help='Check for stale assignments (days)')  
    parser.add_argument('--reassign-abandoned', type=int, default=7, help='Reassign abandoned issues (days)')
    parser.add_argument('--monitor-prs', action='store_true', help='Monitor PR status')
    parser.add_argument('--report', action='store_true', help='Generate status report')
    
    args = parser.parse_args()
    
    workflow = CoordinationWorkflow()
    
    if args.daily:
        workflow.run_daily_workflow()
    
    if args.check_stale:
        stale = workflow.check_stale_assignments(args.check_stale)
        print(f"Found {len(stale)} stale assignments: {stale}")
        workflow.send_stale_reminders(stale)
    
    if args.reassign_abandoned:
        reassigned = workflow.auto_reassign_abandoned_issues(args.reassign_abandoned)
        print(f"Reassigned {len(reassigned)} abandoned issues: {reassigned}")
    
    if args.monitor_prs:
        status = workflow.monitor_pr_status()
        print(json.dumps(status, indent=2))
    
    if args.report:
        report = workflow.generate_daily_status_report()
        print(json.dumps(report, indent=2, default=str))

if __name__ == '__main__':
    main()