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
    
    private static int[] parseIntArray(String json, String key) {
        // Find the array in JSON
        String pattern = "\"" + key + "\"\\s*:\\s*\\[(.*)\\]";
        Pattern p = Pattern.compile(pattern);
        Matcher m = p.matcher(json);
        if (!m.find()) return new int[0];
        
        String content = m.group(1).trim();
        if (content.isEmpty()) return new int[0];
        
        String[] elements = content.split(",");
        int[] result = new int[elements.length];
        for (int i = 0; i < elements.length; i++) {
            result[i] = Integer.parseInt(elements[i].trim());
        }
        
        return result;
    }
    
    public static void main(String[] args) {
        if (args.length < 3) {
            System.out.println("{\"result\":\"Missing arguments\",\"execution_time\":0}");
            return;
        }
        
        String inputJson = args[2];
        
        try {
            int[] nums = parseIntArray(inputJson, "nums");
            
            Solution solution = new Solution();
            List<List<Integer>> result = solution.threeSum(nums);
            
            // Format as JSON array of arrays
            System.out.print("{\"result\": [");
            for (int i = 0; i < result.size(); i++) {
                if (i > 0) System.out.print(",");
                System.out.print("[");
                for (int j = 0; j < result.get(i).size(); j++) {
                    if (j > 0) System.out.print(",");
                    System.out.print(result.get(i).get(j));
                }
                System.out.print("]");
            }
            System.out.println("], \"execution_time\": 0}");
            
        } catch (Exception e) {
            System.out.println("{\"result\": \"Error: " + e.getMessage().replace("\"", "\\\"") + "\", \"execution_time\": 0}");
        }
    }
}
