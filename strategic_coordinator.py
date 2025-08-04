#!/usr/bin/env python3
"""
Strategic Development Coordinator
Author: Whisky, PR Worker

This module implements functional strategic coordination for the Wenyan Standard Library project.
It provides automated agent assignment, progress tracking, resource allocation, and GitHub integration.

Addresses Issue #26 - Strategic Development Coordination with actual working systems.
"""

import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from github_auth import github_api_request

@dataclass
class Agent:
    """Represents a development agent with skills and current workload"""
    name: str
    skills: List[str]  # e.g., ['string-processing', 'file-operations', 'math-libraries']
    current_issues: List[int]  # Issue numbers currently assigned
    max_concurrent: int = 2  # Maximum concurrent issues
    performance_score: float = 1.0  # Based on past completion times and quality
    
    def is_available(self) -> bool:
        """Check if agent can take on new work"""
        return len(self.current_issues) < self.max_concurrent
    
    def skill_match_score(self, required_skills: List[str]) -> float:
        """Calculate how well agent skills match issue requirements"""
        if not required_skills:
            return 0.5  # Neutral score for issues without specific skill requirements
        
        matches = sum(1 for skill in required_skills if skill in self.skills)
        return (matches / len(required_skills)) * self.performance_score

@dataclass
class Issue:
    """Represents a GitHub issue with coordination metadata"""
    number: int
    title: str
    state: str
    labels: List[str]
    assigned_agent: Optional[str] = None
    estimated_complexity: int = 3  # 1-5 scale
    required_skills: List[str] = None
    deadline: Optional[datetime] = None
    dependencies: List[int] = None  # Issue numbers that must be completed first
    
    def __post_init__(self):
        if self.required_skills is None:
            self.required_skills = []
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class ProgressReport:
    """Progress tracking report for an issue or agent"""
    timestamp: datetime
    agent: str
    issue_number: int
    status: str  # 'assigned', 'in_progress', 'blocked', 'ready_for_review', 'completed'
    progress_percentage: int
    blockers: List[str]
    next_steps: List[str]
    estimated_completion: Optional[datetime] = None

class StrategicCoordinator:
    """Main coordination system that manages agents, issues, and resources"""
    
    def __init__(self, config_file: str = "coordination_config.json"):
        self.config_file = config_file
        self.agents: Dict[str, Agent] = {}
        self.issues: Dict[int, Issue] = {}
        self.progress_reports: List[ProgressReport] = []
        self.load_configuration()
    
    def load_configuration(self):
        """Load agent and issue configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                
            # Load agents
            for agent_data in config.get('agents', []):
                agent = Agent(**agent_data)
                self.agents[agent.name] = agent
                
            # Load known issues
            for issue_data in config.get('issues', []):
                issue = Issue(**issue_data)
                self.issues[issue.number] = issue
                
            # If no agents are loaded, create default configuration
            if not self.agents:
                self.create_default_configuration()
                
        except FileNotFoundError:
            # Initialize with default configuration
            self.create_default_configuration()
    
    def create_default_configuration(self):
        """Create default agent and issue configuration"""
        # Default agent profiles based on observed project patterns
        default_agents = [
            Agent(
                name="StringOperationsAgent",
                skills=["string-processing", "text-manipulation", "unicode-handling"],
                current_issues=[],
                max_concurrent=2,
                performance_score=1.0
            ),
            Agent(
                name="MathLibraryAgent", 
                skills=["mathematical-operations", "algorithms", "numerical-computing"],
                current_issues=[],
                max_concurrent=2,
                performance_score=1.0
            ),
            Agent(
                name="FileSystemAgent",
                skills=["file-operations", "io-handling", "data-persistence"],
                current_issues=[],
                max_concurrent=1,
                performance_score=1.0
            ),
            Agent(
                name="GeneralPurposeAgent",
                skills=["documentation", "testing", "integration", "general-programming"],
                current_issues=[],
                max_concurrent=3,
                performance_score=0.8
            )
        ]
        
        for agent in default_agents:
            self.agents[agent.name] = agent
            
        self.save_configuration()
    
    def save_configuration(self):
        """Save current configuration to file"""
        config = {
            'agents': [asdict(agent) for agent in self.agents.values()],
            'issues': [asdict(issue) for issue in self.issues.values()],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2, default=str)
    
    def fetch_github_issues(self, state: str = 'open') -> List[Dict]:
        """Fetch issues from GitHub API"""
        response = github_api_request(f'/repos/UltimatePea/wenyan-stdlib/issues?state={state}&per_page=100')
        
        if response.status_code == 200:
            issues_data = response.json()
            # Filter out pull requests (they have 'pull_request' key)
            return [issue for issue in issues_data if 'pull_request' not in issue]
        else:
            print(f"Error fetching issues: {response.status_code}")
            return []
    
    def analyze_issue_requirements(self, issue_data: Dict) -> Tuple[List[str], int]:
        """Analyze issue to determine required skills and complexity"""
        title = issue_data['title'].lower()
        body = issue_data.get('body', '').lower()
        labels = [label['name'].lower() for label in issue_data.get('labels', [])]
        
        # Skill mapping based on keywords
        skills = []
        complexity = 3  # Default medium complexity
        
        # String processing keywords
        if any(keyword in title + body for keyword in ['string', '字符串', 'text', 'character']):
            skills.append('string-processing')
            
        # Math keywords
        if any(keyword in title + body for keyword in ['math', '算', 'calculation', 'number', 'numeric']):
            skills.append('mathematical-operations')
            
        # File operations keywords
        if any(keyword in title + body for keyword in ['file', '檔', 'io', 'read', 'write', 'data']):
            skills.append('file-operations')
            
        # Testing keywords
        if any(keyword in title + body for keyword in ['test', '測試', 'testing', 'validation']):
            skills.append('testing')
            
        # Documentation keywords
        if any(keyword in title + body for keyword in ['doc', 'readme', 'documentation', '文檔']):
            skills.append('documentation')
            
        # Complexity estimation based on labels and content
        if 'enhancement' in labels or 'feature' in labels:
            complexity = 4
        if 'bug' in labels:
            complexity = 2
        if 'good first issue' in labels:
            complexity = 1
        if 'help wanted' in labels or 'complex' in title + body:
            complexity = 5
            
        return skills, complexity
    
    def find_best_agent(self, issue: Issue) -> Optional[str]:
        """Find the best available agent for an issue"""
        if not issue.required_skills:
            # For issues without specific skills, prefer agents with lower workload
            available_agents = [(name, agent) for name, agent in self.agents.items() if agent.is_available()]
            if available_agents:
                # Sort by current workload (ascending)
                available_agents.sort(key=lambda x: len(x[1].current_issues))
                return available_agents[0][0]
            return None
        
        best_agent = None
        best_score = 0.0
        
        for name, agent in self.agents.items():
            if not agent.is_available():
                continue
                
            score = agent.skill_match_score(issue.required_skills)
            
            # Boost score for agents with fewer current assignments
            workload_factor = 1.0 - (len(agent.current_issues) / agent.max_concurrent * 0.3)
            score *= workload_factor
            
            if score > best_score:
                best_score = score
                best_agent = name
        
        return best_agent if best_score > 0.1 else None  # Minimum threshold (adjusted per Delta feedback)
    
    def assign_issue(self, issue_number: int, agent_name: Optional[str] = None) -> bool:
        """Assign an issue to an agent (auto-select if not specified)"""
        if issue_number not in self.issues:
            print(f"Issue #{issue_number} not found in coordination system")
            return False
        
        issue = self.issues[issue_number]
        
        if agent_name is None:
            agent_name = self.find_best_agent(issue)
            
        if agent_name is None or agent_name not in self.agents:
            print(f"No suitable agent found for issue #{issue_number}")
            return False
        
        agent = self.agents[agent_name]
        if not agent.is_available():
            print(f"Agent {agent_name} is not available (has {len(agent.current_issues)} assignments)")
            return False
        
        # Check dependencies
        for dep_issue in issue.dependencies:
            if dep_issue in self.issues and self.issues[dep_issue].state != 'closed':
                print(f"Issue #{issue_number} blocked by dependency #{dep_issue}")
                return False
        
        # Assign the issue
        issue.assigned_agent = agent_name
        agent.current_issues.append(issue_number)
        
        # Create assignment comment on GitHub
        self.post_assignment_comment(issue_number, agent_name)
        
        # Create initial progress report
        report = ProgressReport(
            timestamp=datetime.now(),
            agent=agent_name,
            issue_number=issue_number,
            status='assigned',
            progress_percentage=0,
            blockers=[],
            next_steps=['Set up development environment', 'Analyze requirements', 'Create feature branch']
        )
        self.progress_reports.append(report)
        
        self.save_configuration()
        print(f"Issue #{issue_number} assigned to {agent_name}")
        return True
    
    def post_assignment_comment(self, issue_number: int, agent_name: str):
        """Post assignment comment to GitHub issue"""
        issue = self.issues[issue_number]
        agent = self.agents[agent_name]
        
        comment_body = f"""## Strategic Assignment - Issue #{issue_number}

**Assigned Agent**: {agent_name}
**Timeline**: {self.estimate_completion_time(issue)} days
**Agent Skills**: {', '.join(agent.skills)}
**Estimated Complexity**: {issue.estimated_complexity}/5

### Coordination Requirements:
- Daily progress updates required
- Commit code daily (even if incomplete) 
- Test coverage >90% before PR submission
- Follow Chinese naming conventions for Wenyan code

### Success Criteria:
- All issue requirements implemented and tested
- PR submitted with "Fix #{issue_number}" in title/description
- Code passes all existing tests
- Documentation updated as needed

### Dependencies:
{f"- Depends on issues: {', '.join(f'#{dep}' for dep in issue.dependencies)}" if issue.dependencies else "- No blocking dependencies"}

**Author: Whisky, PR Worker - Strategic Coordination System**
"""
        
        response = github_api_request(
            f'/repos/UltimatePea/wenyan-stdlib/issues/{issue_number}/comments',
            method='POST',
            data={'body': comment_body}
        )
        
        if response.status_code != 201:
            print(f"Warning: Could not post assignment comment to issue #{issue_number}")
    
    def estimate_completion_time(self, issue: Issue) -> int:
        """Estimate completion time in days based on complexity"""
        base_days = {1: 1, 2: 2, 3: 3, 4: 5, 5: 8}
        return base_days.get(issue.estimated_complexity, 3)
    
    def update_issue_progress(self, issue_number: int, status: str, progress_percentage: int, 
                            blockers: List[str] = None, next_steps: List[str] = None) -> bool:
        """Update progress for an issue"""
        if issue_number not in self.issues:
            return False
        
        issue = self.issues[issue_number]
        if not issue.assigned_agent:
            return False
        
        report = ProgressReport(
            timestamp=datetime.now(),
            agent=issue.assigned_agent,
            issue_number=issue_number,
            status=status,
            progress_percentage=progress_percentage,
            blockers=blockers or [],
            next_steps=next_steps or []
        )
        
        self.progress_reports.append(report)
        
        # Post progress update to GitHub
        self.post_progress_comment(issue_number, report)
        return True
    
    def post_progress_comment(self, issue_number: int, report: ProgressReport):
        """Post progress update comment to GitHub"""
        comment_body = f"""## Progress Update - {report.timestamp.strftime('%Y-%m-%d %H:%M')}

**Agent**: {report.agent}
**Status**: {report.status}
**Progress**: {report.progress_percentage}%

### Current Blockers:
{chr(10).join(f'- {blocker}' for blocker in report.blockers) if report.blockers else '- None'}

### Next Steps:
{chr(10).join(f'- {step}' for step in report.next_steps) if report.next_steps else '- To be determined'}

**Author: Whisky, PR Worker - Automated Progress Tracking**
"""
        
        response = github_api_request(
            f'/repos/UltimatePea/wenyan-stdlib/issues/{issue_number}/comments',
            method='POST',
            data={'body': comment_body}
        )
    
    def generate_resource_allocation_report(self) -> Dict[str, Any]:
        """Generate comprehensive resource allocation report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'agents': {},
            'issues': {
                'assigned': 0,
                'unassigned': 0,
                'blocked': 0,
                'completed': 0
            },
            'resource_utilization': 0.0,
            'bottlenecks': [],
            'recommendations': []
        }
        
        total_capacity = 0
        used_capacity = 0
        
        # Analyze agents
        for name, agent in self.agents.items():
            total_capacity += agent.max_concurrent
            used_capacity += len(agent.current_issues)
            
            report['agents'][name] = {
                'current_workload': len(agent.current_issues),
                'max_capacity': agent.max_concurrent,
                'utilization': len(agent.current_issues) / agent.max_concurrent,
                'skills': agent.skills,
                'performance_score': agent.performance_score
            }
        
        # Analyze issues
        for issue in self.issues.values():
            if issue.assigned_agent:
                report['issues']['assigned'] += 1
            else:
                report['issues']['unassigned'] += 1
            
            if issue.state == 'closed':
                report['issues']['completed'] += 1
        
        report['resource_utilization'] = used_capacity / total_capacity if total_capacity > 0 else 0
        
        # Identify bottlenecks
        overloaded_agents = [name for name, agent in self.agents.items() 
                           if len(agent.current_issues) >= agent.max_concurrent]
        if overloaded_agents:
            report['bottlenecks'].append(f"Overloaded agents: {', '.join(overloaded_agents)}")
        
        # Generate recommendations
        if report['resource_utilization'] > 0.8:
            report['recommendations'].append("High resource utilization - consider expanding agent capacity")
        
        if report['issues']['unassigned'] > 0:
            report['recommendations'].append(f"{report['issues']['unassigned']} unassigned issues need attention")
        
        return report
    
    def sync_with_github(self):
        """Synchronize local coordination state with GitHub"""
        print("Syncing with GitHub...")
        
        # Fetch current issues
        github_issues = self.fetch_github_issues('all')  # Get both open and closed
        
        for issue_data in github_issues:
            issue_number = issue_data['number']
            required_skills, complexity = self.analyze_issue_requirements(issue_data)
            
            # Update or create issue entry
            if issue_number in self.issues:
                issue = self.issues[issue_number]
                issue.state = issue_data['state']
                issue.title = issue_data['title']
                issue.labels = [label['name'] for label in issue_data.get('labels', [])]
            else:
                issue = Issue(
                    number=issue_number,
                    title=issue_data['title'],
                    state=issue_data['state'],
                    labels=[label['name'] for label in issue_data.get('labels', [])],
                    required_skills=required_skills,
                    estimated_complexity=complexity
                )
                self.issues[issue_number] = issue
        
        # Update agent workloads based on GitHub assignees
        # Reset current issues and rebuild from GitHub state
        for agent in self.agents.values():
            agent.current_issues = []
        
        for issue_number, issue in self.issues.items():
            if issue.assigned_agent and issue.state == 'open':
                if issue.assigned_agent in self.agents:
                    self.agents[issue.assigned_agent].current_issues.append(issue_number)
        
        self.save_configuration()
        print(f"Synced {len(github_issues)} issues from GitHub")
    
    def auto_assign_unassigned_issues(self) -> List[int]:
        """Automatically assign unassigned open issues"""
        assigned_issues = []
        
        unassigned_issues = [
            issue for issue in self.issues.values() 
            if issue.state == 'open' and not issue.assigned_agent
        ]
        
        # Sort by complexity (lower first) to handle easier issues quickly
        unassigned_issues.sort(key=lambda x: x.estimated_complexity)
        
        for issue in unassigned_issues:
            if self.assign_issue(issue.number):
                assigned_issues.append(issue.number)
        
        return assigned_issues

def main():
    """Command-line interface for strategic coordination system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Strategic Development Coordinator')
    parser.add_argument('--sync', action='store_true', help='Sync with GitHub issues')
    parser.add_argument('--assign', type=int, help='Assign specific issue number')
    parser.add_argument('--auto-assign', action='store_true', help='Auto-assign all unassigned issues')
    parser.add_argument('--report', action='store_true', help='Generate resource allocation report')
    parser.add_argument('--progress', nargs=4, metavar=('ISSUE', 'STATUS', 'PERCENTAGE', 'NOTES'),
                       help='Update issue progress')
    
    args = parser.parse_args()
    
    coordinator = StrategicCoordinator()
    
    if args.sync:
        coordinator.sync_with_github()
    
    if args.assign:
        success = coordinator.assign_issue(args.assign)
        if success:
            print(f"Successfully assigned issue #{args.assign}")
        else:
            print(f"Failed to assign issue #{args.assign}")
    
    if args.auto_assign:
        assigned = coordinator.auto_assign_unassigned_issues()
        print(f"Auto-assigned {len(assigned)} issues: {assigned}")
    
    if args.report:
        report = coordinator.generate_resource_allocation_report()
        print(json.dumps(report, indent=2, default=str))
    
    if args.progress:
        issue_num, status, percentage, notes = args.progress
        coordinator.update_issue_progress(
            int(issue_num), status, int(percentage), 
            [notes] if notes != 'none' else []
        )

if __name__ == '__main__':
    main()