#!/usr/bin/env python3
"""
Test the normalize function behavior
"""
import ast


def normalize_answer(answer):
    """Normalize answer to handle different formats (list vs string)."""
    if isinstance(answer, str):
        try:
            return ast.literal_eval(answer)
        except:
            return answer
    return answer


# Test different formats
test_cases = [
    "[1, 3, 12, 0, 0]",  # With spaces (like our actual output)
    "[1,3,12,0,0]",  # Without spaces (like JSON)
    [1, 3, 12, 0, 0],  # Actual list
]

expected = [1, 3, 12, 0, 0]

print("Testing normalize_answer function:")
print("=" * 50)

for i, test in enumerate(test_cases):
    normalized = normalize_answer(test)
    matches = normalized == expected
    print(f"Test {i+1}: {repr(test)}")
    print(f"  Normalized: {repr(normalized)} (type: {type(normalized)})")
    print(f"  Expected: {repr(expected)} (type: {type(expected)})")
    print(f"  Match: {matches}")
    print()
