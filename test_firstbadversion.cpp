#include <iostream>
using namespace std;

// Global isBadVersion API for first-bad-version problem
int globalBadVersion = 0;

bool isBadVersion(int version) {
    return version >= globalBadVersion;
}

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
}