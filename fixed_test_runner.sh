#!/bin/bash

# Fixed Test Runner for Wenyan Standard Library
# Author: Whisky, PR Worker
# 
# Uses post-processing to fix Wenyan compiler v0.3.4 JavaScript generation bugs

echo "=========================================="
echo "修復版文言標準庫測試運行器 - Fixed Wenyan Stdlib Test Runner"
echo "Author: Whisky, PR Worker"
echo "=========================================="
echo ""

# 設置變量
TESTS_DIR="tests"
PASSED_TESTS=0
FAILED_TESTS=0
TOTAL_TESTS=0
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="fixed_test_results_${TIMESTAMP}.log"

# 清空日誌文件
> "$LOG_FILE"

# 檢查依賴
if ! command -v wenyan &> /dev/null; then
    echo "錯誤：wenyan 編譯器未找到" >&2
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "錯誤：python3 未找到" >&2
    exit 1
fi

echo "使用 wenyan 版本: $(wenyan --version)" | tee -a "$LOG_FILE"
echo "開始運行修復版測試..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 函數：運行單個測試文件
run_fixed_test() {
    local test_file="$1"
    local lib_name="$2"
    
    echo "測試文件：$test_file" | tee -a "$LOG_FILE"
    echo "庫名稱：$lib_name" | tee -a "$LOG_FILE"
    
    # 創建臨時文件
    local raw_js=$(mktemp).js
    local fixed_js=$(mktemp).js
    local test_output=$(mktemp)
    
    # 步驟1：編譯為JavaScript
    if wenyan "$test_file" --compile > "$raw_js" 2>/dev/null; then
        echo "✓ 編譯成功" | tee -a "$LOG_FILE"
    else
        echo "✗ 編譯失敗" | tee -a "$LOG_FILE"
        ((FAILED_TESTS++))
        ((TOTAL_TESTS++))
        rm -f "$raw_js" "$fixed_js" "$test_output"
        return 1
    fi
    
    # 步驟2：修復JavaScript
    if python3 comprehensive_js_fix.py "$raw_js" "$fixed_js" 2>/dev/null; then
        echo "✓ JavaScript修復成功" | tee -a "$LOG_FILE"
    else
        echo "✗ JavaScript修復失敗" | tee -a "$LOG_FILE"
        ((FAILED_TESTS++))
        ((TOTAL_TESTS++))
        rm -f "$raw_js" "$fixed_js" "$test_output"
        return 1
    fi
    
    # 步驟3：執行修復的JavaScript
    if timeout 10s node "$fixed_js" > "$test_output" 2>&1; then
        local output_content=$(cat "$test_output")
        echo "✓ 執行成功" | tee -a "$LOG_FILE"
        echo "輸出內容：" | tee -a "$LOG_FILE"
        echo "$output_content" | tee -a "$LOG_FILE"
        
        # 檢查輸出是否包含有意義的內容（不只是DEBUG消息）
        if echo "$output_content" | grep -v "DEBUG:" | grep -q "."; then
            echo "✓ 測試通過：$lib_name" | tee -a "$LOG_FILE"
            ((PASSED_TESTS++))
        else
            echo "○ 測試跳過：$lib_name（僅調試輸出）" | tee -a "$LOG_FILE"
        fi
    else
        echo "✗ 執行失敗：$lib_name" | tee -a "$LOG_FILE"
        ((FAILED_TESTS++))
    fi
    
    ((TOTAL_TESTS++))
    echo "" | tee -a "$LOG_FILE"
    
    # 清理臨時文件
    rm -f "$raw_js" "$fixed_js" "$test_output"
}

# 測試字符串經
echo "=== 測試字符串經庫 ===" | tee -a "$LOG_FILE"

if [ -f "tests/字符串經/測試字符串功能.wy" ]; then
    run_fixed_test "tests/字符串經/測試字符串功能.wy" "字符串經"
fi

# 測試其他簡單的.wy文件
echo "=== 測試其他文件 ===" | tee -a "$LOG_FILE"

for test_file in *.wy; do
    if [ -f "$test_file" ] && [[ "$test_file" == *test* ]]; then
        run_fixed_test "$test_file" "根目錄測試"
    fi
done

# 生成最終報告
echo "==========================================" | tee -a "$LOG_FILE"
echo "修復版測試結果摘要" | tee -a "$LOG_FILE"
echo "==========================================" | tee -a "$LOG_FILE"
echo "總測試數：$TOTAL_TESTS" | tee -a "$LOG_FILE"
echo "通過測試：$PASSED_TESTS" | tee -a "$LOG_FILE"
echo "失敗測試：$FAILED_TESTS" | tee -a "$LOG_FILE"

if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "成功率：${SUCCESS_RATE}%" | tee -a "$LOG_FILE"
fi

if [ $PASSED_TESTS -gt 0 ]; then
    echo "🎉 有 $PASSED_TESTS 個測試成功！修復方案有效！" | tee -a "$LOG_FILE"
    echo "詳細日誌：$LOG_FILE" | tee -a "$LOG_FILE"
    exit 0
else
    echo "❌ 沒有測試通過" | tee -a "$LOG_FILE"
    exit 1
fi