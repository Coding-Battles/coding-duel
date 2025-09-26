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
        String pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]+)\\]";
        Pattern p = Pattern.compile(pattern);
        Matcher m = p.matcher(json);
        if (m.find()) {
            String arrayContent = m.group(1);
            if (arrayContent.trim().isEmpty()) {
                return new int[0];
            }
            String[] elements = arrayContent.split(",");
            int[] result = new int[elements.length];
            for (int i = 0; i < elements.length; i++) {
                result[i] = Integer.parseInt(elements[i].trim());
            }
            return result;
        }
        return new int[0];
    }
    
    private static String vectorToString(int[] arr) {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        for (int i = 0; i < arr.length; i++) {
            if (i > 0) sb.append(",");
            sb.append(arr[i]);
        }
        sb.append("]");
        return sb.toString();
    }
    
    public static void main(String[] args) {
        if (args.length < 3) {
            System.out.println("{\"result\":\"Missing arguments\",\"execution_time\":0}");
            return;
        }
        
        String inputJson = args[2];
        
        try {
            int[] nums1 = parseIntArray(inputJson, "nums1");
            int[] nums2 = parseIntArray(inputJson, "nums2");
            
            Solution solution = new Solution();
            int[] result = solution.intersection(nums1, nums2);
            
            String resultStr = vectorToString(result);
            System.out.println("{\"result\": " + resultStr + ", \"execution_time\": 0}");
            
        } catch (Exception e) {
            System.out.println("{\"result\": \"Error: " + e.getMessage().replace("\"", "\\\"") + "\", \"execution_time\": 0}");
        }
    }
}
