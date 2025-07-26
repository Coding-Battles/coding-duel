#!/usr/bin/env python3

# Simple test to verify C++ wrapper generation for firstBadVersion

def test_cpp_wrapper():
    # Simple C++ test code
    test_code = '''
class Solution {
public:
    int firstBadVersion(int n) {
        int left = 1, right = n;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (isBadVersion(mid)) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }
        return left;
    }
};
'''

    # Generate a simple C++ wrapper
    wrapper = '''#include <iostream>
using namespace std;

// Global isBadVersion API for first-bad-version problem
int globalBadVersion = 0;

bool isBadVersion(int version) {
    return version >= globalBadVersion;
}

''' + test_code + '''

int main() {
    // Test case: n=5, bad=4, expected=4
    globalBadVersion = 4;
    Solution sol;
    int result = sol.firstBadVersion(5);
    cout << "Result: " << result << " (expected: 4)" << endl;
    
    if (result == 4) {
        cout << "✅ Test PASSED" << endl;
    } else {
        cout << "❌ Test FAILED" << endl;
    }
    
    return 0;
}'''

    print("✅ C++ wrapper generated successfully")
    print("Key components verified:")
    print("- isBadVersion function:", "isBadVersion" in wrapper)
    print("- globalBadVersion usage:", "globalBadVersion = 4" in wrapper) 
    print("- firstBadVersion call:", "sol.firstBadVersion(5)" in wrapper)
    print()
    print("Generated C++ test code:")
    print("=" * 50)
    print(wrapper)
    return wrapper

if __name__ == "__main__":
    test_cpp_wrapper()