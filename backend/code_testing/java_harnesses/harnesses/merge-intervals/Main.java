import java.util.*;
import java.util.regex.*;

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
    
    private static int[][] parseIntMatrix(String json, String key) {
        // Much simpler approach - find the key and extract the array content
        String searchKey = "\"" + key + "\":";
        int keyIndex = json.indexOf(searchKey);
        if (keyIndex == -1) return new int[0][0];
        
        int startBracket = json.indexOf("[", keyIndex);
        if (startBracket == -1) return new int[0][0];
        
        // Find the matching closing bracket by counting
        int bracketCount = 0;
        int endBracket = -1;
        for (int i = startBracket; i < json.length(); i++) {
            char c = json.charAt(i);
            if (c == '[') bracketCount++;
            else if (c == ']') {
                bracketCount--;
                if (bracketCount == 0) {
                    endBracket = i;
                    break;
                }
            }
        }
        
        if (endBracket == -1) return new int[0][0];
        
        String arrayStr = json.substring(startBracket + 1, endBracket);
        System.err.println("DEBUG: arrayStr = '" + arrayStr + "'");
        
        if (arrayStr.trim().isEmpty()) return new int[0][0];
        
        // Parse individual intervals like [1,3],[2,6],[8,10],[15,18]
        List<int[]> intervals = new ArrayList<>();
        int i = 0;
        while (i < arrayStr.length()) {
            // Find opening bracket
            while (i < arrayStr.length() && arrayStr.charAt(i) != '[') i++;
            if (i >= arrayStr.length()) break;
            
            int start = i + 1; // after [
            
            // Find closing bracket
            while (i < arrayStr.length() && arrayStr.charAt(i) != ']') i++;
            if (i >= arrayStr.length()) break;
            
            int end = i; // at ]
            
            // Extract numbers between brackets
            String intervalStr = arrayStr.substring(start, end);
            System.err.println("DEBUG: intervalStr = '" + intervalStr + "'");
            String[] parts = intervalStr.split(",");
            if (parts.length == 2) {
                int[] interval = {Integer.parseInt(parts[0].trim()), Integer.parseInt(parts[1].trim())};
                intervals.add(interval);
            }
            
            i++; // move past ]
        }
        
        System.err.println("DEBUG: Found " + intervals.size() + " intervals");
        return intervals.toArray(new int[0][]);
    }
    
    public static void main(String[] args) {
        if (args.length < 3) {
            System.out.println("{\"result\":\"Missing arguments\",\"execution_time\":0}");
            return;
        }
        
        String inputJson = args[2];
        
        try {
            int[][] intervals = parseIntMatrix(inputJson, "intervals");
            
            // DEBUG: Print what we parsed
            System.err.println("DEBUG: Parsed " + intervals.length + " intervals:");
            for (int i = 0; i < intervals.length; i++) {
                System.err.print("  [");
                for (int j = 0; j < intervals[i].length; j++) {
                    if (j > 0) System.err.print(",");
                    System.err.print(intervals[i][j]);
                }
                System.err.println("]");
            }
            
            Solution solution = new Solution();
            int[][] result = solution.merge(intervals);
            
            // Format as JSON array of arrays
            System.out.print("{\"result\": [");
            for (int i = 0; i < result.length; i++) {
                if (i > 0) System.out.print(",");
                System.out.print("[");
                for (int j = 0; j < result[i].length; j++) {
                    if (j > 0) System.out.print(",");
                    System.out.print(result[i][j]);
                }
                System.out.print("]");
            }
            System.out.println("], \"execution_time\": 0}");
            
        } catch (Exception e) {
            System.out.println("{\"result\": \"Error: " + e.getMessage().replace("\"", "\\\"") + "\", \"execution_time\": 0}");
        }
    }
}
