// Comprehensive standard library includes for portability
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <map>
#include <set>
#include <queue>
#include <stack>
#include <deque>
#include <list>
#include <algorithm>
#include <numeric>
#include <climits>
#include <cmath>
#include <sstream>
#include <utility>
#include <chrono>
#include <functional>
#include <iomanip>
#include <bitset>
#include <array>
#include <memory>
#include <iterator>
#include <random>
using namespace std;

// Standard LeetCode data structures
struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};

struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};

#include "userfunc.h"

// TODO: Implement problem-specific parsing and main function for sliding-window-maximum
// This is a placeholder harness - needs to be customized for the specific problem

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cout << "{\"result\": [], \"execution_time\": 0}" << endl;
        return 1;
    }

    string function_name = argv[1];
    string input_json = argv[2];

    auto start_time = chrono::high_resolution_clock::now();

    try {
        // Handle wrapped input format
        string actualInput = input_json;
        size_t inputKeyPos = input_json.find("\"input\":");
        if (inputKeyPos != string::npos) {
            size_t valueStart = input_json.find("\"", inputKeyPos + 8);
            if (valueStart != string::npos) {
                valueStart++;
                size_t valueEnd = input_json.rfind("\"");
                if (valueEnd != string::npos && valueEnd > valueStart) {
                    actualInput = input_json.substr(valueStart, valueEnd - valueStart);
                    // Unescape the JSON
                    size_t pos = 0;
                    while ((pos = actualInput.find("\\\"", pos)) != string::npos) {
                        actualInput.replace(pos, 2, "\"");
                        pos += 1;
                    }
                }
            }
        }

        // Parse input: [[1,3,-1,-3,5,3,6,7],3]
        // Find the array and k value
        vector<int> nums;
        int k = 0;
        
        // Remove outer brackets
        if (actualInput.size() >= 2 && actualInput[0] == '[' && actualInput.back() == ']') {
            actualInput = actualInput.substr(1, actualInput.size() - 2);
        }
        
        // Find the array part (first bracket pair)
        int arrayStart = actualInput.find('[');
        int arrayEnd = actualInput.find(']');
        
        if (arrayStart != string::npos && arrayEnd != string::npos) {
            string arrayStr = actualInput.substr(arrayStart + 1, arrayEnd - arrayStart - 1);
            
            // Parse array elements
            stringstream ss(arrayStr);
            string num;
            while (getline(ss, num, ',')) {
                if (!num.empty()) {
                    nums.push_back(stoi(num));
                }
            }
            
            // Parse k value (after the array)
            string remaining = actualInput.substr(arrayEnd + 1);
            size_t commaPos = remaining.find(',');
            if (commaPos != string::npos) {
                string kStr = remaining.substr(commaPos + 1);
                k = stoi(kStr);
            }
        }
        
        // Call the solution
        Solution solution;
        vector<int> result = solution.maxSlidingWindow(nums, k);
        
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        // Output as JSON array
        cout << "{\"result\": [";
        for (int i = 0; i < result.size(); i++) {
            if (i > 0) cout << ",";
            cout << result[i];
        }
        cout << "], \"execution_time\": " << duration.count() << "}" << endl;
        
    } catch (const exception& e) {
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        cout << "{\"result\": [], \"execution_time\": " << duration.count() << "}" << endl;
    }
    
    return 0;
}
