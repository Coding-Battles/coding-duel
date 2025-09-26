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

// TODO: Implement problem-specific parsing and main function for longest-increasing-path-in-a-matrix
// This is a placeholder harness - needs to be customized for the specific problem

// Helper function to parse matrix from string
vector<vector<int>> parseMatrix(const string& input) {
    vector<vector<int>> matrix;
    string cleanInput = input;
    
    // Remove outer brackets
    if (cleanInput.size() >= 2 && cleanInput[0] == '[' && cleanInput.back() == ']') {
        cleanInput = cleanInput.substr(1, cleanInput.size() - 2);
    }
    
    // Parse each row
    string current = "";
    int depth = 0;
    
    for (char c : cleanInput) {
        if (c == '[') {
            depth++;
            if (depth == 1) current = "";
        } else if (c == ']') {
            depth--;
            if (depth == 0) {
                // Parse the current row
                vector<int> row;
                if (!current.empty()) {
                    stringstream ss(current);
                    string num;
                    while (getline(ss, num, ',')) {
                        if (!num.empty()) {
                            row.push_back(stoi(num));
                        }
                    }
                }
                matrix.push_back(row);
                current = "";
            }
        } else if (c == ',' && depth == 0) {
            // Skip commas between rows
        } else if (depth > 0) {
            current += c;
        }
    }
    
    return matrix;
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cout << "{\"result\": 0, \"execution_time\": 0}" << endl;
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

        // Parse matrix: [[9,9,4],[6,6,8],[2,1,1]]
        vector<vector<int>> matrix = parseMatrix(actualInput);
        
        // Call the solution
        Solution solution;
        int result = solution.longestIncreasingPath(matrix);
        
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        // Output as JSON
        cout << "{\"result\": " << result << ", \"execution_time\": " << duration.count() << "}" << endl;
        
    } catch (const exception& e) {
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        cout << "{\"result\": 0, \"execution_time\": " << duration.count() << "}" << endl;
    }
    
    return 0;
}
