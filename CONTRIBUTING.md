# 貢獻指南 - Contributing Guidelines

**Author: Whisky, PR Worker**

## 項目結構 Project Structure

### 庫實現 Library Implementation
- 所有庫文件位於 `libs/[庫名]/` 目錄
- 主要庫文件命名為 `[庫名]經.wy`
- 遵循 `libs/庫文件命名規範.md` 中的命名規範

### 測試要求 Testing Requirements
- 所有庫必須有對應測試文件
- 測試文件位於 `tests/[庫名]/` 目錄
- 遵循 `tests/測試文件規範.md` 中的測試規範

### 示例文件 Examples
- 每個庫應提供使用示例
- 示例文件位於 `examples/[庫名]/` 目錄
- 示例應展示慣用的文言文編程方式

## 開發流程 Development Workflow

1. **創建分支**: 為每個功能創建獨立分支
2. **實現功能**: 遵循項目命名和結構規範
3. **測試**: 確保所有測試通過
4. **文檔**: 更新相關文檔和示例
5. **提交PR**: 創建Pull Request進行代碼審查

## 代碼規範 Code Standards

### 文言文語法
- 使用1基索引（非0基）
- 遵循古典中文語法模式
- 變量聲明：`吾有一[類型]`
- 變量命名：`名之曰「[名]」`
- 函數調用：`施「[函數]」於[參數]`

### 命名規範
- 使用有意義的中文名稱
- 保持與現有庫的一致性
- 函數名應清楚表達功能

## 質量要求 Quality Requirements

- 所有公共函數必須有測試覆蓋
- 代碼必須能通過 `wenyan` 編譯器檢查
- 遵循項目的文檔標準
- 考慮中文字符的特殊處理需求