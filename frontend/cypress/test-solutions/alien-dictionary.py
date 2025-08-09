from collections import defaultdict, deque

class Solution:
    def alienOrder(self, words: list[str]) -> str:
        graph = defaultdict(set)
        in_degree = {char for word in words for char in word}
        
        for i in range(len(words) - 1):
            word1, word2 = words[i], words[i + 1]
            min_len = min(len(word1), len(word2))
            
            if len(word1) > len(word2) and word1[:min_len] == word2[:min_len]:
                return ""
            
            for j in range(min_len):
                if word1[j] != word2[j]:
                    if word2[j] not in graph[word1[j]]:
                        graph[word1[j]].add(word2[j])
                    break
        
        in_degree = {char: 0 for char in in_degree}
        for char in graph:
            for neighbor in graph[char]:
                in_degree[neighbor] += 1
        
        queue = deque([char for char in in_degree if in_degree[char] == 0])
        result = []
        
        while queue:
            char = queue.popleft()
            result.append(char)
            
            for neighbor in graph[char]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return "".join(result) if len(result) == len(in_degree) else ""