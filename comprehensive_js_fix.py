#!/usr/bin/env python3
"""
Comprehensive Wenyan JavaScript Fixer
Author: Whisky, PR Worker

A comprehensive solution to fix all issues in Wenyan-generated JavaScript
"""

import re
import sys

def format_and_fix_js(js_content):
    """
    Format the JS properly and fix all issues
    """
    # First, format the semicolon-separated code into readable format
    statements = [s.strip() for s in js_content.split(';') if s.strip() and s.strip() != '\n']
    
    fixed_statements = []
    declared_vars = set()
    
    for i, stmt in enumerate(statements):
        if not stmt:
            continue
            
        # Handle variable declarations and redeclarations
        var_match = re.match(r'var\s+([^=]+)=(.+)', stmt)
        if var_match:
            var_name = var_match.group(1).strip()
            var_value = var_match.group(2).strip()
            
            if var_name in declared_vars:
                # Change to assignment instead of redeclaration
                stmt = f"{var_name}={var_value}"
            else:
                declared_vars.add(var_name)
        
        # Handle empty console.log() calls
        if stmt == 'console.log()':
            # Look for context to determine what to log
            context_var = None
            
            # Look backward for recent assignments or function calls
            for j in range(i-1, max(-1, i-5), -1):
                if j < 0 or j >= len(statements):
                    continue
                    
                prev_stmt = statements[j]
                
                # Check for variable assignment
                assign_match = re.match(r'([a-zA-Z_\u4e00-\u9fff][a-zA-Z0-9_\u4e00-\u9fff]*)=([^=]+)', prev_stmt)
                if assign_match:
                    context_var = assign_match.group(1)
                    break
                
                # Check for const assignment (function result)
                const_match = re.match(r'const\s+([^=]+)=(.+)', prev_stmt)
                if const_match:
                    context_var = const_match.group(1).strip()
                    break
            
            if context_var:
                stmt = f'console.log({context_var})'
            else:
                stmt = 'console.log("DEBUG: Output")'
        
        fixed_statements.append(stmt)
    
    return fixed_statements

def create_readable_js(statements):
    """
    Create properly formatted, readable JavaScript
    """
    js_lines = []
    
    for stmt in statements:
        # Add proper formatting for different statement types
        if stmt.startswith('var ') or stmt.startswith('const '):
            js_lines.append(stmt + ';')
        elif stmt.startswith('console.log'):
            js_lines.append(stmt + ';')
        elif '=' in stmt and not stmt.startswith('if'):
            js_lines.append(stmt + ';')
        elif stmt.startswith('if '):
            js_lines.append(stmt)
        elif stmt == 'return true' or stmt == 'return false' or stmt.startswith('return '):
            js_lines.append('    ' + stmt + ';')
        elif stmt == '}':
            js_lines.append(stmt + ';')
        else:
            js_lines.append(stmt + ';' if not stmt.endswith(';') else stmt)
    
    return '\n'.join(js_lines)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 comprehensive_js_fix.py input.js output.js")  
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_js = f.read()
        
        print(f"Processing {len(raw_js)} characters of JavaScript...")
        
        # Fix the JavaScript
        fixed_statements = format_and_fix_js(raw_js)
        formatted_js = create_readable_js(fixed_statements)
        
        # Write the result
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_js)
        
        print(f"✓ Fixed JavaScript written to {output_file}")
        print(f"Generated {len(fixed_statements)} statements")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)