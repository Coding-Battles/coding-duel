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

static inline string parseStringValue(const string& json, const string& key){
    string needle="\""+key+"\"";
    size_t k=json.find(needle);
    if(k==string::npos) return "";
    size_t q1=json.find('\"', json.find(':',k));
    if(q1==string::npos) return "";
    size_t q2=json.find('\"', q1+1);
    if(q2==string::npos) return "";
    return json.substr(q1+1, q2-(q1+1));
}

static inline vector<string> parseStringArray(const string& json, const string& key){
    string needle="\""+key+"\"";
    size_t k=json.find(needle);
    if(k==string::npos) return {};
    size_t b1=json.find('[',k);
    if(b1==string::npos) return {};
    size_t b2=json.find(']',b1);
    if(b2==string::npos) return {};
    string arrayStr=json.substr(b1+1, b2-(b1+1));
    vector<string> result;
    size_t pos=0;
    while(pos<arrayStr.size()){
        while(pos<arrayStr.size() && (isspace((unsigned char)arrayStr[pos]) || arrayStr[pos]==',')) ++pos;
        if(pos>=arrayStr.size()) break;
        if(arrayStr[pos]=='\"'){
            size_t end=arrayStr.find('\"',pos+1);
            if(end==string::npos) break;
            result.push_back(arrayStr.substr(pos+1, end-(pos+1)));
            pos=end+1;
        } else {
            size_t end=pos;
            while(end<arrayStr.size() && arrayStr[end]!=',' && !isspace((unsigned char)arrayStr[end])) ++end;
            result.push_back(arrayStr.substr(pos, end-pos));
            pos=end;
        }
    }
    return result;
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cout << "{\"result\": \"Missing arguments\", \"execution_time\": 0}" << endl;
        return 1;
    }

    string function_name = argv[1];
    string input_json = argv[2];

    auto start_time = chrono::high_resolution_clock::now();
    
    try {
        string beginWord = parseStringValue(input_json, "beginWord");
        string endWord = parseStringValue(input_json, "endWord");
        vector<string> wordList = parseStringArray(input_json, "wordList");
        
        Solution solution;
        int result = solution.ladderLength(beginWord, endWord, wordList);
        
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        cout << "{\"result\": " << result << ", \"execution_time\": " << duration.count() << "}" << endl;
        
    } catch (const exception& e) {
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        cout << "{\"result\": \"" << e.what() << "\", \"execution_time\": " << duration.count() << "}" << endl;
    }
    
    return 0;
}
