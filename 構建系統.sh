#!/bin/bash

# 文言標準庫構建系統 - Wenyan Standard Library Build System
# Author: Whisky, PR Worker
# Version: 2.0
# 
# 自動化構建、驗證和打包所有庫文件
# Automated building, validation and packaging of all library files

set -euo pipefail  # 嚴格錯誤處理

# 顏色輸出配置
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 構建配置
BUILD_DIR="build"
DIST_DIR="dist"  
DOCS_DIR="docs/generated"
LIBS_DIR="libs"
TESTS_DIR="tests"
EXAMPLES_DIR="examples"

# 構建統計
TOTAL_LIBS=0
SUCCESSFUL_BUILDS=0
FAILED_BUILDS=0
TOTAL_TESTS=0
PASSED_TESTS=0

# 時間戳
BUILD_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BUILD_LOG="build_${BUILD_TIMESTAMP}.log"

# 功能：打印帶顏色的消息
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 功能：記錄日誌
log_message() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" | tee -a "$BUILD_LOG"
}

# 功能：顯示構建橫幅
show_banner() {
    print_color $CYAN "=================================================="
    print_color $CYAN "    文言標準庫構建系統 v2.0"
    print_color $CYAN "    Wenyan Standard Library Build System v2.0"
    print_color $CYAN "    Author: Whisky, PR Worker"
    print_color $CYAN "=================================================="
    echo ""
    log_message "構建系統啟動 Build system started"
}

# 功能：初始化構建環境
init_build_env() {
    print_color $BLUE "🔧 初始化構建環境 Initializing build environment..."
    
    # 創建構建目錄
    mkdir -p "$BUILD_DIR"
    mkdir -p "$DIST_DIR"
    mkdir -p "$DOCS_DIR"
    
    # 清理之前的構建
    rm -rf "$BUILD_DIR"/*
    rm -rf "$DIST_DIR"/*
    rm -rf "$DOCS_DIR"/*
    
    # 檢查wenyan編譯器
    if ! command -v wenyan &> /dev/null; then
        print_color $RED "❌ 錯誤：wenyan編譯器未找到"
        print_color $RED "❌ Error: wenyan compiler not found"
        exit 1
    fi
    
    # 檢查必要目錄
    if [ ! -d "$LIBS_DIR" ]; then
        print_color $RED "❌ 錯誤：找不到庫目錄 $LIBS_DIR"
        print_color $RED "❌ Error: Libraries directory $LIBS_DIR not found"
        exit 1
    fi
    
    log_message "構建環境初始化完成 Build environment initialized"
    print_color $GREEN "✅ 構建環境準備完成 Build environment ready"
    echo ""
}

# 功能：驗證單個文件
validate_file() {
    local file_path="$1"
    local file_name=$(basename "$file_path")
    
    print_color $BLUE "🔍 驗證文件 Validating: $file_name"
    
    # 語法檢查
    if wenyan -c "$file_path" &> /dev/null; then
        print_color $GREEN "  ✅ 語法檢查通過 Syntax validation passed"
        return 0
    else
        print_color $RED "  ❌ 語法檢查失敗 Syntax validation failed"
        log_message "語法錯誤 Syntax error in: $file_path"
        return 1
    fi
}

# 功能：編譯單個文件
compile_file() {
    local file_path="$1"
    local lib_name="$2"
    local file_name=$(basename "$file_path")
    local output_dir="$BUILD_DIR/$lib_name"
    
    mkdir -p "$output_dir"
    
    print_color $BLUE "🔨 編譯文件 Compiling: $file_name"
    
    # 編譯為JavaScript
    local js_output="$output_dir/${file_name%.wy}.js"
    if wenyan -c "$file_path" -o "$js_output" 2>/dev/null; then
        print_color $GREEN "  ✅ 編譯成功 Compilation successful: $js_output"
        log_message "編譯成功 Compiled successfully: $file_path -> $js_output"
        return 0
    else
        print_color $RED "  ❌ 編譯失敗 Compilation failed"
        log_message "編譯失敗 Compilation failed: $file_path"
        return 1
    fi
}

# 功能：構建單個庫
build_library() {
    local lib_dir="$1"
    local lib_name=$(basename "$lib_dir")
    
    print_color $PURPLE "📚 構建庫 Building library: $lib_name"
    print_color $PURPLE "=========================================="
    
    local lib_success=true
    local lib_file_count=0
    local lib_success_count=0
    
    # 遍歷庫中的所有.wy文件
    for wy_file in "$lib_dir"/*.wy; do
        if [ -f "$wy_file" ]; then
            ((lib_file_count++))
            
            # 驗證文件
            if validate_file "$wy_file"; then
                # 編譯文件
                if compile_file "$wy_file" "$lib_name"; then
                    ((lib_success_count++))
                else
                    lib_success=false
                fi
            else
                lib_success=false
            fi
        fi
    done
    
    # 庫構建結果
    if [ "$lib_success" = true ] && [ $lib_file_count -gt 0 ]; then
        print_color $GREEN "✅ 庫構建成功 Library build successful: $lib_name ($lib_success_count/$lib_file_count files)"
        ((SUCCESSFUL_BUILDS++))
        
        # 創建庫包
        create_library_package "$lib_name"
    else
        print_color $RED "❌ 庫構建失敗 Library build failed: $lib_name ($lib_success_count/$lib_file_count files)"
        ((FAILED_BUILDS++))
    fi
    
    ((TOTAL_LIBS++))
    echo ""
}

# 功能：創建庫包
create_library_package() {
    local lib_name="$1"
    local package_dir="$DIST_DIR/$lib_name"
    
    print_color $CYAN "📦 創建庫包 Creating package for: $lib_name"
    
    mkdir -p "$package_dir"
    
    # 復制源文件
    if [ -d "$LIBS_DIR/$lib_name" ]; then
        cp -r "$LIBS_DIR/$lib_name"/*.wy "$package_dir/" 2>/dev/null || true
    fi
    
    # 復制編譯文件
    if [ -d "$BUILD_DIR/$lib_name" ]; then
        cp -r "$BUILD_DIR/$lib_name"/*.js "$package_dir/" 2>/dev/null || true
    fi
    
    # 創建包信息文件
    create_package_info "$lib_name" "$package_dir"
    
    # 創建tar包
    cd "$DIST_DIR"
    tar -czf "${lib_name}_${BUILD_TIMESTAMP}.tar.gz" "$lib_name"
    cd - > /dev/null
    
    print_color $GREEN "  ✅ 庫包創建完成 Package created: ${lib_name}_${BUILD_TIMESTAMP}.tar.gz"
}

# 功能：創建包信息文件
create_package_info() {
    local lib_name="$1"
    local package_dir="$2"
    local info_file="$package_dir/package.json"
    
    cat > "$info_file" << EOF
{
    "name": "$lib_name",
    "version": "1.0.0",
    "description": "文言標準庫 - $lib_name",
    "language": "wenyan",
    "author": "Wenyan Standard Library Team",
    "buildDate": "$(date -Iseconds)",
    "buildTimestamp": "$BUILD_TIMESTAMP",
    "files": {
        "source": [],
        "compiled": []
    },
    "dependencies": [],
    "keywords": ["wenyan", "standard-library", "$lib_name"],
    "repository": "https://github.com/wenyan-lang/wenyan-stdlib",
    "license": "MIT"
}
EOF

    # 添加文件列表
    if [ -d "$package_dir" ]; then
        local source_files=$(find "$package_dir" -name "*.wy" -exec basename {} \; | jq -R . | jq -s .)
        local compiled_files=$(find "$package_dir" -name "*.js" -exec basename {} \; | jq -R . | jq -s .)
        
        # 更新package.json
        jq ".files.source = $source_files | .files.compiled = $compiled_files" "$info_file" > "${info_file}.tmp" && mv "${info_file}.tmp" "$info_file"
    fi
}

# 功能：構建所有庫
build_all_libraries() {
    print_color $PURPLE "🏗️  開始構建所有庫 Starting to build all libraries..."
    print_color $PURPLE "======================================================"
    echo ""
    
    # 遍歷所有庫目錄
    for lib_dir in "$LIBS_DIR"/*; do
        if [ -d "$lib_dir" ]; then
            build_library "$lib_dir"
        fi
    done
    
    log_message "所有庫構建完成 All library builds completed"
}

# 功能：運行測試
run_tests() {
    print_color $PURPLE "🧪 運行測試套件 Running test suite..."
    print_color $PURPLE "======================================"
    
    if [ -f "./增強測試運行器.sh" ]; then
        # 運行增強測試運行器
        if ./增強測試運行器.sh; then
            print_color $GREEN "✅ 測試套件通過 Test suite passed"
            log_message "測試套件通過 Test suite passed"
        else
            print_color $RED "❌ 測試套件失敗 Test suite failed"
            log_message "測試套件失敗 Test suite failed"
            return 1
        fi
    else
        print_color $YELLOW "⚠️  未找到測試運行器，跳過測試 Test runner not found, skipping tests"
        log_message "測試運行器未找到 Test runner not found"
    fi
    
    echo ""
}

# 功能：生成文檔
generate_documentation() {
    print_color $PURPLE "📖 生成文檔 Generating documentation..."
    print_color $PURPLE "======================================="
    
    # 創建主文檔索引
    local index_file="$DOCS_DIR/index.html"
    
    cat > "$index_file" << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文言標準庫文檔 - Wenyan Standard Library Documentation</title>
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 15px; }
        h2 { color: #34495e; border-left: 4px solid #3498db; padding-left: 15px; }
        .library-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .library-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; }
        .library-card h3 { color: #495057; margin-top: 0; }
        .build-info { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .timestamp { text-align: right; color: #6c757d; font-size: 0.9em; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 文言標準庫文檔<br>Wenyan Standard Library Documentation</h1>
        
        <div class="build-info">
            <h3>📋 構建信息 Build Information</h3>
            <ul>
                <li><strong>構建時間 Build Time:</strong> $(date)</li>
                <li><strong>構建版本 Build Version:</strong> $BUILD_TIMESTAMP</li>
                <li><strong>構建系統 Build System:</strong> Wenyan Standard Library Build System v2.0</li>
                <li><strong>作者 Author:</strong> Whisky, PR Worker</li>
            </ul>
        </div>
        
        <h2>📚 可用庫 Available Libraries</h2>
        <div class="library-grid">
EOF

    # 為每個庫生成文檔卡片
    for lib_dir in "$LIBS_DIR"/*; do
        if [ -d "$lib_dir" ]; then
            local lib_name=$(basename "$lib_dir")
            local lib_file_count=$(find "$lib_dir" -name "*.wy" | wc -l)
            
            cat >> "$index_file" << EOF
            <div class="library-card">
                <h3>📦 $lib_name</h3>
                <p><strong>文件數量 File Count:</strong> $lib_file_count</p>
                <p><strong>位置 Location:</strong> libs/$lib_name/</p>
                <p><strong>包文件 Package:</strong> <a href="../dist/${lib_name}_${BUILD_TIMESTAMP}.tar.gz">${lib_name}_${BUILD_TIMESTAMP}.tar.gz</a></p>
            </div>
EOF
        fi
    done
    
    cat >> "$index_file" << 'EOF'
        </div>
        
        <h2>🔧 開發工具 Development Tools</h2>
        <div class="library-grid">
            <div class="library-card">
                <h3>🧪 測試框架 Testing Framework</h3>
                <ul>
                    <li>增強測試框架.wy - Enhanced testing with detailed reporting</li>
                    <li>增強性能測試框架.wy - Performance benchmarking framework</li>
                    <li>增強測試運行器.sh - Automated test runner</li>
                </ul>
            </div>
            <div class="library-card">
                <h3>🏗️ 構建系統 Build System</h3>
                <ul>
                    <li>構建系統.sh - Automated build and packaging</li>
                    <li>API設計模式標準.wy - API design patterns</li>
                    <li>錯誤處理標準.wy - Error handling standards</li>
                </ul>
            </div>
            <div class="library-card">
                <h3>📖 文檔標準 Documentation Standards</h3>
                <ul>
                    <li>文言編碼標準指南.md - Comprehensive coding standards</li>
                    <li>Automated documentation generation</li>
                    <li>API reference documentation</li>
                </ul>
            </div>
        </div>
        
        <div class="timestamp">
            文檔生成時間 Documentation generated: $(date)<br>
            構建系統版本 Build system version: 2.0
        </div>
    </div>
</body>
</html>
EOF

    print_color $GREEN "✅ 文檔生成完成 Documentation generated: $index_file"
    log_message "文檔生成完成 Documentation generated"
    echo ""
}

# 功能：創建發布歸檔
create_release_archive() {
    print_color $PURPLE "📁 創建發布歸檔 Creating release archive..."
    print_color $PURPLE "=============================================="
    
    local release_name="wenyan-stdlib-${BUILD_TIMESTAMP}"
    local release_dir="$DIST_DIR/$release_name"
    
    mkdir -p "$release_dir"
    
    # 復制所有構建產物
    cp -r "$BUILD_DIR"/* "$release_dir/" 2>/dev/null || true
    cp -r "$DOCS_DIR"/* "$release_dir/docs/" 2>/dev/null || mkdir -p "$release_dir/docs"
    
    # 復制重要文件
    cp README.md "$release_dir/" 2>/dev/null || true
    cp 文言編碼標準指南.md "$release_dir/" 2>/dev/null || true
    cp API設計模式標準.wy "$release_dir/" 2>/dev/null || true
    
    # 創建發布信息文件
    cat > "$release_dir/RELEASE_INFO.md" << EOF
# 文言標準庫發布信息
# Wenyan Standard Library Release Information

**發布版本 Release Version**: $BUILD_TIMESTAMP  
**發布時間 Release Date**: $(date)  
**構建系統 Build System**: Wenyan Standard Library Build System v2.0  
**作者 Author**: Whisky, PR Worker  

## 構建統計 Build Statistics

- **總庫數 Total Libraries**: $TOTAL_LIBS
- **成功構建 Successful Builds**: $SUCCESSFUL_BUILDS  
- **失敗構建 Failed Builds**: $FAILED_BUILDS
- **構建成功率 Build Success Rate**: $(( SUCCESSFUL_BUILDS * 100 / (TOTAL_LIBS > 0 ? TOTAL_LIBS : 1) ))%

## 包含內容 Contents

- **源代碼 Source Code**: 所有庫的.wy源文件
- **編譯文件 Compiled Files**: JavaScript編譯輸出
- **文檔 Documentation**: API文檔和使用指南
- **測試框架 Testing Framework**: 完整的測試基礎設施
- **開發工具 Development Tools**: 構建和開發工具

## 使用方法 Usage

1. 解壓發布包 Extract the release package
2. 閱讀文檔 Read the documentation in docs/
3. 查看示例 Check examples in examples/
4. 運行測試 Run tests using the testing framework

## 技術要求 Requirements

- wenyan 編譯器 wenyan compiler
- Node.js (for JavaScript output)
- Bash (for build scripts)

## 支持 Support

如有問題請參考文檔或提交Issue
For questions, please refer to documentation or submit an issue

---
**生成時間 Generated**: $(date)
EOF
    
    # 創建最終歸檔
    cd "$DIST_DIR"
    tar -czf "${release_name}.tar.gz" "$release_name"
    cd - > /dev/null
    
    print_color $GREEN "✅ 發布歸檔創建完成 Release archive created: ${release_name}.tar.gz"
    log_message "發布歸檔創建完成 Release archive created"
    echo ""
}

# 功能：顯示構建摘要
show_build_summary() {
    local end_time=$(date +%s)
    local start_time_file=".build_start_time"
    local duration=0
    
    if [ -f "$start_time_file" ]; then
        local start_time=$(cat "$start_time_file")
        duration=$((end_time - start_time))
        rm -f "$start_time_file"
    fi
    
    print_color $PURPLE "======================================================"
    print_color $PURPLE "          構建摘要 Build Summary"
    print_color $PURPLE "======================================================"
    
    echo "📊 構建統計 Build Statistics:"
    echo "   └─ 總庫數 Total Libraries: $TOTAL_LIBS"
    echo "   └─ 成功構建 Successful Builds: $SUCCESSFUL_BUILDS"
    echo "   └─ 失敗構建 Failed Builds: $FAILED_BUILDS"
    echo "   └─ 構建時間 Build Duration: ${duration}s"
    echo ""
    
    echo "📁 輸出文件 Output Files:"
    echo "   └─ 構建目錄 Build Directory: $BUILD_DIR/"
    echo "   └─ 發布目錄 Distribution Directory: $DIST_DIR/"
    echo "   └─ 文檔目錄 Documentation Directory: $DOCS_DIR/"
    echo "   └─ 構建日誌 Build Log: $BUILD_LOG"
    echo ""
    
    if [ $FAILED_BUILDS -eq 0 ]; then
        print_color $GREEN "🎉 構建成功！所有庫都已成功構建"
        print_color $GREEN "🎉 Build Successful! All libraries built successfully"
        log_message "構建成功完成 Build completed successfully"
    else
        print_color $RED "❌ 構建部分失敗！$FAILED_BUILDS 個庫構建失敗"
        print_color $RED "❌ Build Partially Failed! $FAILED_BUILDS libraries failed to build"
        log_message "構建部分失敗 Build completed with failures"
    fi
    
    echo ""
    print_color $CYAN "📋 檢查詳細日誌: $BUILD_LOG"
    print_color $CYAN "📋 Check detailed log: $BUILD_LOG"
    print_color $PURPLE "======================================================"
}

# 功能：清理構建環境
cleanup_build() {
    if [ "${1:-}" = "--full" ]; then
        print_color $YELLOW "🧹 執行完整清理 Performing full cleanup..."
        rm -rf "$BUILD_DIR" "$DIST_DIR" "$DOCS_DIR"
        rm -f build_*.log
        print_color $GREEN "✅ 完整清理完成 Full cleanup completed"
    else
        print_color $YELLOW "🧹 執行標準清理 Performing standard cleanup..."
        rm -rf "$BUILD_DIR/tmp" "$DIST_DIR/tmp"
        print_color $GREEN "✅ 標準清理完成 Standard cleanup completed"
    fi
}

# 功能：顯示幫助信息
show_help() {
    echo "文言標準庫構建系統 - Wenyan Standard Library Build System v2.0"
    echo ""
    echo "用法 Usage:"
    echo "  $0 [選項] [Options]"
    echo ""
    echo "選項 Options:"
    echo "  -h, --help              顯示此幫助信息 Show this help"
    echo "  -b, --build-only        僅構建，不運行測試 Build only, skip tests"
    echo "  -t, --test-only         僅運行測試 Run tests only"
    echo "  -d, --docs-only         僅生成文檔 Generate documentation only"
    echo "  -c, --clean             清理構建文件 Clean build files"
    echo "  --full-clean            完整清理所有文件 Full cleanup of all files"
    echo "  -v, --verbose           詳細輸出模式 Verbose output mode"
    echo "  --no-color              禁用顏色輸出 Disable colored output"
    echo ""
    echo "示例 Examples:"
    echo "  $0                      完整構建流程 Full build process"
    echo "  $0 -b                   僅構建庫文件 Build libraries only"
    echo "  $0 -t                   僅運行測試 Run tests only"
    echo "  $0 -d                   僅生成文檔 Generate docs only"
    echo "  $0 -c                   清理構建文件 Clean build files"
    echo ""
    echo "構建產物 Build Artifacts:"
    echo "  - build/                編譯後的文件 Compiled files"
    echo "  - dist/                 發布包 Distribution packages"
    echo "  - docs/generated/       生成的文檔 Generated documentation"
    echo "  - build_*.log           構建日誌 Build logs"
    echo ""
}

# 主函數
main() {
    # 記錄開始時間
    echo $(date +%s) > .build_start_time
    
    local build_only=false
    local test_only=false
    local docs_only=false
    local clean_only=false
    local full_clean=false
    local verbose=false
    
    # 解析命令行參數
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -b|--build-only)
                build_only=true
                shift
                ;;
            -t|--test-only)
                test_only=true
                shift
                ;;
            -d|--docs-only)
                docs_only=true
                shift
                ;;
            -c|--clean)
                clean_only=true
                shift
                ;;
            --full-clean)
                full_clean=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                set -x
                shift
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
            *)
                echo "未知選項: $1"
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 執行相應操作
    if [ "$clean_only" = true ] || [ "$full_clean" = true ]; then
        if [ "$full_clean" = true ]; then
            cleanup_build --full
        else
            cleanup_build
        fi
        exit 0
    fi
    
    show_banner
    
    if [ "$test_only" = true ]; then
        run_tests
    elif [ "$docs_only" = true ]; then
        init_build_env
        generate_documentation
    elif [ "$build_only" = true ]; then
        init_build_env
        build_all_libraries
        create_release_archive
    else
        # 完整構建流程
        init_build_env
        build_all_libraries
        run_tests
        generate_documentation
        create_release_archive
    fi
    
    show_build_summary
    
    # 清理臨時文件
    cleanup_build
    
    # 返回適當的退出代碼
    if [ $FAILED_BUILDS -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# 錯誤處理
trap 'echo "❌ 構建過程中發生錯誤 Error occurred during build process"; cleanup_build; exit 1' ERR

# 執行主函數
main "$@"