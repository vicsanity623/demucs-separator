#!/bin/bash

echo "====================================="
echo "   Starting Idle Pal RPG Check...    "
echo "====================================="

# Fix: Added spaces between array elements
FILES=(
    "index.html"
    "train_headless.py"
)

ERRORS=0

for file in "${FILES[@]}"; do
    # -f checks if it is a regular file
    if [ -f "$file" ]; then
        # -s checks if file size is greater than 0
        if [ -s "$file" ]; then
            echo "✅ OK: $file found and contains data."
        else
            echo "❌ ERROR: $file exists but is completely EMPTY!"
            ERRORS=1
        fi
    else
        echo "❌ ERROR: Missing required file: $file"
        ERRORS=1
    fi
done

echo "====================================="
if [ $ERRORS -eq 1 ]; then
    echo "💥 Check Failed! Please fix the errors above."
    exit 1
else
    echo "🎉 All PWA Game files are present and valid. Check Passed!"
    exit 0
fi
