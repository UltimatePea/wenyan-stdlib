#!/usr/bin/env python3
"""
Branch Management and Merge Conflict Prevention System
Author: Whisky, PR Worker

This system provides automated branch management tools to prevent merge conflicts
and coordinate multi-agent development as specified in Issue #26.

Features:
- Automated branch synchronization
- Merge conflict detection and prevention
- Branch cleanup and maintenance
- Multi-agent coordination through branch analysis

Usage:
    python branch_manager.py sync --branch feature/string-advanced
    python branch_manager.py check-conflicts --source feature/math-core --target main
    python branch_manager.py cleanup --dry-run
    python branch_manager.py coordinate --all-branches
"""

import subprocess
import sys
import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class BranchManager:
    """Automated branch management and conflict prevention system."""
    
    def __init__(self):
        self.repo_root = Path.cwd()
        self.remote_name = "origin"
        self.main_branch = "main"
        
    def sync_branch(self, branch_name: str, force: bool = False) -> Dict:
        """Synchronize a branch with the latest main branch changes."""
        sync_result = {
            "branch": branch_name,
            "timestamp": datetime.now().isoformat(),
            "actions_taken": [],
            "conflicts_detected": [],
            "success": False
        }
        
        try:
            # Save current branch
            current_branch = self._get_current_branch()
            sync_result["original_branch"] = current_branch
            
            # Fetch latest changes
            self._run_git_command(["git", "fetch", self.remote_name])
            sync_result["actions_taken"].append("Fetched latest changes from remote")
            
            # Check if branch exists
            if not self._branch_exists(branch_name):
                sync_result["actions_taken"].append(f"Branch {branch_name} does not exist")
                return sync_result
            
            # Switch to target branch
            self._run_git_command(["git", "checkout", branch_name])
            sync_result["actions_taken"].append(f"Switched to branch {branch_name}")
            
            # Check for uncommitted changes
            if self._has_uncommitted_changes():
                if force:
                    self._run_git_command(["git", "stash", "push", "-m", f"Auto-stash before sync {datetime.now()}"])
                    sync_result["actions_taken"].append("Stashed uncommitted changes")
                else:
                    sync_result["actions_taken"].append("Uncommitted changes detected - use --force to stash")
                    return sync_result
            
            # Merge main branch
            merge_result = self._run_git_command(["git", "merge", f"{self.remote_name}/{self.main_branch}"], 
                                               capture_output=True)
            
            if merge_result.returncode == 0:
                sync_result["actions_taken"].append("Successfully merged main branch changes")
                sync_result["success"] = True
            else:
                # Check for merge conflicts
                conflicts = self._detect_merge_conflicts()
                sync_result["conflicts_detected"] = conflicts
                sync_result["actions_taken"].append("Merge conflicts detected")
                
                # Abort merge to clean state
                self._run_git_command(["git", "merge", "--abort"])
                sync_result["actions_taken"].append("Aborted merge due to conflicts")
            
            # Return to original branch
            if current_branch != branch_name:
                self._run_git_command(["git", "checkout", current_branch])
                sync_result["actions_taken"].append(f"Returned to original branch {current_branch}")
                
        except Exception as e:
            sync_result["actions_taken"].append(f"Error during sync: {str(e)}")
            
        return sync_result
    
    def check_conflicts(self, source_branch: str, target_branch: str = None) -> Dict:
        """Check for potential merge conflicts between branches."""
        if target_branch is None:
            target_branch = self.main_branch
            
        conflict_analysis = {
            "source_branch": source_branch,
            "target_branch": target_branch,
            "timestamp": datetime.now().isoformat(),
            "potential_conflicts": [],
            "file_changes": {},
            "recommendations": []
        }
        
        try:
            # Get diff between branches
            diff_result = self._run_git_command([
                "git", "diff", "--name-status", 
                f"{target_branch}...{source_branch}"
            ], capture_output=True)
            
            if diff_result.returncode == 0:
                changes = diff_result.stdout.decode().strip().split('\n')
                for change in changes:
                    if change:
                        status, filename = change.split('\t', 1)
                        conflict_analysis["file_changes"][filename] = status
            
            # Check for overlapping file modifications
            target_changes = self._get_recent_changes(target_branch)
            source_changes = list(conflict_analysis["file_changes"].keys())
            
            overlapping_files = set(target_changes) & set(source_changes)
            
            for file_path in overlapping_files:
                conflict_info = self._analyze_file_conflict_potential(file_path, source_branch, target_branch)
                if conflict_info["conflict_probability"] > 0.5:
                    conflict_analysis["potential_conflicts"].append(conflict_info)
            
            # Generate recommendations
            if conflict_analysis["potential_conflicts"]:
                conflict_analysis["recommendations"] = [
                    "Coordinate with other agents working on overlapping files",
                    "Consider rebasing instead of merging",
                    "Sync branch frequently to minimize conflicts",
                    "Break down changes into smaller, focused commits"
                ]
            else:
                conflict_analysis["recommendations"] = [
                    "No conflicts detected - safe to merge",
                    "Continue with current development approach"
                ]
                    
        except Exception as e:
            conflict_analysis["error"] = str(e)
            
        return conflict_analysis
    
    def cleanup_branches(self, dry_run: bool = True) -> Dict:
        """Clean up old and merged branches."""
        cleanup_result = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "branches_analyzed": [],
            "branches_to_delete": [],
            "actions_taken": []
        }
        
        try:
            # Get all local branches
            branches_result = self._run_git_command([
                "git", "branch", "--list", "--format=%(refname:short) %(committerdate:iso8601)"
            ], capture_output=True)
            
            if branches_result.returncode == 0:
                branches = branches_result.stdout.decode().strip().split('\n')
                
                for branch_line in branches:
                    if not branch_line.strip():
                        continue
                        
                    parts = branch_line.strip().split(' ', 1)
                    branch_name = parts[0]
                    
                    if branch_name in [self.main_branch, self._get_current_branch()]:
                        continue  # Skip main and current branch
                    
                    branch_info = self._analyze_branch_status(branch_name)
                    cleanup_result["branches_analyzed"].append(branch_info)
                    
                    # Determine if branch should be deleted
                    should_delete = (
                        branch_info["is_merged"] or
                        branch_info["days_since_activity"] > 30 or
                        branch_info["is_abandoned"]
                    )
                    
                    if should_delete:
                        cleanup_result["branches_to_delete"].append(branch_name)
                        
                        if not dry_run:
                            try:
                                self._run_git_command(["git", "branch", "-D", branch_name])
                                cleanup_result["actions_taken"].append(f"Deleted branch {branch_name}")
                            except Exception as e:
                                cleanup_result["actions_taken"].append(f"Failed to delete {branch_name}: {e}")
                        else:
                            cleanup_result["actions_taken"].append(f"Would delete branch {branch_name}")
                            
        except Exception as e:
            cleanup_result["error"] = str(e)
            
        return cleanup_result
    
    def coordinate_branches(self) -> Dict:
        """Analyze all feature branches for coordination opportunities."""
        coordination_analysis = {
            "timestamp": datetime.now().isoformat(),
            "active_branches": [],
            "coordination_opportunities": [],
            "potential_conflicts": [],
            "recommendations": []
        }
        
        try:
            # Get all feature branches
            branches_result = self._run_git_command([
                "git", "branch", "-r", "--list", "origin/feature/*"
            ], capture_output=True)
            
            if branches_result.returncode == 0:
                remote_branches = [
                    b.strip().replace('origin/', '') 
                    for b in branches_result.stdout.decode().strip().split('\n')
                    if b.strip()
                ]
                
                # Analyze each feature branch
                for branch in remote_branches:
                    branch_analysis = self._analyze_branch_coordination(branch)
                    coordination_analysis["active_branches"].append(branch_analysis)
                
                # Find coordination opportunities
                coordination_analysis["coordination_opportunities"] = self._find_coordination_opportunities(
                    coordination_analysis["active_branches"]
                )
                
                # Find potential conflicts
                coordination_analysis["potential_conflicts"] = self._find_branch_conflicts(
                    coordination_analysis["active_branches"]
                )
                
                # Generate recommendations
                coordination_analysis["recommendations"] = self._generate_coordination_recommendations(
                    coordination_analysis
                )
                
        except Exception as e:
            coordination_analysis["error"] = str(e)
            
        return coordination_analysis
    
    def _run_git_command(self, command: List[str], capture_output: bool = False, **kwargs):
        """Run a git command with error handling."""
        try:
            if capture_output:
                return subprocess.run(command, capture_output=True, text=True, **kwargs)
            else:
                return subprocess.run(command, check=True, **kwargs)
        except subprocess.CalledProcessError as e:
            if capture_output:
                return e
            else:
                raise
    
    def _get_current_branch(self) -> str:
        """Get the current branch name."""
        result = self._run_git_command(["git", "branch", "--show-current"], capture_output=True)
        return result.stdout.decode().strip() if result.returncode == 0 else "unknown"
    
    def _branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists."""
        result = self._run_git_command(["git", "show-ref", "--verify", f"refs/heads/{branch_name}"], 
                                     capture_output=True)
        return result.returncode == 0
    
    def _has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        result = self._run_git_command(["git", "status", "--porcelain"], capture_output=True)
        return bool(result.stdout.decode().strip()) if result.returncode == 0 else False
    
    def _detect_merge_conflicts(self) -> List[str]:
        """Detect files with merge conflicts."""
        result = self._run_git_command(["git", "diff", "--name-only", "--diff-filter=U"], 
                                     capture_output=True)
        if result.returncode == 0:
            return [f.strip() for f in result.stdout.decode().split('\n') if f.strip()]
        return []
    
    def _get_recent_changes(self, branch: str, days: int = 7) -> List[str]:
        """Get list of files changed in the last N days on a branch."""
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        result = self._run_git_command([
            "git", "log", f"--since={since_date}", "--name-only", "--pretty=format:", branch
        ], capture_output=True)
        
        if result.returncode == 0:
            files = [f.strip() for f in result.stdout.decode().split('\n') if f.strip()]
            return list(set(files))  # Remove duplicates
        return []
    
    def _analyze_file_conflict_potential(self, file_path: str, branch1: str, branch2: str) -> Dict:
        """Analyze the potential for conflicts in a specific file."""
        conflict_info = {
            "file": file_path,
            "conflict_probability": 0.0,
            "reasons": []
        }
        
        try:
            # Get diff stats for the file
            diff_result = self._run_git_command([
                "git", "diff", "--stat", f"{branch2}...{branch1}", "--", file_path
            ], capture_output=True)
            
            if diff_result.returncode == 0 and diff_result.stdout.decode().strip():
                # Simple heuristic: more changes = higher conflict probability
                diff_output = diff_result.stdout.decode()
                if "insertions" in diff_output and "deletions" in diff_output:
                    conflict_info["conflict_probability"] = 0.7
                    conflict_info["reasons"].append("File has both insertions and deletions")
                elif "insertions" in diff_output or "deletions" in diff_output:
                    conflict_info["conflict_probability"] = 0.3
                    conflict_info["reasons"].append("File has been modified")
                    
        except Exception as e:
            conflict_info["reasons"].append(f"Error analyzing file: {e}")
            
        return conflict_info
    
    def _analyze_branch_status(self, branch_name: str) -> Dict:
        """Analyze the status of a branch for cleanup decisions."""
        branch_info = {
            "name": branch_name,
            "is_merged": False,
            "days_since_activity": 0,
            "is_abandoned": False,
            "commit_count": 0
        }
        
        try:
            # Check if merged
            merged_result = self._run_git_command([
                "git", "branch", "--merged", self.main_branch
            ], capture_output=True)
            
            if merged_result.returncode == 0:
                merged_branches = merged_result.stdout.decode()
                branch_info["is_merged"] = branch_name in merged_branches
            
            # Get last commit date
            date_result = self._run_git_command([
                "git", "log", "-1", "--format=%ci", branch_name
            ], capture_output=True)
            
            if date_result.returncode == 0:
                last_commit_str = date_result.stdout.decode().strip()
                if last_commit_str:
                    last_commit = datetime.fromisoformat(last_commit_str.replace(' +', '+'))
                    branch_info["days_since_activity"] = (datetime.now().astimezone() - last_commit).days
            
            # Get commit count
            count_result = self._run_git_command([
                "git", "rev-list", "--count", branch_name
            ], capture_output=True)
            
            if count_result.returncode == 0:
                branch_info["commit_count"] = int(count_result.stdout.decode().strip())
            
            # Determine if abandoned (no activity for 30+ days and few commits)
            branch_info["is_abandoned"] = (
                branch_info["days_since_activity"] > 30 and 
                branch_info["commit_count"] < 5
            )
                
        except Exception as e:
            branch_info["error"] = str(e)
            
        return branch_info
    
    def _analyze_branch_coordination(self, branch_name: str) -> Dict:
        """Analyze a branch for coordination opportunities."""
        analysis = {
            "branch": branch_name,
            "files_modified": [],
            "libraries_affected": [],
            "last_activity": None,
            "coordination_score": 0
        }
        
        try:
            # Get modified files
            files_result = self._run_git_command([
                "git", "diff", "--name-only", f"{self.main_branch}...{branch_name}"
            ], capture_output=True)
            
            if files_result.returncode == 0:
                files = [f.strip() for f in files_result.stdout.decode().split('\n') if f.strip()]
                analysis["files_modified"] = files
                
                # Extract libraries affected
                for file_path in files:
                    if file_path.startswith('libs/'):
                        lib_name = file_path.split('/')[1]
                        if lib_name not in analysis["libraries_affected"]:
                            analysis["libraries_affected"].append(lib_name)
            
            # Get last activity
            activity_result = self._run_git_command([
                "git", "log", "-1", "--format=%ci", branch_name
            ], capture_output=True)
            
            if activity_result.returncode == 0:
                analysis["last_activity"] = activity_result.stdout.decode().strip()
                
        except Exception as e:
            analysis["error"] = str(e)
            
        return analysis
    
    def _find_coordination_opportunities(self, branches: List[Dict]) -> List[Dict]:
        """Find opportunities for coordination between branches."""
        opportunities = []
        
        for i, branch1 in enumerate(branches):
            for branch2 in branches[i+1:]:
                # Check for overlapping libraries
                common_libs = set(branch1["libraries_affected"]) & set(branch2["libraries_affected"])
                
                if common_libs:
                    opportunities.append({
                        "branches": [branch1["branch"], branch2["branch"]],
                        "common_libraries": list(common_libs),
                        "recommendation": "Coordinate API changes and testing"
                    })
        
        return opportunities
    
    def _find_branch_conflicts(self, branches: List[Dict]) -> List[Dict]:
        """Find potential conflicts between branches."""
        conflicts = []
        
        for i, branch1 in enumerate(branches):
            for branch2 in branches[i+1:]:
                # Check for overlapping files
                common_files = set(branch1["files_modified"]) & set(branch2["files_modified"])
                
                if common_files:
                    conflicts.append({
                        "branches": [branch1["branch"], branch2["branch"]],
                        "conflicting_files": list(common_files),
                        "severity": "HIGH" if len(common_files) > 3 else "MEDIUM"
                    })
        
        return conflicts
    
    def _generate_coordination_recommendations(self, analysis: Dict) -> List[str]:
        """Generate coordination recommendations based on analysis."""
        recommendations = []
        
        if analysis["coordination_opportunities"]:
            recommendations.append(
                "Coordinate with other agents working on the same libraries"
            )
            
        if analysis["potential_conflicts"]:
            recommendations.append(
                "High conflict risk detected - consider staggered development schedule"
            )
            
        recommendations.extend([
            "Sync branches with main daily to minimize conflicts",
            "Use small, focused commits for easier conflict resolution",
            "Communicate changes through GitHub issue comments"
        ])
        
        return recommendations

def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(description="Branch Management and Coordination System")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync branch with main')
    sync_parser.add_argument('--branch', required=True, help='Branch to sync')
    sync_parser.add_argument('--force', action='store_true', help='Force sync (stash changes)')
    
    # Check conflicts command
    conflict_parser = subparsers.add_parser('check-conflicts', help='Check for merge conflicts')
    conflict_parser.add_argument('--source', required=True, help='Source branch')
    conflict_parser.add_argument('--target', help='Target branch (default: main)')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old branches')
    cleanup_parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted')
    
    # Coordinate command
    subparsers.add_parser('coordinate', help='Analyze branch coordination')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = BranchManager()
    
    if args.command == 'sync':
        result = manager.sync_branch(args.branch, args.force)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif args.command == 'check-conflicts':
        result = manager.check_conflicts(args.source, args.target)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif args.command == 'cleanup':
        result = manager.cleanup_branches(args.dry_run)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif args.command == 'coordinate':
        result = manager.coordinate_branches()
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()