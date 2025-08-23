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
#include "userfunc.h"
using namespace std;

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

int main(int argc,char**argv){
    if(argc<3){ cout<<"{\"result\":\"Missing arguments\",\"execution_time\": 0}\n"; return 1; }
    string in=argv[2];
    auto nums=parseIntArray(in,"nums");
    int k=parseIntValue(in,"k");
    Solution sol;
    int res=sol.subarraySum(nums, k);
    cout<<"{\"result\": "<<res<<", \"execution_time\": 0}\n";
    return 0;
}
