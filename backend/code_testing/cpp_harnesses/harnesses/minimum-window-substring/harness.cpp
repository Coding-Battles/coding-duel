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

// TODO: Implement problem-specific parsing and main function for minimum-window-substring
// This is a placeholder harness - needs to be customized for the specific problem

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cout << "{\"result\": \"\", \"execution_time\": 0}" << endl;
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

        // Parse input: ["ADOBECODEBANC","ABC"]
        // Remove brackets and quotes
        if (actualInput.size() >= 2 && actualInput[0] == '[' && actualInput.back() == ']') {
            actualInput = actualInput.substr(1, actualInput.size() - 2);
        }
        
        // Find the two strings
        vector<string> parts;
        string current = "";
        bool inQuotes = false;
        
        for (int i = 0; i < actualInput.length(); i++) {
            char c = actualInput[i];
            if (c == '"') {
                inQuotes = !inQuotes;
            } else if (c == ',' && !inQuotes) {
                if (!current.empty()) {
                    parts.push_back(current);
                    current = "";
                }
            } else if (inQuotes) {
                current += c;
            }
        }
        if (!current.empty()) {
            parts.push_back(current);
        }
        
        if (parts.size() != 2) {
            throw runtime_error("Expected exactly 2 string parameters");
        }
        
        string s = parts[0];
        string t = parts[1];
        
        // Call the solution
        Solution solution;
        string result = solution.minWindow(s, t);
        
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        // Output as JSON string
        cout << "{\"result\": \"" << result << "\", \"execution_time\": " << duration.count() << "}" << endl;
        
    } catch (const exception& e) {
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        cout << "{\"result\": \"\", \"execution_time\": " << duration.count() << "}" << endl;
    }
    
    return 0;
}
