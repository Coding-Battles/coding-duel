#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <cstdlib>
#include "userfunc.h"
using namespace std;

vector<int> parseIntArray(const string& str) {
    vector<int> result;
    if (str.empty() || str == "[]") return result;
    
    string clean = str;
    // Remove brackets and spaces
    size_t start = clean.find('[');
    size_t end = clean.find(']');
    if (start != string::npos && end != string::npos) {
        clean = clean.substr(start + 1, end - start - 1);
    }
    
    stringstream ss(clean);
    string token;
    while (getline(ss, token, ',')) {
        // Trim whitespace
        size_t first = token.find_first_not_of(" \t");
        if (first != string::npos) {
            size_t last = token.find_last_not_of(" \t");
            token = token.substr(first, last - first + 1);
            result.push_back(stoi(token));
        }
    }
    return result;
}

int main() {
    string json_input;
    getline(cin, json_input);
    
    // Parse JSON manually to extract coins array and amount
    size_t coins_start = json_input.find("\"coins\":");
    if (coins_start == string::npos) {
        cerr << "Error: 'coins' not found in input" << endl;
        return 1;
    }
    
    // Find the start of the array
    size_t bracket_start = json_input.find('[', coins_start);
    if (bracket_start == string::npos) {
        cerr << "Error: coins array not found" << endl;
        return 1;
    }
    
    // Find the end of the array
    size_t bracket_end = json_input.find(']', bracket_start);
    if (bracket_end == string::npos) {
        cerr << "Error: coins array end not found" << endl;
        return 1;
    }
    
    string coins_str = json_input.substr(bracket_start, bracket_end - bracket_start + 1);
    vector<int> coins = parseIntArray(coins_str);
    
    // Parse amount
    size_t amount_start = json_input.find("\"amount\":");
    if (amount_start == string::npos) {
        cerr << "Error: 'amount' not found in input" << endl;
        return 1;
    }
    
    // Find the number after "amount":
    size_t colon_pos = json_input.find(':', amount_start);
    if (colon_pos == string::npos) {
        cerr << "Error: amount value not found" << endl;
        return 1;
    }
    
    // Skip whitespace and find the number
    size_t num_start = colon_pos + 1;
    while (num_start < json_input.size() && (json_input[num_start] == ' ' || json_input[num_start] == '\t')) {
        num_start++;
    }
    
    // Find end of number (comma, brace, or end)
    size_t num_end = num_start;
    while (num_end < json_input.size() && 
           json_input[num_end] != ',' && 
           json_input[num_end] != '}' && 
           json_input[num_end] != ' ' &&
           json_input[num_end] != '\t') {
        num_end++;
    }
    
    string amount_str = json_input.substr(num_start, num_end - num_start);
    int amount = stoi(amount_str);
    
    // Call user function
    int result = coinChange(coins, amount);
    
    // Output result
    cout << result << endl;
    
    return 0;
}
