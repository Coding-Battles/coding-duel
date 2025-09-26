#!/usr/bin/env python3

import subprocess
import tempfile
import os
import json


def test_docker_cpp_compilation():
    """Test C++ compilation using the same Docker environment as the backend"""

    # Test user code without includes (realistic user scenario)
    user_code = """class Solution {
public:
    string alienOrder(vector<string>& words) {
        unordered_set<string> chars;
        unordered_map<char, unordered_set<char>> graph;
        unordered_map<char, int> indegree;
        
        for (const string& word : words) {
            for (char c : word) {
                chars.insert(string(1, c));
                indegree[c] = 0;
            }
        }
        
        for (int i = 0; i < words.size() - 1; i++) {
            string word1 = words[i];
            string word2 = words[i + 1];
            
            if (word1.length() > word2.length() && word1.substr(0, word2.length()) == word2) {
                return "";
            }
            
            for (int j = 0; j < min(word1.length(), word2.length()); j++) {
                if (word1[j] != word2[j]) {
                    if (graph[word1[j]].find(word2[j]) == graph[word1[j]].end()) {
                        graph[word1[j]].insert(word2[j]);
                        indegree[word2[j]]++;
                    }
                    break;
                }
            }
        }
        
        queue<char> q;
        for (auto& pair : indegree) {
            if (pair.second == 0) {
                q.push(pair.first);
            }
        }
        
        string result = "";
        while (!q.empty()) {
            char c = q.front();
            q.pop();
            result += c;
            
            for (char neighbor : graph[c]) {
                indegree[neighbor]--;
                if (indegree[neighbor] == 0) {
                    q.push(neighbor);
                }
            }
        }
        
        return result.length() == chars.size() ? result : "";
    }
};"""

    # Test input
    test_input = {"words": ["wrt", "wrf", "er", "ett", "rftt"]}

    print("=== Testing C++ compilation in Docker (same as backend) ===")

    # Create temporary files
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cpp", delete=False
    ) as user_file:
        user_file.write(user_code)
        user_file.flush()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as input_file:
            json.dump(test_input, input_file)
            input_file.flush()

            try:
                # Use docker to test compilation (same as backend)
                docker_cmd = [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{user_file.name}:/tmp/solution.cpp:ro",
                    "-v",
                    f"{input_file.name}:/tmp/input.json:ro",
                    "-v",
                    "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/code_testing/cpp_harnesses/harnesses/alien-dictionary:/tmp/harness:ro",
                    "frolvlad/alpine-gxx:latest",
                    "sh",
                    "-c",
                    """
                    cd /tmp &&
                    cp harness/harness.cpp solution_final.cpp &&
                    sed -i "s|#include \\"userfunc.h\\"|$(cat /tmp/solution.cpp; echo; echo "using namespace std;")|g" solution_final.cpp &&
                    echo "=== Final code ===" &&
                    cat solution_final.cpp &&
                    echo "=== Compiling ===" &&
                    g++ -std=c++17 -o solution solution_final.cpp &&
                    echo "=== Running ===" &&
                    ./solution < /tmp/input.json
                    """,
                ]

                print("Running Docker command...")
                result = subprocess.run(
                    docker_cmd, capture_output=True, text=True, timeout=30
                )

                if result.returncode == 0:
                    print("✅ DOCKER COMPILATION AND EXECUTION SUCCESSFUL")
                    print("Output:", result.stdout.strip())
                else:
                    print("❌ DOCKER COMPILATION/EXECUTION FAILED")
                    print("STDERR:", result.stderr)
                    print("STDOUT:", result.stdout)

            except subprocess.TimeoutExpired:
                print("⏱️ DOCKER EXECUTION TIMEOUT")
            except Exception as e:
                print(f"💥 DOCKER ERROR: {e}")
            finally:
                # Cleanup
                try:
                    os.unlink(user_file.name)
                    os.unlink(input_file.name)
                except:
                    pass


if __name__ == "__main__":
    test_docker_cpp_compilation()
