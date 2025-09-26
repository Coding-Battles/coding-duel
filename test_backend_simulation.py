#!/usr/bin/env python3

import subprocess
import tempfile
import os
import json


def test_backend_exact_simulation():
    """Test the exact same process as the backend does"""

    # Read the actual harness file
    harness_path = "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/code_testing/cpp_harnesses/harnesses/alien-dictionary/harness.cpp"

    with open(harness_path, "r") as f:
        harness_content = f.read()

    # User code without includes (realistic scenario)
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

    # Apply the EXACT same replacement as backend
    user_code_with_namespace = f"""// User solution code with namespace access
using namespace std;

{user_code}"""

    wrapped_code = harness_content.replace(
        '#include "userfunc.h"',
        user_code_with_namespace,
    )

    print("=== Testing exact backend simulation ===")
    print("Applied replacement:")
    print(
        "- Found '#include \"userfunc.h\"':", '#include "userfunc.h"' in harness_content
    )
    print("- Replacement successful:", '#include "userfunc.h"' not in wrapped_code)

    # Test input
    test_input = '{"words": ["wrt", "wrf", "er", "ett", "rftt"]}'

    # Create temporary files
    with tempfile.NamedTemporaryFile(mode="w", suffix=".cpp", delete=False) as cpp_file:
        cpp_file.write(wrapped_code)
        cpp_file.flush()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as input_file:
            input_file.write(test_input)
            input_file.flush()

            try:
                # Use docker exactly like backend
                docker_cmd = [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{cpp_file.name}:/tmp/solution.cpp:ro",
                    "-v",
                    f"{input_file.name}:/tmp/input.json:ro",
                    "frolvlad/alpine-gxx:latest",
                    "sh",
                    "-c",
                    """
                    cd /tmp &&
                    echo "=== Compiling ===" &&
                    g++ -std=c++17 -o solution solution.cpp &&
                    echo "=== Running ===" &&
                    timeout 10 ./solution < input.json
                    """,
                ]

                print("Running Docker command...")
                result = subprocess.run(
                    docker_cmd, capture_output=True, text=True, timeout=30
                )

                if result.returncode == 0:
                    print("✅ COMPILATION AND EXECUTION SUCCESSFUL")
                    print("Output:", result.stdout.strip())
                else:
                    print("❌ COMPILATION/EXECUTION FAILED")
                    if result.stderr:
                        print("STDERR:")
                        print(result.stderr[:2000])
                    if result.stdout:
                        print("STDOUT:")
                        print(result.stdout[:1000])

                    # Let's also debug the final code
                    print("\n=== DEBUGGING: First 50 lines of final code ===")
                    lines = wrapped_code.split("\n")
                    for i, line in enumerate(lines[:50], 1):
                        print(f"{i:2d}: {line}")

            except subprocess.TimeoutExpired:
                print("⏱️ EXECUTION TIMEOUT")
            except Exception as e:
                print(f"💥 ERROR: {e}")
            finally:
                # Cleanup
                try:
                    os.unlink(cpp_file.name)
                    os.unlink(input_file.name)
                except:
                    pass


if __name__ == "__main__":
    test_backend_exact_simulation()
