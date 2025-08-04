#!/bin/bash

# Fix missing author headers in all .wy files
# Author: Whisky, PR Worker

echo "Adding author headers to files missing them..."

find . -name "*.wy" -type f | while read -r file; do
    if ! head -10 "$file" | grep -q "Author:"; then
        echo "Adding header to: $file"
        
        # Check the first line to determine the comment style
        first_line=$(head -1 "$file")
        
        if [[ "$first_line" == /* ]]; then
            # File starts with /* comment
            sed -i '1a/* Author: Whisky, PR Worker */' "$file"
        elif [[ "$first_line" == 注曰* ]]; then
            # File starts with 注曰 comment
            sed -i '1a注曰「Author: Whisky, PR Worker」' "$file"
        elif [[ "$first_line" == "<!--"* ]]; then
            # File starts with HTML comment
            sed -i '1a<!-- Author: Whisky, PR Worker -->' "$file"
        else
            # File doesn't start with comment, add HTML comment at the top
            sed -i '1i<!-- Author: Whisky, PR Worker -->' "$file"
        fi
    fi
done

echo "Author header fix completed."