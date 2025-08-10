class Solution {
public:
    int ladderLength(string beginWord, string endWord, vector<string>& wordList) {
        unordered_set<string> wordSet(wordList.begin(), wordList.end());
        if (wordSet.find(endWord) == wordSet.end()) return 0;
        
        // BFS queue: pair<current_word, transformation_count>
        queue<pair<string, int>> q;
        q.push({beginWord, 1});
        unordered_set<string> visited;
        visited.insert(beginWord);
        
        while (!q.empty()) {
            auto [currentWord, count] = q.front();
            q.pop();
            
            if (currentWord == endWord) {
                return count;
            }
            
            // Try changing each character
            for (int i = 0; i < currentWord.length(); i++) {
                for (char c = 'a'; c <= 'z'; c++) {
                    if (c == currentWord[i]) continue;
                    
                    string newWord = currentWord;
                    newWord[i] = c;
                    
                    if (wordSet.find(newWord) != wordSet.end() && visited.find(newWord) == visited.end()) {
                        visited.insert(newWord);
                        q.push({newWord, count + 1});
                    }
                }
            }
        }
        
        return 0;
    }
};