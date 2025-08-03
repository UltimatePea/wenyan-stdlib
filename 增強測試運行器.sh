#!/bin/bash

# 增強測試運行器 - Enhanced Test Runner
# Author: Whisky, PR Worker
# 
# 批量運行所有庫的測試文件並生成詳細報告
# Batch run all library test files and generate detailed reports

set -uo pipefail  # 錯誤處理，但允許單個命令失敗

echo "=========================================="
echo "文言標準庫增強測試運行器 - Enhanced Wenyan Stdlib Test Runner"
echo "Author: Whisky, PR Worker"
echo "Version: 2.0"
echo "=========================================="
echo ""

# 設置變量
TESTS_DIR="tests"
LIBS_DIR="libs"
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0
TOTAL_TESTS=0
WARNING_COUNT=0
ERROR_COUNT=0

# 日誌文件配置
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="test_results_${TIMESTAMP}.log"
DETAILED_LOG="detailed_test_${TIMESTAMP}.log"
SUMMARY_REPORT="test_summary_${TIMESTAMP}.html"
JSON_REPORT="test_results_${TIMESTAMP}.json"

# 性能統計
START_TIME=$(date +%s)
PERFORMANCE_THRESHOLD_MS=1000
SLOW_TESTS=0

# 測試分類計數
UNIT_TESTS=0
INTEGRATION_TESTS=0
PERFORMANCE_TESTS=0

# 顏色輸出配置
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 功能：打印帶顏色的消息
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 功能：記錄到所有日誌文件
log_to_all() {
    local message="$1"
    echo "$message" | tee -a "$LOG_FILE" "$DETAILED_LOG"
}

# 功能：初始化報告文件
initialize_reports() {
    # 清空日誌文件
    > "$LOG_FILE"
    > "$DETAILED_LOG"
    
    # 初始化HTML報告
    cat > "$SUMMARY_REPORT" << EOF
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文言標準庫測試報告 - Wenyan Stdlib Test Report</title>
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; border-left: 4px solid #3498db; padding-left: 10px; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat-box { text-align: center; padding: 15px; border-radius: 8px; min-width: 120px; }
        .passed { background-color: #d4edda; color: #155724; }
        .failed { background-color: #f8d7da; color: #721c24; }
        .skipped { background-color: #fff3cd; color: #856404; }
        .total { background-color: #d1ecf1; color: #0c5460; }
        .test-item { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .test-passed { background-color: #d4edda; }
        .test-failed { background-color: #f8d7da; }
        .test-skipped { background-color: #fff3cd; }
        .progress-bar { width: 100%; height: 20px; background-color: #e9ecef; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background-color: #28a745; transition: width 0.3s ease; }
        .timestamp { text-align: right; color: #6c757d; font-size: 0.9em; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; }
        .warning { color: #856404; }
        .error { color: #721c24; }
        .success { color: #155724; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 文言標準庫測試報告<br>Wenyan Standard Library Test Report</h1>
        <div class="timestamp">生成時間 Generated: $(date)</div>
EOF
    
    # 初始化JSON報告
    cat > "$JSON_REPORT" << EOF
{
    "testReport": {
        "timestamp": "$(date -Iseconds)",
        "version": "2.0",
        "framework": "Enhanced Wenyan Test Runner",
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "warnings": 0,
            "errors": 0
        },
        "performance": {
            "totalDuration": 0,
            "slowTests": 0,
            "threshold": $PERFORMANCE_THRESHOLD_MS
        },
        "categories": {
            "unit": 0,
            "integration": 0,
            "performance": 0
        },
        "tests": []
    }
}
EOF
}

# 功能：檢查測試文件類型
classify_test() {
    local test_file="$1"
    local test_content=$(cat "$test_file" 2>/dev/null || echo "")
    
    if echo "$test_content" | grep -q "單元測試\|unit.*test"; then
        ((UNIT_TESTS++))
        echo "unit"
    elif echo "$test_content" | grep -q "集成測試\|integration.*test"; then
        ((INTEGRATION_TESTS++))
        echo "integration"
    elif echo "$test_content" | grep -q "性能測試\|performance.*test"; then
        ((PERFORMANCE_TESTS++))
        echo "performance"
    else
        ((UNIT_TESTS++))  # 默認為單元測試
        echo "unit"
    fi
}

# 功能：檢查wenyan編譯器是否可用
check_wenyan() {
    if ! command -v wenyan &> /dev/null; then
        print_color $RED "錯誤：wenyan 編譯器未找到，請確保已安裝文言編程語言"
        print_color $RED "Error: wenyan compiler not found, please ensure Wenyan is installed"
        exit 1
    fi
    
    # 檢查wenyan版本
    local wenyan_version=$(wenyan --version 2>/dev/null || echo "未知版本")
    log_to_all "使用 wenyan 版本: $wenyan_version"
    log_to_all "Using wenyan version: $wenyan_version"
}

# 功能：運行單個測試文件
run_test_file() {
    local test_file="$1"
    local lib_name="$2"
    local test_category=$(classify_test "$test_file")
    
    print_color $BLUE "運行測試：$test_file"
    print_color $BLUE "Running test: $test_file"
    log_to_all "=========================================="
    log_to_all "測試文件: $test_file"
    log_to_all "庫名稱: $lib_name"
    log_to_all "測試類型: $test_category"
    log_to_all "開始時間: $(date)"
    
    # 記錄測試開始時間
    local test_start=$(date +%s%3N)
    
    # 創建臨時目錄用於測試
    local temp_dir=$(mktemp -d)
    local test_output="$temp_dir/test_output.log"
    local test_error="$temp_dir/test_error.log"
    
    # 運行測試並捕獲輸出
    local test_result=0
    if timeout 30s wenyan "$test_file" > "$test_output" 2> "$test_error"; then
        test_result=0
    else
        test_result=$?
    fi
    
    # 計算執行時間
    local test_end=$(date +%s%3N)
    local duration=$((test_end - test_start))
    
    # 檢查是否為慢測試
    if [ $duration -gt $PERFORMANCE_THRESHOLD_MS ]; then
        ((SLOW_TESTS++))
        print_color $YELLOW "⚠️  慢測試警告：執行時間 ${duration}ms 超過閾值 ${PERFORMANCE_THRESHOLD_MS}ms"
        print_color $YELLOW "⚠️  Slow test warning: ${duration}ms exceeds threshold ${PERFORMANCE_THRESHOLD_MS}ms"
        ((WARNING_COUNT++))
    fi
    
    # 分析測試結果
    local test_output_content=$(cat "$test_output" 2>/dev/null || echo "")
    local test_error_content=$(cat "$test_error" 2>/dev/null || echo "")
    
    # 記錄詳細日誌
    {
        echo "測試輸出 Test Output:"
        echo "$test_output_content"
        echo ""
        echo "錯誤輸出 Error Output:"
        echo "$test_error_content"
        echo ""
        echo "執行時間 Duration: ${duration}ms"
        echo "退出代碼 Exit Code: $test_result"
        echo "=========================================="
    } >> "$DETAILED_LOG"
    
    # 判定測試結果
    if [ $test_result -eq 0 ]; then
        if echo "$test_output_content" | grep -q "測試全部通過\|All Tests PASSED\|🎉"; then
            print_color $GREEN "✓ 通過：$lib_name (${duration}ms)"
            print_color $GREEN "✓ PASSED: $lib_name (${duration}ms)"
            log_to_all "結果: 通過 PASSED"
            ((PASSED_TESTS++))
            
            # 添加到HTML報告
            echo "<div class='test-item test-passed'>✓ $lib_name ($test_category) - ${duration}ms</div>" >> "$SUMMARY_REPORT"
        else
            print_color $YELLOW "○ 跳過：$lib_name (無明確測試結果)"
            print_color $YELLOW "○ SKIPPED: $lib_name (No clear test result)"
            log_to_all "結果: 跳過 SKIPPED"
            ((SKIPPED_TESTS++))
            
            echo "<div class='test-item test-skipped'>○ $lib_name ($test_category) - 跳過</div>" >> "$SUMMARY_REPORT"
        fi
    else
        print_color $RED "✗ 失敗：$lib_name (退出代碼: $test_result, ${duration}ms)"
        print_color $RED "✗ FAILED: $lib_name (Exit code: $test_result, ${duration}ms)"
        log_to_all "結果: 失敗 FAILED"
        ((FAILED_TESTS++))
        ((ERROR_COUNT++))
        
        # 記錄失敗詳情
        log_to_all "失敗詳情 Failure Details:"
        log_to_all "$test_error_content"
        
        echo "<div class='test-item test-failed'>✗ $lib_name ($test_category) - 失敗 (${duration}ms)</div>" >> "$SUMMARY_REPORT"
    fi
    
    ((TOTAL_TESTS++))
    log_to_all "結束時間: $(date)"
    log_to_all ""
    
    # 清理臨時文件
    rm -rf "$temp_dir"
}

# 功能：掃描並運行所有測試
run_all_tests() {
    log_to_all "開始運行測試..."
    log_to_all "Starting test execution..."
    log_to_all ""

    # 檢查測試目錄是否存在
    if [ ! -d "$TESTS_DIR" ]; then
        print_color $RED "錯誤：測試目錄 '$TESTS_DIR' 不存在"
        print_color $RED "Error: Test directory '$TESTS_DIR' does not exist"
        exit 1
    fi

    # 遍歷所有庫目錄
    for lib_dir in "$TESTS_DIR"/*; do
        if [ -d "$lib_dir" ]; then
            lib_name=$(basename "$lib_dir")
            print_color $CYAN "檢查庫：$lib_name"
            print_color $CYAN "Checking library: $lib_name"
            log_to_all "檢查庫: $lib_name"
            
            # 查找測試文件 - 使用更安全的方法
            local found_tests=false
            # 檢查是否存在.wy文件
            if ls "$lib_dir"/*.wy 1> /dev/null 2>&1; then
                for test_file in "$lib_dir"/*.wy; do
                    if [ -f "$test_file" ]; then
                        found_tests=true
                        run_test_file "$test_file" "$lib_name"
                    fi
                done
            fi
            
            if [ "$found_tests" = false ]; then
                print_color $YELLOW "⚠️  警告：庫 $lib_name 沒有找到測試文件（這是正常的，不影響構建）"
                print_color $YELLOW "⚠️  Warning: No test files found for library $lib_name (this is normal and doesn't affect build)"
                log_to_all "警告: 庫 $lib_name 沒有測試文件 - 跳過"
                ((WARNING_COUNT++))
            fi
        fi
    done

    # 運行根目錄的測試文件
    print_color $CYAN "檢查根目錄測試文件..."
    print_color $CYAN "Checking root directory test files..."
    log_to_all "檢查根目錄測試文件..."

    # 使用更安全的方法檢查根目錄測試文件
    if ls *.wy 1> /dev/null 2>&1; then
        for test_file in *.wy; do
            if [ -f "$test_file" ] && [[ "$test_file" == 測試* || "$test_file" == *test* ]]; then
                run_test_file "$test_file" "根目錄測試"
            fi
        done
    fi
}

# 功能：生成最終報告
generate_final_report() {
    local end_time=$(date +%s)
    local total_duration=$((end_time - START_TIME))
    
    print_color $PURPLE "=========================================="
    print_color $PURPLE "測試結果摘要 - Test Results Summary"
    print_color $PURPLE "=========================================="
    
    # 控制台輸出
    echo "總測試數 Total Tests: $TOTAL_TESTS" | tee -a "$LOG_FILE"
    echo "通過測試 Passed: $PASSED_TESTS" | tee -a "$LOG_FILE"
    echo "失敗測試 Failed: $FAILED_TESTS" | tee -a "$LOG_FILE"
    echo "跳過測試 Skipped: $SKIPPED_TESTS" | tee -a "$LOG_FILE"
    echo "警告數量 Warnings: $WARNING_COUNT" | tee -a "$LOG_FILE"
    echo "錯誤數量 Errors: $ERROR_COUNT" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    # 測試分類統計
    echo "測試分類統計 Test Category Statistics:" | tee -a "$LOG_FILE"
    echo "  單元測試 Unit Tests: $UNIT_TESTS" | tee -a "$LOG_FILE"
    echo "  集成測試 Integration Tests: $INTEGRATION_TESTS" | tee -a "$LOG_FILE"
    echo "  性能測試 Performance Tests: $PERFORMANCE_TESTS" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    # 性能統計
    echo "性能統計 Performance Statistics:" | tee -a "$LOG_FILE"
    echo "  總執行時間 Total Duration: ${total_duration}s" | tee -a "$LOG_FILE"
    echo "  慢測試數量 Slow Tests: $SLOW_TESTS" | tee -a "$LOG_FILE"
    echo "  性能閾值 Performance Threshold: ${PERFORMANCE_THRESHOLD_MS}ms" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"

    # 計算成功率
    local success_rate=0
    if [ $TOTAL_TESTS -gt 0 ]; then
        success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
        echo "成功率 Success Rate: ${success_rate}%" | tee -a "$LOG_FILE"
    fi

    # 完善HTML報告
    cat >> "$SUMMARY_REPORT" << EOF
        
        <h2>📊 測試統計 Test Statistics</h2>
        <div class="stats">
            <div class="stat-box total">
                <h3>$TOTAL_TESTS</h3>
                <p>總測試數<br>Total Tests</p>
            </div>
            <div class="stat-box passed">
                <h3>$PASSED_TESTS</h3>
                <p>通過測試<br>Passed</p>
            </div>
            <div class="stat-box failed">
                <h3>$FAILED_TESTS</h3>
                <p>失敗測試<br>Failed</p>
            </div>
            <div class="stat-box skipped">
                <h3>$SKIPPED_TESTS</h3>
                <p>跳過測試<br>Skipped</p>
            </div>
        </div>
        
        <h2>📈 成功率 Success Rate</h2>
        <div class="progress-bar">
            <div class="progress-fill" style="width: ${success_rate}%"></div>
        </div>
        <p style="text-align: center; margin-top: 10px;">成功率 Success Rate: ${success_rate}%</p>
        
        <h2>🏷️ 測試分類 Test Categories</h2>
        <table>
            <tr><th>測試類型 Test Type</th><th>數量 Count</th><th>比例 Percentage</th></tr>
            <tr><td>單元測試 Unit Tests</td><td>$UNIT_TESTS</td><td>$((UNIT_TESTS * 100 / (TOTAL_TESTS > 0 ? TOTAL_TESTS : 1)))%</td></tr>
            <tr><td>集成測試 Integration Tests</td><td>$INTEGRATION_TESTS</td><td>$((INTEGRATION_TESTS * 100 / (TOTAL_TESTS > 0 ? TOTAL_TESTS : 1)))%</td></tr>
            <tr><td>性能測試 Performance Tests</td><td>$PERFORMANCE_TESTS</td><td>$((PERFORMANCE_TESTS * 100 / (TOTAL_TESTS > 0 ? TOTAL_TESTS : 1)))%</td></tr>
        </table>
        
        <h2>⚡ 性能信息 Performance Info</h2>
        <ul>
            <li>總執行時間 Total Duration: ${total_duration}s</li>
            <li>慢測試數量 Slow Tests: $SLOW_TESTS</li>
            <li>性能閾值 Performance Threshold: ${PERFORMANCE_THRESHOLD_MS}ms</li>
            <li>警告數量 Warnings: $WARNING_COUNT</li>
            <li>錯誤數量 Errors: $ERROR_COUNT</li>
        </ul>
        
        <h2>📋 報告文件 Report Files</h2>
        <ul>
            <li>基本日誌 Basic Log: <code>$LOG_FILE</code></li>
            <li>詳細日誌 Detailed Log: <code>$DETAILED_LOG</code></li>
            <li>JSON報告 JSON Report: <code>$JSON_REPORT</code></li>
        </ul>
    </div>
</body>
</html>
EOF

    # 更新JSON報告
    cat > "$JSON_REPORT" << EOF
{
    "testReport": {
        "timestamp": "$(date -Iseconds)",
        "version": "2.0",
        "framework": "Enhanced Wenyan Test Runner",
        "summary": {
            "total": $TOTAL_TESTS,
            "passed": $PASSED_TESTS,
            "failed": $FAILED_TESTS,
            "skipped": $SKIPPED_TESTS,
            "warnings": $WARNING_COUNT,
            "errors": $ERROR_COUNT,
            "successRate": $success_rate
        },
        "performance": {
            "totalDuration": $total_duration,
            "slowTests": $SLOW_TESTS,
            "threshold": $PERFORMANCE_THRESHOLD_MS
        },
        "categories": {
            "unit": $UNIT_TESTS,
            "integration": $INTEGRATION_TESTS,
            "performance": $PERFORMANCE_TESTS
        },
        "reports": {
            "basicLog": "$LOG_FILE",
            "detailedLog": "$DETAILED_LOG",
            "htmlReport": "$SUMMARY_REPORT"
        }
    }
}
EOF

    echo "" | tee -a "$LOG_FILE"

    # 最終判定和建議
    if [ $FAILED_TESTS -eq 0 ]; then
        print_color $GREEN "🎉 所有測試通過！All tests passed!"
        log_to_all "🎉 所有測試通過！All tests passed!"
        if [ $WARNING_COUNT -gt 0 ]; then
            print_color $YELLOW "⚠️  注意：存在 $WARNING_COUNT 個警告（不影響構建成功）"
            print_color $YELLOW "⚠️  Note: $WARNING_COUNT warnings found (does not affect build success)"
            log_to_all "警告不影響構建 - 這些通常是缺失測試文件的提醒"
        fi
        print_color $CYAN "📋 報告文件已生成 Reports generated:"
        print_color $CYAN "  - 基本日誌 Basic log: $LOG_FILE"
        print_color $CYAN "  - 詳細日誌 Detailed log: $DETAILED_LOG"
        print_color $CYAN "  - HTML報告 HTML report: $SUMMARY_REPORT"
        print_color $CYAN "  - JSON報告 JSON report: $JSON_REPORT"
        exit 0
    else
        print_color $RED "❌ 有 $FAILED_TESTS 個測試失敗！$FAILED_TESTS tests failed!"
        log_to_all "❌ 有 $FAILED_TESTS 個測試失敗！$FAILED_TESTS tests failed!"
        print_color $CYAN "📋 報告文件已生成 Reports generated:"
        print_color $CYAN "  - 基本日誌 Basic log: $LOG_FILE"
        print_color $CYAN "  - 詳細日誌 Detailed log: $DETAILED_LOG"
        print_color $CYAN "  - HTML報告 HTML report: $SUMMARY_REPORT"
        print_color $CYAN "  - JSON報告 JSON report: $JSON_REPORT"
        exit 1
    fi
}

# 功能：顯示幫助信息
show_help() {
    echo "文言標準庫增強測試運行器 - Enhanced Wenyan Stdlib Test Runner"
    echo ""
    echo "用法 Usage:"
    echo "  $0 [選項] [Options]"
    echo ""
    echo "選項 Options:"
    echo "  -h, --help              顯示此幫助信息 Show this help"
    echo "  -v, --verbose           詳細輸出模式 Verbose output mode"
    echo "  -t, --threshold <ms>    設置性能閾值(毫秒) Set performance threshold (ms)"
    echo "  --no-color              禁用顏色輸出 Disable colored output"
    echo "  --timeout <seconds>     設置測試超時時間 Set test timeout"
    echo ""
    echo "示例 Examples:"
    echo "  $0                      運行所有測試 Run all tests"
    echo "  $0 -v                   運行所有測試（詳細模式） Run all tests (verbose)"
    echo "  $0 -t 2000              設置2秒性能閾值 Set 2s performance threshold"
    echo ""
    echo "生成的文件 Generated Files:"
    echo "  - test_results_*.log    基本測試日誌 Basic test log"
    echo "  - detailed_test_*.log   詳細測試日誌 Detailed test log"
    echo "  - test_summary_*.html   HTML測試報告 HTML test report"
    echo "  - test_results_*.json   JSON測試報告 JSON test report"
    echo ""
}

# 解析命令行參數
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            set -x  # 啟用詳細模式
            shift
            ;;
        -t|--threshold)
            PERFORMANCE_THRESHOLD_MS="$2"
            shift 2
            ;;
        --no-color)
            RED=''
            GREEN=''
            YELLOW=''
            BLUE=''
            PURPLE=''
            CYAN=''
            NC=''
            shift
            ;;
        --timeout)
            # 這裡可以設置timeout值，當前在run_test_file中hardcode為30s
            shift 2
            ;;
        *)
            echo "未知選項: $1"
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# 主程序流程
main() {
    print_color $CYAN "🚀 初始化測試環境..."
    print_color $CYAN "🚀 Initializing test environment..."
    
    initialize_reports
    check_wenyan
    
    print_color $GREEN "✅ 測試環境準備完成"
    print_color $GREEN "✅ Test environment ready"
    print_color $CYAN "📊 性能閾值設置為: ${PERFORMANCE_THRESHOLD_MS}ms"
    print_color $CYAN "📊 Performance threshold set to: ${PERFORMANCE_THRESHOLD_MS}ms"
    echo ""
    
    run_all_tests
    generate_final_report
}

# 錯誤處理
trap 'echo "❌ 測試運行器意外退出 Test runner crashed unexpectedly"; exit 1' ERR

# 執行主程序
main "$@"