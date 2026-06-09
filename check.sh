#!/usr/bin/env bash
# Strict Web Repository Validation Pipeline (HTML, CSS, JS)

set -e 
set -u 

echo "=========================================="
echo " Starting Strict Web Quality Checks..."
echo "=========================================="

# 1. Verify necessary Web Files exist
echo "[1/4] Checking required web files..."
REQUIRED_FILES=("index.html" "app.js" "style.css" "settings.js" "manifest.json" "sw.js")
for FILE in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$FILE" ]; then
        echo "❌ ERROR: Required file '$FILE' is missing."
        exit 1
    fi
done
echo "    All required web files exist."

# 2. Verify Internal Links in HTML
echo "[2/4] Validating internal file references in index.html..."
links=$(grep -oE '(href|src)="([^"#\?]+)"' index.html | cut -d'"' -f2)
for link in $links; do
    if [[ $link == http* ]] || [[ $link == \$\{* ]] || [[ $link == https* ]]; then continue; fi
    if [ ! -f "$link" ]; then
        echo "❌ ERROR: index.html references '$link', but the file does not exist."
        exit 1
    fi
done
echo "    All internal file links are valid."

# 3. CSS Validation Check
echo "[3/4] Validating CSS variables and syntax..."
open_brackets=$(grep -o "{" style.css | wc -l)
close_brackets=$(grep -o "}" style.css | wc -l)
if [ "$open_brackets" -ne "$close_brackets" ]; then
    echo "❌ ERROR: style.css has mismatched curly brackets (Open: $open_brackets, Close: $close_brackets)."
    exit 1
fi
echo "    CSS bracket matching is correct."

# 4. JavaScript Syntax Validation Check
echo "[4/4] Validating JavaScript Syntax..."
if command -v node &> /dev/null; then
    for JS_FILE in "app.js" "settings.js" "sw.js"; do
        node -c "$JS_FILE"
        echo "    $JS_FILE syntax is correct."
    done
else
    for JS_FILE in "app.js" "settings.js" "sw.js"; do
        if [ ! -s "$JS_FILE" ]; then
            echo "❌ ERROR: $JS_FILE is empty."
            exit 1
        fi
    done
    echo "    Node.js not installed. Performed basic file checks."
fi

echo "=========================================="
echo "🎉 ALL CHECKS PASSED. Ready for Deployment!"
echo "=========================================="