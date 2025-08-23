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

static inline string vectorToJsonArray(const vector<string>& vec) {
    string result = "[";
    for (size_t i = 0; i < vec.size(); ++i) {
        if (i > 0) result += ",";
        result += "\"" + vec[i] + "\"";
    }
    result += "]";
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
        string s = parseStringValue(input_json, "s");
        vector<string> wordDict = parseStringArray(input_json, "wordDict");
        
        Solution solution;
        vector<string> result = solution.wordBreak(s, wordDict);
        
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        cout << "{\"result\": " << vectorToJsonArray(result) << ", \"execution_time\": " << duration.count() << "}" << endl;
        
    } catch (const exception& e) {
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        cout << "{\"result\": \"" << e.what() << "\", \"execution_time\": " << duration.count() << "}" << endl;
    }
    
    return 0;
}
