#!/bin/bash

# Script to fix all Jackson-based harnesses to use proper regex parsing and JSON output

HARNESSES_DIR="/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/code_testing/java_harnesses/harnesses"

cd "$HARNESSES_DIR"

# List of harnesses that need fixing (those using Jackson)
BROKEN_HARNESSES=$(find . -name "Main.java" -exec grep -l "com.fasterxml.jackson" {} \; | sed 's|./||' | sed 's|/Main.java||')

echo "Found broken harnesses:"
echo "$BROKEN_HARNESSES"

for harness in $BROKEN_HARNESSES; do
    echo "Fixing $harness..."
    
    # Check if directory exists
    if [ -d "$harness" ]; then
        # Create a backup
        cp "$harness/Main.java" "$harness/Main.java.bak"
        
        # Remove Jackson imports and replace with regex imports
        sed -i '' 's/import java.io.IOException;//g' "$harness/Main.java"
        sed -i '' 's/import com.fasterxml.jackson.databind.JsonNode;//g' "$harness/Main.java"
        sed -i '' 's/import com.fasterxml.jackson.databind.ObjectMapper;//g' "$harness/Main.java"
        sed -i '' '1i\
import java.util.regex.*;' "$harness/Main.java"
        
        echo "  - Removed Jackson imports and added regex imports for $harness"
    else
        echo "  - Directory $harness does not exist, skipping"
    fi
done

echo "Basic fixes applied. Manual JSON output format fixes still needed."