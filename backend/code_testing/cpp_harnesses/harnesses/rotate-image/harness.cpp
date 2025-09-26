#pragma once
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>
#include <climits>
#include <queue>
#include <map>
#include <set>
#include <unordered_map>
#include <unordered_set>
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

// Generic utility functions for parsing
static inline vector<vector<int>> parse2DIntArray(const string& json, const string& key){
    string needle="\""+key+"\":";
    size_t k=json.find(needle);
    if(k==string::npos) return {};
    size_t b=json.find('[',k);
    if(b==string::npos) return {};
    vector<vector<int>> out;
    size_t i=b+1; int depth=0; size_t start=i;
    while(i<json.size()){
        if(json[i]=='['){ if(depth==0) start=i; depth++; }
        else if(json[i]==']'){ depth--; if(depth==0){
            string inner=json.substr(start+1, i-start-1);
            vector<int> row; string cur; stringstream ss(inner);
            while(getline(ss,cur,',')){
                if(cur.size()){
                    cur.erase(0,cur.find_first_not_of(" \t"));
                    cur.erase(cur.find_last_not_of(" \t")+1);
                    if(cur.size()) row.push_back(stoi(cur));
                }
            }
            out.push_back(row);
        } if(depth<0) break;}
        else if(json[i]==']' && depth==0) break;
        i++;
        if(depth==0){
            size_t next = json.find('[', i);
            if(next==string::npos) break;
            i=next;
        }
    }
    return out;
}

static inline string vec2DToStr(const vector<vector<int>>& a){
    string s="["; 
    for(size_t i=0;i<a.size();++i){ 
        s+="[";
        for(size_t j=0;j<a[i].size();++j){
            s+=to_string(a[i][j]); 
            if(j+1<a[i].size()) s+=','; 
        }
        s+="]";
        if(i+1<a.size()) s+=','; 
    } 
    s+=']'; 
    return s;
}

int main(int argc,char**argv){
    if(argc<3){ cout<<"{\"result\":\"Missing arguments\",\"execution_time\": 0}\n"; return 1; }
    string in=argv[2];
    auto matrix=parse2DIntArray(in,"matrix");
    Solution sol;
    sol.rotate(matrix);  // void function modifies matrix in place
    cout<<"{\"result\": "<<vec2DToStr(matrix)<<", \"execution_time\": 0}\n";
    return 0;
}
