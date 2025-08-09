class Solution {
    ladderLength(beginWord, endWord, wordList) {
        if (!wordList.includes(endWord)) return 0;
        
        // Convert wordList to set for O(1) lookup
        const wordSet = new Set(wordList);
        
        // BFS queue: [current_word, transformation_count]
        const queue = [[beginWord, 1]];
        const visited = new Set([beginWord]);
        
        while (queue.length > 0) {
            const [currentWord, count] = queue.shift();
            
            if (currentWord === endWord) {
                return count;
            }
            
            // Try changing each character
            for (let i = 0; i < currentWord.length; i++) {
                for (let c = 0; c < 26; c++) {
                    const char = String.fromCharCode(97 + c); // 'a' to 'z'
                    if (char === currentWord[i]) continue;
                    
                    const newWord = currentWord.slice(0, i) + char + currentWord.slice(i + 1);
                    
                    if (wordSet.has(newWord) && !visited.has(newWord)) {
                        visited.add(newWord);
                        queue.push([newWord, count + 1]);
                    }
                }
            }
        }
        
        return 0;
    }
}