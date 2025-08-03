#!/bin/bash

# 運行所有測試腳本 - Run All Tests Script
# Author: Whisky, PR Worker
# 
# 批量運行所有庫的測試文件並生成報告
# Batch run all library test files and generate reports

echo "=========================================="
echo "文言標準庫測試運行器 - Wenyan Stdlib Test Runner"
echo "Author: Whisky, PR Worker"
echo "=========================================="
echo ""

# 設置變量
TESTS_DIR="tests"
LIBS_DIR="libs"
PASSED_TESTS=0
FAILED_TESTS=0
TOTAL_TESTS=0
LOG_FILE="test_results.log"

# 清空日誌文件
> "$LOG_FILE"

# 檢查 wenyan 是否可用
if ! command -v wenyan &> /dev/null; then
    echo "錯誤：wenyan 編譯器未找到，請確保已安裝文言編程語言" >&2
    echo "Error: wenyan compiler not found, please ensure Wenyan is installed" >&2
    exit 1
fi

echo "開始運行測試..." | tee -a "$LOG_FILE"
echo "Starting test execution..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 函數：運行單個測試文件
run_test_file() {
    local test_file="$1"
    local lib_name="$2"
    
    echo "運行測試：$test_file" | tee -a "$LOG_FILE"
    echo "Running test: $test_file" | tee -a "$LOG_FILE"
    
    # 運行測試
    if wenyan "$test_file" >> "$LOG_FILE" 2>&1; then
        echo "✓ 通過：$lib_name" | tee -a "$LOG_FILE"
        echo "✓ PASSED: $lib_name" | tee -a "$LOG_FILE"
        ((PASSED_TESTS++))
    else
        echo "✗ 失敗：$lib_name" | tee -a "$LOG_FILE"
        echo "✗ FAILED: $lib_name" | tee -a "$LOG_FILE"
        ((FAILED_TESTS++))
    fi
    
    ((TOTAL_TESTS++))
    echo "" | tee -a "$LOG_FILE"
}

# 檢查測試目錄是否存在
if [ ! -d "$TESTS_DIR" ]; then
    echo "錯誤：測試目錄 '$TESTS_DIR' 不存在" >&2
    echo "Error: Test directory '$TESTS_DIR' does not exist" >&2
    exit 1
fi

# 遍歷所有庫目錄
for lib_dir in "$TESTS_DIR"/*; do
    if [ -d "$lib_dir" ]; then
        lib_name=$(basename "$lib_dir")
        echo "檢查庫：$lib_name" | tee -a "$LOG_FILE"
        echo "Checking library: $lib_name" | tee -a "$LOG_FILE"
        
        # 查找測試文件
        for test_file in "$lib_dir"/*.wy; do
            if [ -f "$test_file" ]; then
                run_test_file "$test_file" "$lib_name"
            fi
        done
    fi
done

# 運行根目錄的測試文件
echo "檢查根目錄測試文件..." | tee -a "$LOG_FILE"
echo "Checking root directory test files..." | tee -a "$LOG_FILE"

for test_file in *.wy; do
    if [ -f "$test_file" ] && [[ "$test_file" == 測試* ]]; then
        run_test_file "$test_file" "根目錄測試"
    fi
done

# 生成最終報告
echo "==========================================" | tee -a "$LOG_FILE"
echo "測試結果摘要 - Test Results Summary" | tee -a "$LOG_FILE"
echo "==========================================" | tee -a "$LOG_FILE"
echo "總測試數 Total Tests: $TOTAL_TESTS" | tee -a "$LOG_FILE"
echo "通過測試 Passed: $PASSED_TESTS" | tee -a "$LOG_FILE"
echo "失敗測試 Failed: $FAILED_TESTS" | tee -a "$LOG_FILE"

if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "成功率 Success Rate: ${SUCCESS_RATE}%" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

if [ $FAILED_TESTS -eq 0 ]; then
    echo "🎉 所有測試通過！All tests passed!" | tee -a "$LOG_FILE"
    exit 0
else
    echo "❌ 有 $FAILED_TESTS 個測試失敗！$FAILED_TESTS tests failed!" | tee -a "$LOG_FILE"
    echo "詳細日誌請查看：$LOG_FILE" | tee -a "$LOG_FILE"
    echo "Detailed logs available in: $LOG_FILE" | tee -a "$LOG_FILE"
    exit 1
fi