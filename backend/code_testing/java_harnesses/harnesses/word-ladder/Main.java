import java.util.*;
import java.util.regex.*;

// Standard LeetCode data structures
class ListNode {
    int val;
    ListNode next;
    ListNode() {}
    ListNode(int val) { this.val = val; }
    ListNode(int val, ListNode next) { this.val = val; this.next = next; }
}

class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
    TreeNode() {}
    TreeNode(int val) { this.val = val; }
    TreeNode(int val, TreeNode left, TreeNode right) {
        this.val = val;
        this.left = left;
        this.right = right;
    }
}

// USER_CODE_PLACEHOLDER

class HarnessMain {
    
    // JSON parsing utilities
    private static String parseStringValue(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\"([^\"]+)\"";
        Pattern p = Pattern.compile(pattern);
        Matcher m = p.matcher(json);
        if (m.find()) {
            return m.group(1);
        }
        throw new RuntimeException("Could not find key: " + key);
    }
    
    private static List<String> parseStringArray(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]+)\\]";
        Pattern p = Pattern.compile(pattern);
        Matcher m = p.matcher(json);
        if (m.find()) {
            String arrayContent = m.group(1);
            List<String> result = new ArrayList<>();
            if (arrayContent.trim().isEmpty()) {
                return result;
            }
            String[] elements = arrayContent.split(",");
            for (String element : elements) {
                String cleaned = element.trim().replaceAll("^\"|\"$", "");
                result.add(cleaned);
            }
            return result;
        }
        return new ArrayList<>();
    }
    
    public static void main(String[] args) {
        if (args.length < 3) {
            System.out.println("{\"result\":\"Missing arguments\",\"execution_time\":0}");
            return;
        }
        
        String inputJson = args[2];
        
        try {
            // Parse input specific to word-ladder problem
            String beginWord = parseStringValue(inputJson, "beginWord");
            String endWord = parseStringValue(inputJson, "endWord");
            List<String> wordList = parseStringArray(inputJson, "wordList");
            
            // Execute user solution
            Solution sol = new Solution();
            int result = sol.ladderLength(beginWord, endWord, wordList);
            
            // Format output
            System.out.println("{\"result\": " + result + ", \"execution_time\": 0}");
            
        } catch (Exception e) {
            System.out.println("{\"result\": \"Error: " + e.getMessage().replace("\"", "\\\"") + "\", \"execution_time\": 0}");
        }
    }
}