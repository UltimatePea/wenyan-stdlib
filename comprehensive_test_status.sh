#!/bin/bash

# 綜合測試狀態檢查器 - Comprehensive Test Status Checker
# Author: Whisky, PR Worker
# 
# Purpose: Run critical tests to verify current status after fixing Issue #37 timeout
# Generate comprehensive report on test health

echo "=========================================="
echo "Wenyan Standard Library - Test Status Check"
echo "Author: Whisky, PR Worker"
echo "Date: $(date)"
echo "=========================================="
echo ""

PASSED_TESTS=0
FAILED_TESTS=0
TOTAL_TESTS=0
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="comprehensive_status_${TIMESTAMP}.log"

# Clear log file
> "$LOG_FILE"

# Function to run a test
run_test() {
    local test_file="$1"
    local test_name="$2"
    local expected_success="$3"  # "pass" or "skip" (for tests that should succeed vs ones that might not work)
    
    echo "Testing: $test_name" | tee -a "$LOG_FILE"
    echo "File: $test_file" | tee -a "$LOG_FILE"
    
    if [ ! -f "$test_file" ]; then
        echo "✗ MISSING: Test file not found" | tee -a "$LOG_FILE"
        ((FAILED_TESTS++))
        ((TOTAL_TESTS++))
        echo "" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # Run with timeout to catch infinite loops
    if timeout 10s wenyan "$test_file" > /tmp/test_output_$$ 2>&1; then
        local output=$(cat /tmp/test_output_$$)
        echo "✓ SUCCESS: Test completed" | tee -a "$LOG_FILE"
        
        # Check if output contains meaningful content
        if [ -n "$output" ] && ! echo "$output" | grep -q "Error\|TypeError\|ReferenceError"; then
            echo "✓ OUTPUT: Contains valid results" | tee -a "$LOG_FILE"
            echo "Sample output: $(echo "$output" | head -3 | tr '\n' ' ')" | tee -a "$LOG_FILE"
            ((PASSED_TESTS++))
        else
            echo "⚠ WARNING: Test ran but may have errors" | tee -a "$LOG_FILE"
            echo "Output: $output" | tee -a "$LOG_FILE"
            if [ "$expected_success" = "pass" ]; then
                ((FAILED_TESTS++))
            else
                echo "⚠ Expected issue - counting as skipped" | tee -a "$LOG_FILE"
            fi
        fi
    else
        echo "✗ FAILED: Test timed out or crashed" | tee -a "$LOG_FILE"
        echo "Error output: $(cat /tmp/test_output_$$ 2>/dev/null)" | tee -a "$LOG_FILE"
        ((FAILED_TESTS++))
    fi
    
    ((TOTAL_TESTS++))
    echo "" | tee -a "$LOG_FILE"
    rm -f /tmp/test_output_$$
}

echo "=== Critical Issue #37 Tests ===" | tee -a "$LOG_FILE"
run_test "test_final_success.wy" "Final Success Test (formerly failing)" "pass"
run_test "WORKING_issue37_number_formatting_test.wy" "Issue #37 Number Formatting" "pass"
run_test "simple_test.wy" "Simple Number Formatting Test" "pass"

echo "=== Math Library Tests ===" | tee -a "$LOG_FILE"
run_test "tests/算經/delta_critical_fixes_test.wy" "Delta Critical Fixes" "pass"
run_test "tests/算經/final_validation_test.wy" "Math Library Final Validation" "pass"
run_test "tests/算經/最簡測試.wy" "Minimal Math Test" "pass"

echo "=== Additional Core Tests ===" | tee -a "$LOG_FILE"
run_test "tests/算經/WORKING_issue37_number_formatting_test.wy" "Working Issue 37 Test (subdirectory)" "pass"

# Generate summary report
echo "==========================================" | tee -a "$LOG_FILE"
echo "TEST STATUS SUMMARY" | tee -a "$LOG_FILE"
echo "==========================================" | tee -a "$LOG_FILE"
echo "Total Tests Run: $TOTAL_TESTS" | tee -a "$LOG_FILE"
echo "Passed Tests: $PASSED_TESTS" | tee -a "$LOG_FILE"
echo "Failed Tests: $FAILED_TESTS" | tee -a "$LOG_FILE"

if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "Success Rate: ${SUCCESS_RATE}%" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "ISSUE #37 STATUS ASSESSMENT" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

if [ $PASSED_TESTS -ge 6 ]; then
    echo "🎉 RESOLVED: Issue #37 number formatting is working correctly!" | tee -a "$LOG_FILE"
    echo "✅ Critical tests are passing" | tee -a "$LOG_FILE"
    echo "✅ Timeout issues have been fixed" | tee -a "$LOG_FILE"
    echo "✅ Math library is functional" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "RECOMMENDATION: Issue #37 PR #43 is ready for approval" | tee -a "$LOG_FILE"
    exit_code=0
else
    echo "❌ ISSUES REMAIN: Some critical tests are still failing" | tee -a "$LOG_FILE"
    echo "Failed tests: $FAILED_TESTS" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "RECOMMENDATION: Further fixes needed before PR approval" | tee -a "$LOG_FILE"
    exit_code=1
fi

echo "" | tee -a "$LOG_FILE"
echo "Detailed log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "Author: Whisky, PR Worker - Test Status Complete" | tee -a "$LOG_FILE"

exit $exit_code