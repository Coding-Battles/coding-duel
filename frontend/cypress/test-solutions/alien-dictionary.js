class Solution {
    alienOrder(words) {
        const graph = new Map();
        const inDegree = new Map();
        
        for (const word of words) {
            for (const char of word) {
                if (!graph.has(char)) {
                    graph.set(char, new Set());
                }
                if (!inDegree.has(char)) {
                    inDegree.set(char, 0);
                }
            }
        }
        
        for (let i = 0; i < words.length - 1; i++) {
            const word1 = words[i];
            const word2 = words[i + 1];
            const minLen = Math.min(word1.length, word2.length);
            
            if (word1.length > word2.length && word1.substring(0, minLen) === word2.substring(0, minLen)) {
                return "";
            }
            
            for (let j = 0; j < minLen; j++) {
                if (word1[j] !== word2[j]) {
                    if (!graph.get(word1[j]).has(word2[j])) {
                        graph.get(word1[j]).add(word2[j]);
                        inDegree.set(word2[j], inDegree.get(word2[j]) + 1);
                    }
                    break;
                }
            }
        }
        
        const queue = [];
        for (const [char, degree] of inDegree) {
            if (degree === 0) {
                queue.push(char);
            }
        }
        
        const result = [];
        while (queue.length > 0) {
            const char = queue.shift();
            result.push(char);
            
            for (const neighbor of graph.get(char)) {
                inDegree.set(neighbor, inDegree.get(neighbor) - 1);
                if (inDegree.get(neighbor) === 0) {
                    queue.push(neighbor);
                }
            }
        }
        
        return result.length === inDegree.size ? result.join('') : "";
    }
}