#!/usr/bin/env python3
"""
Enhanced Wenyan JavaScript Post-Processor
Author: Whisky, PR Worker

Enhanced version that analyzes context to fix console.log calls properly
"""

import sys
import re

def analyze_and_fix_console_logs(js_content):
    """
    Analyze the JavaScript to understand what should be logged
    """
    # Split into statements
    statements = [s.strip() for s in js_content.split(';') if s.strip()]
    fixed_statements = []
    
    i = 0
    while i < len(statements):
        stmt = statements[i]
        
        # If we find console.log(), look at previous statement for context
        if stmt == 'console.log()':
            if i > 0:
                prev_stmt = statements[i-1]
                
                # Case 1: Variable assignment just before console.log
                var_assignment = re.match(r'([a-zA-Z_\u4e00-\u9fff][a-zA-Z0-9_\u4e00-\u9fff]*)=(.+)', prev_stmt)
                if var_assignment:
                    var_name = var_assignment.group(1)
                    fixed_statements.append(f'console.log({var_name})')
                    i += 1
                    continue
                
                # Case 2: Function call result assignment
                func_call = re.match(r'const\s+([^=]+)=(.+)', prev_stmt)
                if func_call:
                    var_name = func_call.group(1).strip()
                    fixed_statements.append(f'console.log({var_name})')
                    i += 1
                    continue
            
            # Default case: add debug message
            fixed_statements.append('console.log("DEBUG: Output called")')
        else:
            fixed_statements.append(stmt)
        
        i += 1
    
    return ';'.join(fixed_statements)

def fix_string_literals(js_content):
    """
    Fix string literal issues in assignments
    """
    # Look for patterns like: var=Hello World -> var="Hello World"
    js_content = re.sub(r'([a-zA-Z_\u4e00-\u9fff][a-zA-Z0-9_\u4e00-\u9fff]*)=([A-Za-z][A-Za-z0-9\s]+)([;\s])', 
                       r'\1="\2"\3', js_content)
    
    return js_content

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 enhanced_fix_wenyan_js.py input.js output.js")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_js = f.read()
        
        print(f"Original JS: {repr(input_js)}")
        
        # Apply fixes
        fixed_js = input_js
        fixed_js = analyze_and_fix_console_logs(fixed_js)
        fixed_js = fix_string_literals(fixed_js)
        
        print(f"Fixed JS: {repr(fixed_js)}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_js)
        
        print(f"✓ Enhanced JavaScript fix applied to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()