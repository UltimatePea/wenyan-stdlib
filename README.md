# Wenyan Standard Library Project

## Project Overview
This project aims to create a comprehensive standard library for the Wenyan programming language (文言文編程語言), ultimately building a complete ecosystem equivalent to Node.js and npm but written entirely in classical Chinese.

## Project Goals

### Phase 1: Core Standard Library (Current Phase)
- **String Library (字符串經)** - String manipulation functions
- **Array Library (列經)** - Array operations and transformations  
- **Math Library (算經)** - Mathematical operations and constants
- **Date/Time Library (曆經)** - Date and time handling
- **File System Library (檔經)** - File I/O operations
- **Network Library (網經)** - HTTP and network protocols
- **JSON Library (析經)** - JSON parsing and stringification
- **Regular Expression Library (律經)** - Pattern matching
- **Crypto Library (密經)** - Cryptographic functions
- **Stream Library (流經)** - Stream processing
- **Process Library (程經)** - Process and system operations
- **Event Library (事經)** - Event emitter patterns

### Phase 2: Package Management System
- **文包 (wenyan-bao)** - Package manager equivalent to npm
- Package registry for Wenyan modules
- Dependency resolution system
- Version management following semantic versioning
- Package.wy manifest format (similar to package.json)

### Phase 3: Build Tools and Utilities
- **文築 (wenyan-zhu)** - Build tool chain
- Module bundler for Wenyan applications
- Testing framework (測經)
- Linting and formatting tools
- Documentation generator

### Phase 4: Framework Ecosystem
- Web framework (similar to Express.js)
- Database connectors
- Template engines
- Middleware system
- CLI tools framework

## Technical Considerations

### Wenyan Language Specifics
- Wenyan uses 1-based indexing (not 0-based)
- Classical Chinese syntax with specific patterns:
  - `吾有一[類型]` - Variable declaration
  - `名之曰「[名]」` - Variable naming
  - `施「[函數]」於[參數]` - Function invocation
  - `夫「[變量]」之[屬性]` - Property access
  - `若[條件]者` - Conditional statements
  - `恆為是` - While loops
  - `乃得[值]` - Return statements

### Implementation Strategy
1. Pure Wenyan implementations where possible
2. JavaScript interop only when absolutely necessary
3. Follow classical Chinese naming conventions
4. Maintain consistency with existing Wenyan libraries
5. Comprehensive testing for all functions
6. Documentation in both Chinese and English

### Current Progress
- ✅ String library basic implementation
- 🔄 String library testing and refinement
- ⏳ Array library (next priority)
- ⏳ Math library
- ⏳ Other core libraries

### Development Guidelines
- Each library should be self-contained in a single `.wy` file
- Test files should be named `測試[庫名].wy`
- Examples should demonstrate idiomatic Wenyan usage
- API should feel natural to Chinese speakers while being functionally complete

### Long-term Vision
Create a fully-functional programming ecosystem in classical Chinese that:
- Preserves Chinese literary traditions in computing
- Provides a complete alternative to Western programming paradigms
- Enables full-stack development in Wenyan
- Builds a community around classical Chinese programming

## Commands to Remember
- Run tests: `wenyan 測試字符串經.wy`
- Check syntax: `wenyan -c [file].wy`

## Notes for Future Sessions
- Wenyan uses 1-based indexing, adjust all array/string operations accordingly
- The `夫「」之` syntax for property access doesn't work with computed indices
- Focus on pure Wenyan implementations to avoid JavaScript interop issues
- Test thoroughly with Chinese characters as they may behave differently than ASCII