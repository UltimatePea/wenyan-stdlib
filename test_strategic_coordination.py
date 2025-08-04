#!/usr/bin/env python3
"""
Test Suite for Strategic Coordination System
Author: Whisky, PR Worker

Comprehensive tests for strategic coordination functionality including:
- Agent assignment automation
- Progress tracking
- Resource allocation
- GitHub workflow integration
"""

import unittest
import json
import tempfile
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from strategic_coordinator import StrategicCoordinator, Agent, Issue, ProgressReport
from coordination_workflow import CoordinationWorkflow

class TestStrategicCoordinator(unittest.TestCase):
    """Test cases for StrategicCoordinator class"""
    
    def setUp(self):
        """Set up test environment with temporary config file"""
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        # Write empty JSON to initialize the file properly
        self.temp_config.write('{"agents": [], "issues": []}')
        self.temp_config.close()
        
        self.coordinator = StrategicCoordinator(config_file=self.temp_config.name)
        
        # Add test agents
        self.coordinator.agents = {
            'TestStringAgent': Agent(
                name='TestStringAgent',
                skills=['string-processing', 'text-manipulation'],
                current_issues=[],
                max_concurrent=2,
                performance_score=1.0
            ),
            'TestMathAgent': Agent(
                name='TestMathAgent', 
                skills=['mathematical-operations', 'algorithms'],
                current_issues=[],
                max_concurrent=1,
                performance_score=0.9
            ),
            'TestGeneralAgent': Agent(
                name='TestGeneralAgent',
                skills=['general-programming', 'testing'],
                current_issues=[],
                max_concurrent=3,
                performance_score=0.8
            )
        }
        
        # Add test issues
        self.coordinator.issues = {
            101: Issue(
                number=101,
                title='Implement string manipulation functions',
                state='open',
                labels=['enhancement'],
                required_skills=['string-processing'],
                estimated_complexity=3
            ),
            102: Issue(
                number=102,
                title='Add mathematical operations to 算經',
                state='open', 
                labels=['feature'],
                required_skills=['mathematical-operations'],
                estimated_complexity=4
            ),
            103: Issue(
                number=103,
                title='Fix documentation typos',
                state='open',
                labels=['documentation'],
                required_skills=['documentation'],
                estimated_complexity=1
            )
        }
    
    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_agent_availability(self):
        """Test agent availability checking"""
        agent = self.coordinator.agents['TestStringAgent']
        self.assertTrue(agent.is_available())
        
        # Fill up agent capacity
        agent.current_issues = [101, 102]
        self.assertFalse(agent.is_available())
    
    def test_skill_matching(self):
        """Test agent skill matching scores"""
        agent = self.coordinator.agents['TestStringAgent']
        
        # Perfect match
        score = agent.skill_match_score(['string-processing'])
        self.assertEqual(score, 1.0)
        
        # Partial match
        score = agent.skill_match_score(['string-processing', 'mathematical-operations'])
        self.assertEqual(score, 0.5)
        
        # No match
        score = agent.skill_match_score(['file-operations'])
        self.assertEqual(score, 0.0)
    
    def test_issue_assignment(self):
        """Test issue assignment functionality"""
        # Test successful assignment
        success = self.coordinator.assign_issue(101, 'TestStringAgent')
        self.assertTrue(success)
        
        issue = self.coordinator.issues[101]
        agent = self.coordinator.agents['TestStringAgent']
        
        self.assertEqual(issue.assigned_agent, 'TestStringAgent')
        self.assertIn(101, agent.current_issues)
        
        # Test assignment to unavailable agent
        agent.current_issues = [101, 102]  # Fill capacity
        success = self.coordinator.assign_issue(102, 'TestStringAgent')
        self.assertFalse(success)
    
    def test_best_agent_selection(self):
        """Test automatic best agent selection"""
        # Issue requiring string processing skills
        best_agent = self.coordinator.find_best_agent(self.coordinator.issues[101])
        self.assertEqual(best_agent, 'TestStringAgent')
        
        # Issue requiring math skills
        best_agent = self.coordinator.find_best_agent(self.coordinator.issues[102])
        self.assertEqual(best_agent, 'TestMathAgent')
        
        # Issue without specific skill requirements
        issue_no_skills = Issue(
            number=104,
            title='General task',
            state='open',
            labels=[],
            required_skills=[],
            estimated_complexity=2
        )
        best_agent = self.coordinator.find_best_agent(issue_no_skills)
        # Should prefer agent with lowest current workload
        self.assertIsNotNone(best_agent)
    
    def test_progress_tracking(self):
        """Test progress update functionality"""
        # Assign issue first
        self.coordinator.assign_issue(101, 'TestStringAgent')
        
        # Update progress
        success = self.coordinator.update_issue_progress(
            101, 'in_progress', 50, 
            blockers=['Need API documentation'],
            next_steps=['Implement core functions', 'Add tests']
        )
        self.assertTrue(success)
        
        # Check progress report was created
        reports = [r for r in self.coordinator.progress_reports if r.issue_number == 101]
        self.assertEqual(len(reports), 2)  # Assignment + progress update
        
        latest_report = reports[-1]
        self.assertEqual(latest_report.status, 'in_progress')
        self.assertEqual(latest_report.progress_percentage, 50)
        self.assertEqual(latest_report.blockers, ['Need API documentation'])
    
    def test_resource_allocation_report(self):
        """Test resource allocation report generation"""
        # Assign some issues
        self.coordinator.assign_issue(101, 'TestStringAgent')
        self.coordinator.assign_issue(102, 'TestMathAgent')
        
        report = self.coordinator.generate_resource_allocation_report()
        
        # Check report structure
        self.assertIn('timestamp', report)
        self.assertIn('agents', report)
        self.assertIn('issues', report)
        self.assertIn('resource_utilization', report)
        
        # Check agent utilization
        self.assertEqual(report['agents']['TestStringAgent']['current_workload'], 1)
        self.assertEqual(report['agents']['TestMathAgent']['current_workload'], 1)
        self.assertEqual(report['agents']['TestGeneralAgent']['current_workload'], 0)
        
        # Check issue counts
        self.assertEqual(report['issues']['assigned'], 2)
        self.assertEqual(report['issues']['unassigned'], 1)
    
    def test_configuration_persistence(self):
        """Test saving and loading configuration"""
        # Assign an issue and save
        self.coordinator.assign_issue(101, 'TestStringAgent') 
        self.coordinator.save_configuration()
        
        # Create new coordinator instance
        new_coordinator = StrategicCoordinator(config_file=self.temp_config.name)
        
        # Check that data was loaded correctly
        self.assertIn('TestStringAgent', new_coordinator.agents)
        self.assertEqual(len(new_coordinator.agents), 3)
        self.assertEqual(len(new_coordinator.issues), 3)
        
        # Check assignment was preserved  
        agent = new_coordinator.agents['TestStringAgent']
        issue = new_coordinator.issues[101]
        self.assertEqual(issue.assigned_agent, 'TestStringAgent')
        self.assertIn(101, agent.current_issues)
    
    @patch('strategic_coordinator.github_api_request')
    def test_github_sync(self, mock_api):
        """Test synchronization with GitHub issues"""
        # Mock GitHub API response
        mock_api.return_value.status_code = 200
        mock_api.return_value.json.return_value = [
            {
                'number': 104,
                'title': 'New GitHub issue',
                'state': 'open',
                'labels': [{'name': 'bug'}],
                'body': 'String processing bug in 字符串經'
            }
        ]
        
        self.coordinator.sync_with_github()
        
        # Check that new issue was added
        self.assertIn(104, self.coordinator.issues)
        new_issue = self.coordinator.issues[104]
        self.assertEqual(new_issue.title, 'New GitHub issue')
        self.assertIn('string-processing', new_issue.required_skills)

class TestCoordinationWorkflow(unittest.TestCase):
    """Test cases for CoordinationWorkflow class"""
    
    def setUp(self):
        """Set up test workflow environment"""
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_config.write('{"agents": [], "issues": []}')
        self.temp_config.close()
        
        self.workflow = CoordinationWorkflow()
        self.workflow.coordinator = StrategicCoordinator(config_file=self.temp_config.name)
        
        # Add test data similar to coordinator tests
        self.workflow.coordinator.agents = {
            'TestAgent': Agent(
                name='TestAgent',
                skills=['string-processing'],
                current_issues=[101],
                max_concurrent=2,
                performance_score=1.0
            )
        }
        
        self.workflow.coordinator.issues = {
            101: Issue(
                number=101,
                title='Test issue',
                state='open',
                labels=[],
                assigned_agent='TestAgent',
                estimated_complexity=3
            )
        }
    
    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_workflow_logging(self):
        """Test workflow action logging"""
        self.workflow.log_action('test_action', 'Test details', True)
        
        self.assertEqual(len(self.workflow.workflow_log), 1)
        log_entry = self.workflow.workflow_log[0]
        
        self.assertEqual(log_entry['action'], 'test_action')
        self.assertEqual(log_entry['details'], 'Test details')
        self.assertTrue(log_entry['success'])
        self.assertIn('timestamp', log_entry)
    
    @patch('coordination_workflow.github_api_request')
    def test_stale_detection(self, mock_api):
        """Test detection of stale issue assignments"""
        # Mock GitHub API to return stale issue
        old_date = (datetime.now() - timedelta(days=5)).isoformat() + 'Z'
        mock_api.return_value.status_code = 200
        mock_api.return_value.json.return_value = {
            'updated_at': old_date
        }
        
        stale_issues = self.workflow.check_stale_assignments(days_threshold=3)
        
        self.assertEqual(len(stale_issues), 1)
        self.assertEqual(stale_issues[0], 101)
    
    def test_issue_number_extraction(self):
        """Test extraction of issue numbers from text"""
        text = "This PR fixes #123 and closes #456. Also resolves #789"
        issue_numbers = self.workflow.extract_issue_numbers_from_text(text)
        
        self.assertEqual(sorted(issue_numbers), [123, 456, 789])
    
    @patch('coordination_workflow.github_api_request')
    def test_pr_monitoring(self, mock_api):
        """Test pull request status monitoring"""
        # Mock PR API response
        mock_api.return_value.status_code = 200
        mock_api.return_value.json.return_value = [
            {
                'number': 30,
                'title': 'Fix #101: String operations',
                'body': 'Implements string functions',
                'mergeable_state': 'clean'
            },
            {
                'number': 31,
                'title': 'Fix #102: Math library',
                'body': 'Adds math operations',
                'mergeable_state': 'dirty'
            }
        ]
        
        pr_status = self.workflow.monitor_pr_status()
        
        self.assertIn('merge_conflicts', pr_status)
        self.assertIn('ready_for_review', pr_status)
        self.assertEqual(len(pr_status['merge_conflicts']), 1)
        self.assertEqual(pr_status['merge_conflicts'][0], 31)
    
    def test_daily_report_generation(self):
        """Test daily status report generation"""
        report = self.workflow.generate_daily_status_report()
        
        # Check report structure
        required_keys = ['date', 'resource_allocation', 'stale_assignments', 
                        'pr_status', 'workflow_actions', 'recommendations']
        for key in required_keys:
            self.assertIn(key, report)
        
        # Check date format
        self.assertEqual(report['date'], datetime.now().strftime('%Y-%m-%d'))

class TestIntegration(unittest.TestCase):
    """Integration tests for complete coordination system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_config.write('{"agents": [], "issues": []}')
        self.temp_config.close()
        
        self.coordinator = StrategicCoordinator(config_file=self.temp_config.name)
        self.workflow = CoordinationWorkflow()
        self.workflow.coordinator = self.coordinator
    
    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    @patch('strategic_coordinator.github_api_request')
    def test_complete_assignment_workflow(self, mock_api):
        """Test complete issue assignment workflow"""
        # Mock successful GitHub API calls
        mock_api.return_value.status_code = 201
        mock_api.return_value.json.return_value = {'id': 12345}
        
        # Create test issue
        issue = Issue(
            number=105,
            title='Test integration issue',
            state='open',
            labels=['enhancement'],
            required_skills=['string-processing'],
            estimated_complexity=3
        )
        self.coordinator.issues[105] = issue
        
        # Assign issue
        success = self.coordinator.assign_issue(105)
        self.assertTrue(success)
        
        # Update progress
        success = self.coordinator.update_issue_progress(
            105, 'in_progress', 75, 
            next_steps=['Final testing', 'Submit PR']
        )
        self.assertTrue(success)
        
        # Generate report
        report = self.coordinator.generate_resource_allocation_report()
        self.assertGreater(report['issues']['assigned'], 0)
        
        # Check that GitHub API was called for assignment comment
        self.assertTrue(mock_api.called)

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        """Set up error handling test environment"""
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_config.write('{"agents": [], "issues": []}')
        self.temp_config.close()
        self.coordinator = StrategicCoordinator(config_file=self.temp_config.name)
    
    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_nonexistent_issue_assignment(self):
        """Test assignment of non-existent issue"""
        success = self.coordinator.assign_issue(999)
        self.assertFalse(success)
    
    def test_nonexistent_agent_assignment(self):
        """Test assignment to non-existent agent"""
        issue = Issue(
            number=106,
            title='Test issue',
            state='open',
            labels=[],
            estimated_complexity=3
        )
        self.coordinator.issues[106] = issue
        
        success = self.coordinator.assign_issue(106, 'NonexistentAgent')
        self.assertFalse(success)
    
    def test_progress_update_unassigned_issue(self):
        """Test progress update for unassigned issue"""
        issue = Issue(
            number=107,
            title='Unassigned issue',
            state='open',
            labels=[],
            estimated_complexity=2
        )
        self.coordinator.issues[107] = issue
        
        success = self.coordinator.update_issue_progress(107, 'in_progress', 50)
        self.assertFalse(success)
    
    def test_closed_issue_assignment_critical_fix(self):
        """CRITICAL TEST: Test assignment of closed issue is prevented"""
        # Add a closed issue
        closed_issue = Issue(
            number=108,
            title='Closed issue test',
            state='closed',
            labels=[],
            estimated_complexity=2
        )
        self.coordinator.issues[108] = closed_issue
        
        # Add test agent
        self.coordinator.agents['TestAgent'] = Agent(
            name='TestAgent',
            skills=['general-programming'],
            current_issues=[],
            max_concurrent=2,
            performance_score=1.0
        )
        
        # Attempt assignment should fail
        success = self.coordinator.assign_issue(108, 'TestAgent')
        self.assertFalse(success)
        
        # Verify agent was not assigned
        self.assertIsNone(closed_issue.assigned_agent)
        self.assertEqual(len(self.coordinator.agents['TestAgent'].current_issues), 0)
    
    @patch('strategic_coordinator.github_api_request')
    def test_github_state_synchronization_critical_fix(self, mock_api):
        """CRITICAL TEST: Test real-time GitHub state synchronization"""
        # Add an issue that appears open locally but is closed on GitHub
        issue = Issue(
            number=109,
            title='State sync test issue',
            state='open',
            labels=[],
            estimated_complexity=2
        )
        self.coordinator.issues[109] = issue
        
        # Add test agent
        self.coordinator.agents['TestAgent'] = Agent(
            name='TestAgent',
            skills=['general-programming'],
            current_issues=[],
            max_concurrent=2,
            performance_score=1.0
        )
        
        # Mock GitHub API to return closed state
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'number': 109,
            'title': 'State sync test issue',
            'state': 'closed',
            'labels': []
        }
        mock_api.return_value = mock_response
        
        # Assignment should fail and local state should be updated
        success = self.coordinator.assign_issue(109, 'TestAgent')
        self.assertFalse(success)
        
        # Verify local state was updated to match GitHub
        self.assertEqual(issue.state, 'closed')
        self.assertIsNone(issue.assigned_agent)
    
    def test_coordination_issue_self_assignment_protection_critical_fix(self):
        """CRITICAL TEST: Test protection against coordination issue self-assignment"""
        # Add coordination-related issues
        coordination_issues = [
            Issue(
                number=110,
                title='Strategic Development Coordination Enhancement',
                state='open',
                labels=[],
                estimated_complexity=4
            ),
            Issue(
                number=111,
                title='Workflow Assignment Optimization',
                state='open',
                labels=[],
                estimated_complexity=3
            ),
            Issue(
                number=112,
                title='Resource Allocation System Update',
                state='open',
                labels=[],
                estimated_complexity=3
            )
        ]
        
        for issue in coordination_issues:
            self.coordinator.issues[issue.number] = issue
        
        # Add test agent
        self.coordinator.agents['TestAgent'] = Agent(
            name='TestAgent',
            skills=['general-programming'],
            current_issues=[],
            max_concurrent=5,
            performance_score=1.0
        )
        
        # All coordination issue assignments should fail
        for issue in coordination_issues:
            success = self.coordinator.assign_issue(issue.number, 'TestAgent')
            self.assertFalse(success, f"Coordination issue #{issue.number} should not be assignable")
            self.assertIsNone(issue.assigned_agent)
        
        # Verify agent has no assignments
        self.assertEqual(len(self.coordinator.agents['TestAgent'].current_issues), 0)
    
    def test_edge_case_empty_coordination_keywords(self):
        """Test edge case with empty or minimal issue titles"""
        # Issue with minimal title
        minimal_issue = Issue(
            number=113,
            title='A',
            state='open',
            labels=[],
            estimated_complexity=1
        )
        self.coordinator.issues[113] = minimal_issue
        
        # Add test agent
        self.coordinator.agents['TestAgent'] = Agent(
            name='TestAgent',
            skills=['general-programming'],
            current_issues=[],
            max_concurrent=2,
            performance_score=1.0
        )
        
        # Should succeed (not a coordination issue)
        success = self.coordinator.assign_issue(113, 'TestAgent')
        self.assertTrue(success)
        self.assertEqual(minimal_issue.assigned_agent, 'TestAgent')
    
    @patch('strategic_coordinator.github_api_request')
    def test_github_api_error_handling(self, mock_api):
        """Test handling of GitHub API errors"""
        # Mock API error
        mock_api.return_value.status_code = 403
        mock_api.return_value.text = 'API rate limit exceeded'
        
        github_issues = self.coordinator.fetch_github_issues()
        self.assertEqual(len(github_issues), 0)  # Should return empty list on error
    
    @patch('strategic_coordinator.github_api_request')
    def test_github_issue_details_error_handling(self, mock_api):
        """Test handling of GitHub issue details API errors"""
        # Mock API error for specific issue
        mock_api.return_value.status_code = 404
        mock_api.return_value.text = 'Not Found'
        
        issue_details = self.coordinator.fetch_github_issue_details(999)
        self.assertIsNone(issue_details)

def run_coordination_system_tests():
    """Run comprehensive test suite for strategic coordination system"""
    print("Running Strategic Coordination System Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestStrategicCoordinator,
        TestCoordinationWorkflow, 
        TestIntegration,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Generate test report
    test_report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
        'details': {
            'failures': [{'test': str(test), 'message': message} for test, message in result.failures],
            'errors': [{'test': str(test), 'message': message} for test, message in result.errors]
        }
    }
    
    # Save detailed test report
    report_file = f"coordination_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(test_report, f, indent=2, default=str)
    
    print(f"\nTest Report Summary:")
    print(f"Total Tests: {test_report['total_tests']}")
    print(f"Failures: {test_report['failures']}")
    print(f"Errors: {test_report['errors']}")
    print(f"Success Rate: {test_report['success_rate']:.1f}%")
    print(f"Detailed report saved to: {report_file}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_coordination_system_tests()
    sys.exit(0 if success else 1)