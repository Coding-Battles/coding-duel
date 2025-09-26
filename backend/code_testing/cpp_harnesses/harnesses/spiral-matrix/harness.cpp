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

// Forward declaration
static inline vector<vector<int>> parseMatrixArray(const string& arrayStr);

static inline vector<vector<int>> parseMatrix(const string& json) {
    vector<vector<int>> matrix;
    
    // Look for "matrix": followed by the array
    size_t matrixPos = json.find("\"matrix\":");
    if (matrixPos == string::npos) {
        // If no "matrix" key, assume the whole input is the matrix
        size_t start = json.find("[[");
        if (start == string::npos) return matrix;
        
        size_t end = json.find("]]", start);
        if (end == string::npos) return matrix;
        
        string matrixStr = json.substr(start, end - start + 2);
        return parseMatrixArray(matrixStr);
    }
    
    // Find the array part after "matrix":
    size_t arrayStart = json.find("[[", matrixPos);
    if (arrayStart == string::npos) return matrix;
    
    size_t arrayEnd = json.find("]]", arrayStart);
    if (arrayEnd == string::npos) return matrix;
    
    string matrixStr = json.substr(arrayStart, arrayEnd - arrayStart + 2);
    return parseMatrixArray(matrixStr);
}

static inline vector<vector<int>> parseMatrixArray(const string& arrayStr) {
    vector<vector<int>> matrix;
    string input = arrayStr;
    
    // Remove outer brackets
    if (input.size() >= 2 && input[0] == '[' && input.back() == ']') {
        input = input.substr(1, input.size() - 2);
    }
    
    // Parse each row
    string current = "";
    int depth = 0;
    
    for (char c : input) {
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
                        // Trim whitespace
                        num.erase(0, num.find_first_not_of(" \t"));
                        num.erase(num.find_last_not_of(" \t") + 1);
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
        cout << "{\"result\": [], \"execution_time\": 0}" << endl;
        return 1;
    }

    string function_name = argv[1];
    string input_json = argv[2];

    auto start_time = chrono::high_resolution_clock::now();

    try {
        // The input might be wrapped in an "input" key, so let's handle both formats
        string matrixJson = input_json;
        
        // Check if input is wrapped in {"input": "..."}
        size_t inputKeyPos = input_json.find("\"input\":");
        if (inputKeyPos != string::npos) {
            // Extract the value part
            size_t valueStart = input_json.find("\"", inputKeyPos + 8);
            if (valueStart != string::npos) {
                valueStart++; // Skip the opening quote
                size_t valueEnd = input_json.rfind("\"");
                if (valueEnd != string::npos && valueEnd > valueStart) {
                    matrixJson = input_json.substr(valueStart, valueEnd - valueStart);
                    // Unescape the JSON
                    size_t pos = 0;
                    while ((pos = matrixJson.find("\\\"", pos)) != string::npos) {
                        matrixJson.replace(pos, 2, "\"");
                        pos += 1;
                    }
                }
            }
        }
        
        // Parse matrix from JSON
        vector<vector<int>> matrix = parseMatrix(matrixJson);
        
        Solution solution;
        vector<int> result = solution.spiralOrder(matrix);
        
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        // Format output as JSON object with result array
        cout << "{\"result\": [";
        for (size_t i = 0; i < result.size(); i++) {
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
