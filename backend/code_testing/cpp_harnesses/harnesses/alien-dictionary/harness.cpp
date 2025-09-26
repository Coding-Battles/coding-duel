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

static inline vector<string> parseStringArray(const string& json, const string& key){
    string needle="\""+key+"\"";
    size_t k=json.find(needle);
    if(k==string::npos) return {};
    size_t b=json.find('[',k);
    if(b==string::npos) return {};
    size_t e=json.find(']',b);
    string s=json.substr(b+1,e-b-1);
    vector<string> out;
    size_t i=0;
    while(i<s.size()){
        size_t q1=s.find('\"',i);
        if(q1==string::npos) break;
        size_t q2=s.find('\"',q1+1);
        if(q2==string::npos) break;
        out.push_back(s.substr(q1+1,q2-q1-1));
        i=q2+1;
    }
    return out;
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
        vector<string> words = parseStringArray(input_json, "words");
        
        Solution solution;
        string result = solution.alienOrder(words);
        
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        cout << "{\"result\": \"" << result << "\", \"execution_time\": " << duration.count() << "}" << endl;
        
    } catch (const exception& e) {
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        cout << "{\"result\": \"" << e.what() << "\", \"execution_time\": " << duration.count() << "}" << endl;
    }
    
    return 0;
}
