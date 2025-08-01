#include <iostream>
#include <string>
#include <vector>
#include <sstream>
using namespace std;

// Simple JSON parsing for testing
vector<int> parseArrayValue(const string& json, const string& key) {
    string searchKey = string(1, 34) + key + string(1, 34) + string(1, 58); // "key":
    size_t keyPos = json.find(searchKey);
    if (keyPos == string::npos) return {};
    
    size_t start = json.find("[", keyPos);
    if (start == string::npos) return {};
    
    start++; // Skip the [
    size_t end = json.find("]", start);
    string arrayStr = json.substr(start, end - start);
    
    vector<int> result;
    if (arrayStr.empty()) return result;
    
    // Simple parsing: split by comma and convert to int
    stringstream ss(arrayStr);
    string item;
    while (getline(ss, item, ',')) {
        // Remove whitespace
        item.erase(0, item.find_first_not_of(" \t"));
        item.erase(item.find_last_not_of(" \t") + 1);
        if (!item.empty()) {
            result.push_back(stoi(item));
        }
    }
    return result;
}

// User code starts here
class Solution {
public:
    int missingNumber(vector<int>& nums) {
        int n = nums.size();
        long expectedSum = (long)n * (n + 1) / 2;
        long actualSum = 0;
        for (int num : nums) {
            actualSum += num;
        }
        return (int)(expectedSum - actualSum);
    }
};
// User code ends here

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cout << "{\"result\": \"Missing arguments\", \"execution_time\": 0}" << endl;
        return 1;
    }
    
    string methodName = argv[1];
    string inputJson = argv[2];
    
    try {
        Solution sol;
        string result;
        
        // Method-specific dispatch for missingNumber
        if (methodName == "missingNumber") {
            vector<int> nums = parseArrayValue(inputJson, "nums");
            int methodResult = sol.missingNumber(nums);
            result = to_string(methodResult);
        } else {
            result = "\"Method " + methodName + " not supported\"";
        }
        
        // Output result in JSON format
        cout << "{\"result\": " << result << ", \"execution_time\": 0.01}" << endl;
        
    } catch (const exception& e) {
        cout << "{\"result\": \"" << e.what() << "\", \"execution_time\": 0.01}" << endl;
    }
    
    return 0;
}