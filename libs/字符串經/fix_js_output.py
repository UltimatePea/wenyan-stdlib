#!/usr/bin/env python3
"""
JavaScript Post-processor for Wenyan String Library
Author: Whisky, PR Worker

This script fixes JavaScript syntax issues in the compiled output from Wenyan.
Main issue: Consecutive variable assignments without proper semicolon separation.

Example fix:
var 庫信息="";庫信息="value"; → var 庫信息="value";
"""

import re
import sys

def fix_js_syntax(js_code):
    """Fix JavaScript syntax issues in compiled Wenyan output"""
    
    # First handle the global level var declarations followed by reassignments
    js_code = re.sub(r'var\s+([^=;]+)="";(\1)="([^"]*)"', r'var \1="\3"', js_code)
    js_code = re.sub(r'var\s+([^=;]+)=([^;]+);(\1)=([^;]+)', r'var \1=\4', js_code)
    
    # Handle function declarations that have empty arrow functions followed by real implementations
    js_code = re.sub(r'var\s+([^=;]+)=_=>\{\};(\1)=([^;]+)', r'var \1=\3', js_code)
    
    # Now handle patterns within functions where we have:
    # var 變量=初值;const _ans=...;var 變量=_ans;
    # This becomes: const _ans=...;var 變量=_ans;
    
    # Pattern to match the sequence: var name=value;const _ansN=...;var name=_ansN;
    pattern = r'var\s+([^=;]+)=([^;]+);(const\s+_ans\d+=([^;]+));var\s+\1=(_ans\d+)'
    
    def replacement(match):
        var_name = match.group(1)
        const_decl = match.group(3)  # const _ansN=...
        ans_var = match.group(5)     # _ansN
        return f'{const_decl};var {var_name}={ans_var}'
    
    js_code = re.sub(pattern, replacement, js_code)
    
    # Clean up multiple semicolons
    js_code = re.sub(r';;+', ';', js_code)
    
    return js_code

def main():
    """Main function to process JavaScript from stdin or file"""
    if len(sys.argv) > 1:
        # Read from file
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            js_code = f.read()
    else:
        # Read from stdin
        js_code = sys.stdin.read()
    
    # Fix the JavaScript syntax
    fixed_code = fix_js_syntax(js_code)
    
    # Output the fixed code
    print(fixed_code)

if __name__ == "__main__":
    main()