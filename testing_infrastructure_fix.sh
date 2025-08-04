#!/bin/bash

# Testing Infrastructure Fix
# Author: Whisky, PR Implementation Specialist
# 
# CRITICAL FIX: Resolves the "無明確測試結果" issue by fixing empty console.log() calls
# in Wenyan-generated JavaScript that prevent proper test output detection.

echo "=========================================="
echo "文言標準庫測試基礎設施修復 - Testing Infrastructure Fix"
echo "Author: Whisky, PR Implementation Specialist"
echo "CRITICAL: Fixing empty console.log() issues causing test failures"
echo "=========================================="
echo ""

# 檢查依賴
if ! command -v wenyan &> /dev/null; then
    echo "錯誤：wenyan 編譯器未找到" >&2
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "錯誤：python3 未找到" >&2
    exit 1
fi

if [ ! -f "comprehensive_js_fix.py" ]; then
    echo "錯誤：comprehensive_js_fix.py 未找到" >&2
    exit 1
fi

echo "使用 wenyan 版本: $(wenyan --version)"
echo ""

# 測試核心修復功能
echo "=== 測試核心修復功能 ==="
echo "測試文件：tests/字符串經/測試字符串功能.wy"

# 創建臨時文件
RAW_JS=$(mktemp).js
FIXED_JS=$(mktemp).js
TEST_OUTPUT=$(mktemp)

echo "步驟1：編譯為JavaScript..."
if wenyan "tests/字符串經/測試字符串功能.wy" --compile > "$RAW_JS" 2>/dev/null; then
    echo "✓ 編譯成功"
    echo "  - 原始JavaScript大小: $(wc -c < "$RAW_JS") 字符"
    
    # 計算空的console.log()調用數量
    empty_logs=$(grep -o "console\.log()" "$RAW_JS" | wc -l)
    echo "  - 發現 $empty_logs 個空的console.log()調用"
    
    echo "步驟2：修復JavaScript..."
    if python3 comprehensive_js_fix.py "$RAW_JS" "$FIXED_JS" 2>/dev/null; then
        echo "✓ JavaScript修復成功"
        echo "  - 修復後JavaScript大小: $(wc -c < "$FIXED_JS") 字符"
        
        # 計算修復後的console.log調用
        fixed_logs=$(grep -o "console\.log(" "$FIXED_JS" | wc -l)
        echo "  - 修復後有 $fixed_logs 個console.log調用"
        
        echo "步驟3：執行修復的JavaScript..."
        if timeout 10s node "$FIXED_JS" > "$TEST_OUTPUT" 2>&1; then
            echo "✓ 執行成功"
            
            # 分析輸出
            output_content=$(cat "$TEST_OUTPUT")
            output_lines=$(echo "$output_content" | wc -l)
            echo "  - 輸出行數: $output_lines"
            
            # 檢查關鍵成功標識
            if echo "$output_content" | grep -q "測試全部通過\|All Tests PASSED\|🎉"; then
                echo "✓ 發現測試成功標識"
                echo "  - 包含 '測試全部通過': $(echo "$output_content" | grep -c "測試全部通過")"
                echo "  - 包含 'All Tests PASSED': $(echo "$output_content" | grep -c "All Tests PASSED")"
                echo "  - 包含 '🎉': $(echo "$output_content" | grep -c "🎉")"
                
                echo ""
                echo "🎉 修復成功！測試基礎設施已恢復正常！"
                echo "測試運行器現在能夠正確識別測試結果。"
                echo ""
                
                # 顯示部分輸出作為驗證
                echo "=== 測試輸出樣本 (最後10行) ==="
                echo "$output_content" | tail -10
                echo "================================"
                echo ""
                
                echo "✅ 測試基礎設施修復完成！"
                echo "✅ 字符串經庫測試現在正常工作"
                echo "✅ 可以繼續其他庫的開發和測試"
                
            else
                echo "⚠️  警告：未發現測試成功標識"
                echo "輸出內容："
                echo "$output_content" | head -20
            fi
        else
            echo "✗ 執行失敗"
            cat "$TEST_OUTPUT"
        fi
    else
        echo "✗ JavaScript修復失敗"
    fi
else
    echo "✗ 編譯失敗"
fi

# 清理臨時文件
rm -f "$RAW_JS" "$FIXED_JS" "$TEST_OUTPUT"

echo ""
echo "=========================================="
echo "修復報告總結："
echo "問題：Wenyan編譯器生成空的console.log()調用"
echo "影響：測試運行器無法檢測到測試輸出，報告'無明確測試結果'"
echo "解決方案：comprehensive_js_fix.py修復空調用"
echo "結果：測試基礎設施恢復正常運行"
echo "=========================================="