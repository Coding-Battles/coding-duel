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

static inline int parseIntValue(const string& json, const string& key){
    string needle="\""+key+"\"";
    size_t k=json.find(needle);
    if(k==string::npos) return 0;
    size_t c=json.find(':',k);
    if(c==string::npos) return 0;
    ++c; while(c<json.size() && isspace((unsigned char)json[c])) ++c;
    bool neg=false; if(c<json.size() && json[c]=='-'){neg=true; ++c;}
    long long v=0; while(c<json.size() && isdigit((unsigned char)json[c])){v=v*10+(json[c]-'0'); ++c;}
    return (int)(neg?-v:v);
}

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

static inline vector<int> parseIntArray(const string& json, const string& key){
    string needle="\""+key+"\"";
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

static inline vector<vector<int>> parse2DIntArray(const string& json, const string& key){
    string needle="\""+key+"\"";
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

// Converters
static inline ListNode* vecToList(const vector<int>& v){
    ListNode* head=nullptr; ListNode* cur=nullptr;
    for(int x: v){
        if(!head){ head=new ListNode(x); cur=head; }
        else{ cur->next=new ListNode(x); cur=cur->next; }
    }
    return head;
}
static inline vector<int> listToVec(ListNode* n){
    vector<int> v; while(n){ v.push_back(n->val); n=n->next; } return v;
}

static inline TreeNode* vecToTree(const vector<int>& v){
    if(v.empty() || v[0]==INT_MIN) return nullptr;
    vector<TreeNode*> nodes(v.size(), nullptr);
    for(size_t i=0;i<v.size();++i){
        if(v[i]!=INT_MIN) nodes[i]=new TreeNode(v[i]);
    }
    for(size_t i=0, pos=1;i<v.size() && pos<v.size();++i){
        if(!nodes[i]) continue;
        if(pos<v.size()) nodes[i]->left = nodes[pos++];
        if(pos<v.size()) nodes[i]->right= nodes[pos++];
    }
    return nodes[0];
}
static inline string vecToStr(const vector<int>& a){
    string s="["; for(size_t i=0;i<a.size();++i){ s+=to_string(a[i]); if(i+1<a.size()) s+=','; } s+=']'; return s;
}
static inline string vec2DToStr(const vector<vector<int>>& a){
    string s="["; for(size_t i=0;i<a.size();++i){ s+=vecToStr(a[i]); if(i+1<a.size()) s+=','; } s+=']'; return s;
}
static inline string vecStrToStr(const vector<string>& a){
    string s="["; for(size_t i=0;i<a.size();++i){ s+='\"'+a[i]+'\"'; if(i+1<a.size()) s+=','; } s+=']'; return s;
}

int main(int argc,char**argv){
    if(argc<3){ cout<<"{\"result\":\"Missing arguments\",\"execution_time\": 0}\n"; return 1; }
    string in=argv[2];
    auto p=parseIntArray(in,"p");
    auto q=parseIntArray(in,"q");
    Solution sol;
    bool res=sol.isSameTree(vecToTree(p), vecToTree(q));
    cout<<"{\"result\": "<<(res?"true":"false")<<", \"execution_time\": 0}\n";
    return 0;
}