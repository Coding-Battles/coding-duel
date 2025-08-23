#include "userfunc.h"
#include <bits/stdc++.h>
using namespace std;

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
