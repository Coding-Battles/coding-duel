#!/usr/bin/env python3

import subprocess
import tempfile
import os


def test_simple_cpp():
    """Test a very basic C++ program to identify core compilation issue"""

    simple_code = """class Solution {
public:
    int add(int a, int b) {
        return a + b;
    }
};
"""

    # Test 1: Without any includes
    print("=== Testing C++ code WITHOUT includes ===")
    test_cpp_code(simple_code, "No includes test")

    # Test 2: With just cstddef
    code_with_cstddef = """#include <cstddef>
using namespace std;

class Solution {
public:
    int add(int a, int b) {
        return a + b;
    }
};
"""

    print("\n=== Testing C++ code WITH cstddef include ===")
    test_cpp_code(code_with_cstddef, "With cstddef test")

    # Test 3: With basic iostream
    code_with_iostream = """#include <iostream>
using namespace std;

class Solution {
public:
    int add(int a, int b) {
        return a + b;
    }
};
"""

    print("\n=== Testing C++ code WITH iostream include ===")
    test_cpp_code(code_with_iostream, "With iostream test")


def test_cpp_code(code, test_name):
    """Test a specific piece of C++ code"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".cpp", delete=False) as f:
        f.write(code)
        f.flush()

        try:
            # Try compilation
            result = subprocess.run(
                ["g++", "-std=c++17", "-c", f.name, "-o", f.name + ".o"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print(f"✅ {test_name}: COMPILED SUCCESSFULLY")
            else:
                print(f"❌ {test_name}: COMPILATION FAILED")
                print("STDERR:")
                print(result.stderr[:2000])  # Limit output

        except subprocess.TimeoutExpired:
            print(f"⏱️ {test_name}: COMPILATION TIMEOUT")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
        finally:
            # Cleanup
            try:
                os.unlink(f.name)
                if os.path.exists(f.name + ".o"):
                    os.unlink(f.name + ".o")
            except:
                pass


if __name__ == "__main__":
    test_simple_cpp()
