#!/bin/bash

# Find all .wy files that don't have author information
find . -name "*.wy" -type f | while read file; do
    if ! head -10 "$file" | grep -q "Author:"; then
        echo "$file"
    fi
done