#include "userfunc.h"
#include <bits/stdc++.h>
using namespace std;

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
            if(!cur.empty()) out.push_back(stoi(cur));
        }
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
        vector<int> height = parseIntArray(input_json, "height");
        
        Solution solution;
        int result = solution.trap(height);
        
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
