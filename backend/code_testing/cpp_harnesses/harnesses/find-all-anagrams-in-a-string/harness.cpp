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

#include "userfunc.h"

// TreeNode definition for binary tree problems
struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};

// ListNode definition for linked list problems
struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};

// Generic utility functions for parsing
static inline int parseIntValue(const string& json, const string& key){
    string needle="\""+key+"\":";
    size_t k=json.find(needle);
    if(k==string::npos) return 0;
    size_t start=k+needle.size();
    while(start<json.size() && (json[start]==' '||json[start]=='\t')) start++;
    size_t end=start;
    while(end<json.size() && json[end]!=','&&json[end]!='}') end++;
    return stoi(json.substr(start,end-start));
}

static inline string parseStringValue(const string& json, const string& key){
    string needle="\""+key+"\":";
    size_t k=json.find(needle);
    if(k==string::npos) return "";
    size_t start=json.find('\"',k+needle.size());
    if(start==string::npos) return "";
    start++;
    size_t end=json.find('\"',start);
    if(end==string::npos) return "";
    return json.substr(start,end-start);
}

static inline vector<int> parseIntArray(const string& json, const string& key){
    string needle="\""+key+"\":";
    size_t k=json.find(needle);
    if(k==string::npos) return {};
    size_t b=json.find('[',k);
    if(b==string::npos) return {};
    size_t e=json.find(']',b);
    string s=json.substr(b+1,e-b-1);
    vector<int> out; string cur; stringstream ss(s);
    while(getline(ss,cur,',')){
        if(cur.size()){
            cur.erase(0,cur.find_first_not_of(" \t"));
            cur.erase(cur.find_last_not_of(" \t")+1);
            if(cur=="null"){ out.push_back(INT_MIN); }
            else out.push_back(stoi(cur));
        }
    }
    return out;
}

static inline string vecToStr(const vector<int>& a){
    string s="["; for(size_t i=0;i<a.size();++i){ s+=to_string(a[i]); if(i+1<a.size()) s+=','; } s+=']'; return s;
}

int main(int argc,char**argv){
    if(argc<3){ cout<<"{\"result\":\"Missing arguments\",\"execution_time\": 0}\n"; return 1; }
    string in=argv[2];
    string s=parseStringValue(in,"s");
    string p=parseStringValue(in,"p");
    Solution sol;
    vector<int> res=sol.findAnagrams(s, p);
    cout<<"{\"result\": "<<vecToStr(res)<<", \"execution_time\": 0}\n";
    return 0;
}
