#!/usr/bin/env python3
"""
Debug script to understand f-string escaping behavior
"""


def test_escaping():
    key = "testKey"

    print("=== Testing different escaping approaches ===")

    # Current (broken) approach
    current = f'String pattern = "\\\\"" + {key} + "\\\\"\\\\s*:\\\\s*(-?\\\\d+)";'
    print(f"Current: {current}")

    # What we want in Java output:
    target = 'String pattern = "\\"" + testKey + "\\"\\\\s*:\\\\s*(-?\\\\d+)";'
    print(f"Target:  {target}")

    # Test various escaping levels
    test1 = f'String pattern = "\\"" + {key} + "\\"\\s*:\\s*(-?\\d+)";'
    print(f"Test1:   {test1}")

    test2 = f'String pattern = "\\\\"" + {key} + "\\\\"\\\\s*:\\\\s*(-?\\\\d+)";'
    print(f"Test2:   {test2}")

    # Try with raw strings
    test3 = rf'String pattern = "\"" + {key} + "\"\\s*:\\s*(-?\\d+)";'
    print(f"Test3:   {test3}")

    print("\n=== Analysis ===")
    print("Target should have:")
    print('- "\\"" (escaped quote in Java)')
    print('- "\\\\s" (escaped backslash-s for regex in Java)')


if __name__ == "__main__":
    test_escaping()
