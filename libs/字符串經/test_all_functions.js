// Comprehensive test suite for Wenyan String Library
// Author: Whisky, PR Worker

const stringLib = require('./字符串經_working.js');

function runTests() {
    console.log('=== Wenyan String Library Test Suite ===');
    console.log('Author: Whisky, PR Worker\n');
    
    let passed = 0;
    let total = 0;
    
    function test(name, actual, expected) {
        total++;
        if (actual === expected) {
            console.log(`✓ ${name}`);
            passed++;
        } else {
            console.log(`✗ ${name}: expected ${expected}, got ${actual}`);
        }
    }
    
    // Test 取字符串長度 (String length)
    test('取字符串長度("hello")', stringLib.取字符串長度("hello"), 5);
    test('取字符串長度("")', stringLib.取字符串長度(""), 0);
    test('取字符串長度("中文")', stringLib.取字符串長度("中文"), 2);
    
    // Test 拼接字符串 (String concatenation)
    test('拼接字符串("hello")("world")', stringLib.拼接字符串("hello")("world"), "helloworld");
    test('拼接字符串("")("test")', stringLib.拼接字符串("")("test"), "test");
    test('拼接字符串("中")("文")', stringLib.拼接字符串("中")("文"), "中文");
    
    // Test 比較字符串 (String comparison)
    test('比較字符串("abc")("abc")', stringLib.比較字符串("abc")("abc"), 0);
    test('比較字符串("a")("b")', stringLib.比較字符串("a")("b"), -1);
    test('比較字符串("b")("a")', stringLib.比較字符串("b")("a"), 1);
    
    // Test 字符串為空 (String is empty)
    test('字符串為空("")', stringLib.字符串為空(""), true);
    test('字符串為空("test")', stringLib.字符串為空("test"), false);
    
    // Test 取字符 (Get character)
    test('取字符("hello")(1)', stringLib.取字符("hello")(1), "h");
    test('取字符("hello")(5)', stringLib.取字符("hello")(5), "o");
    test('取字符("hello")(0)', stringLib.取字符("hello")(0), "");
    test('取字符("hello")(6)', stringLib.取字符("hello")(6), "");
    test('取字符("")(1)', stringLib.取字符("")(1), "");
    
    // Test 截取字符串 (Substring)
    test('截取字符串("hello")(1)(3)', stringLib.截取字符串("hello")(1)(3), "hel");
    test('截取字符串("hello")(2)(4)', stringLib.截取字符串("hello")(2)(4), "ell");
    test('截取字符串("hello")(1)(5)', stringLib.截取字符串("hello")(1)(5), "hello");
    test('截取字符串("hello")(3)(3)', stringLib.截取字符串("hello")(3)(3), "l");
    test('截取字符串("hello")(6)(8)', stringLib.截取字符串("hello")(6)(8), "");
    test('截取字符串("")(1)(1)', stringLib.截取字符串("")(1)(1), "");
    
    // Test 字符串包含 (String contains)
    test('字符串包含("hello")("ell")', stringLib.字符串包含("hello")("ell"), true);
    test('字符串包含("hello")("xyz")', stringLib.字符串包含("hello")("xyz"), false);
    test('字符串包含("hello")("")', stringLib.字符串包含("hello")(""), true);
    test('字符串包含("")("test")', stringLib.字符串包含("")("test"), false);
    test('字符串包含("hello")("hello")', stringLib.字符串包含("hello")("hello"), true);
    
    // Test 查找字符串位置 (Find string position)
    test('查找字符串位置("hello")("ell")', stringLib.查找字符串位置("hello")("ell"), 2);
    test('查找字符串位置("hello")("xyz")', stringLib.查找字符串位置("hello")("xyz"), 0);
    test('查找字符串位置("hello")("")', stringLib.查找字符串位置("hello")(""), 1);
    test('查找字符串位置("")("test")', stringLib.查找字符串位置("")("test"), 0);
    test('查找字符串位置("hello")("h")', stringLib.查找字符串位置("hello")("h"), 1);
    test('查找字符串位置("hello")("o")', stringLib.查找字符串位置("hello")("o"), 5);
    
    // Test 重複字符串 (Repeat string)
    test('重複字符串("hi")(3)', stringLib.重複字符串("hi")(3), "hihihi");
    test('重複字符串("hi")(1)', stringLib.重複字符串("hi")(1), "hi");
    test('重複字符串("hi")(0)', stringLib.重複字符串("hi")(0), "");
    test('重複字符串("")(5)', stringLib.重複字符串("")(5), "");
    
    // Test 去除前後空格 (Trim)
    test('去除前後空格("  hello  ")', stringLib.去除前後空格("  hello  "), "hello");
    test('去除前後空格("hello")', stringLib.去除前後空格("hello"), "hello");
    test('去除前後空格("  ")', stringLib.去除前後空格("  "), "");
    test('去除前後空格("")', stringLib.去除前後空格(""), "");
    
    // Test case conversion helpers
    test('是否小寫字母("a")', stringLib.是否小寫字母("a"), true);
    test('是否小寫字母("A")', stringLib.是否小寫字母("A"), false);
    test('是否小寫字母("1")', stringLib.是否小寫字母("1"), false);
    
    test('是否大寫字母("A")', stringLib.是否大寫字母("A"), true);
    test('是否大寫字母("a")', stringLib.是否大寫字母("a"), false);
    test('是否大寫字母("1")', stringLib.是否大寫字母("1"), false);
    
    test('轉為大寫字符("a")', stringLib.轉為大寫字符("a"), "A");
    test('轉為大寫字符("A")', stringLib.轉為大寫字符("A"), "A");
    test('轉為大寫字符("1")', stringLib.轉為大寫字符("1"), "1");
    
    test('轉為小寫字符("A")', stringLib.轉為小寫字符("A"), "a");
    test('轉為小寫字符("a")', stringLib.轉為小寫字符("a"), "a");
    test('轉為小寫字符("1")', stringLib.轉為小寫字符("1"), "1");
    
    // Test 字符串轉大寫 (String to uppercase)
    test('字符串轉大寫("hello")', stringLib.字符串轉大寫("hello"), "HELLO");
    test('字符串轉大寫("HeLLo")', stringLib.字符串轉大寫("HeLLo"), "HELLO");
    test('字符串轉大寫("")', stringLib.字符串轉大寫(""), "");
    test('字符串轉大寫("123")', stringLib.字符串轉大寫("123"), "123");
    
    // Test 字符串轉小寫 (String to lowercase)
    test('字符串轉小寫("HELLO")', stringLib.字符串轉小寫("HELLO"), "hello");
    test('字符串轉小寫("HeLLo")', stringLib.字符串轉小寫("HeLLo"), "hello");
    test('字符串轉小寫("")', stringLib.字符串轉小寫(""), "");
    test('字符串轉小寫("123")', stringLib.字符串轉小寫("123"), "123");
    
    // Summary
    console.log(`\n=== Test Results ===`);
    console.log(`Passed: ${passed}/${total}`);
    console.log(`Success Rate: ${((passed/total)*100).toFixed(1)}%`);
    
    if (passed === total) {
        console.log('🎉 All tests passed! String library is working correctly.');
        return true;
    } else {
        console.log('❌ Some tests failed. Please check the implementation.');
        return false;
    }
}

runTests();