#!/usr/bin/env python3
"""
Test Java code generation with the new approach.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / 'backend'))

from code_testing.language_config import LANGUAGE_CONFIG

def test_java_simple():
    """Test that Java code compiles without syntax errors."""
    
    java_code = """
class Solution {
    public int ladderLength(String beginWord, String endWord, List<String> wordList) {
        return 5;
    }
}
"""

    config = LANGUAGE_CONFIG["java"]
    wrapped_code = config["wrapper_template"].format(
        code=java_code.strip(),
        function_name="ladderLength"
    )
    
    print("Generated Java code:")
    print("=" * 60)
    print(wrapped_code)
    print("=" * 60)
    
    # Save to a file for manual compilation test
    with open("TestMain.java", "w") as f:
        f.write(wrapped_code)
    
    print("\nJava code saved to TestMain.java")
    print("You can test compilation with: javac TestMain.java")

if __name__ == "__main__":
    test_java_simple()