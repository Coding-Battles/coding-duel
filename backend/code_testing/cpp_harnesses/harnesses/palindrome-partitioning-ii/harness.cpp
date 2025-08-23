#include "userfunc.h"
#include <bits/stdc++.h>
using namespace std;

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

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cout << "{\"result\": \"Missing arguments\", \"execution_time\": 0}" << endl;
        return 1;
    }

    string function_name = argv[1];
    string input_json = argv[2];

    auto start_time = chrono::high_resolution_clock::now();
    
    try {
        string s = parseStringValue(input_json, "s");
        
        Solution solution;
        int result = solution.minCut(s);
        
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
