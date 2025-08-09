class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: list[str]) -> int:
        if endWord not in wordList:
            return 0
        
        from collections import deque
        
        # Convert wordList to set for O(1) lookup
        word_set = set(wordList)
        
        # BFS queue: (current_word, transformation_count)
        queue = deque([(beginWord, 1)])
        visited = {beginWord}
        
        while queue:
            current_word, count = queue.popleft()
            
            if current_word == endWord:
                return count
            
            # Try changing each character
            for i in range(len(current_word)):
                for c in 'abcdefghijklmnopqrstuvwxyz':
                    if c == current_word[i]:
                        continue
                    
                    new_word = current_word[:i] + c + current_word[i+1:]
                    
                    if new_word in word_set and new_word not in visited:
                        visited.add(new_word)
                        queue.append((new_word, count + 1))
        
        return 0