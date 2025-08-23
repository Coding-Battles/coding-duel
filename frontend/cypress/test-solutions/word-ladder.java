import java.util.*;

class Solution {
    public int ladderLength(String beginWord, String endWord, List<String> wordList) {
        if (!wordList.contains(endWord)) return 0;
        
        // Convert wordList to set for O(1) lookup
        Set<String> wordSet = new HashSet<>(wordList);
        
        // BFS queue: [current_word, transformation_count]
        Queue<String[]> queue = new LinkedList<>();
        queue.offer(new String[]{beginWord, "1"});
        Set<String> visited = new HashSet<>();
        visited.add(beginWord);
        
        while (!queue.isEmpty()) {
            String[] current = queue.poll();
            String currentWord = current[0];
            int count = Integer.parseInt(current[1]);
            
            if (currentWord.equals(endWord)) {
                return count;
            }
            
            // Try changing each character
            for (int i = 0; i < currentWord.length(); i++) {
                for (char c = 'a'; c <= 'z'; c++) {
                    if (c == currentWord.charAt(i)) continue;
                    
                    String newWord = currentWord.substring(0, i) + c + currentWord.substring(i + 1);
                    
                    if (wordSet.contains(newWord) && !visited.contains(newWord)) {
                        visited.add(newWord);
                        queue.offer(new String[]{newWord, String.valueOf(count + 1)});
                    }
                }
            }
        }
        
        return 0;
    }
}