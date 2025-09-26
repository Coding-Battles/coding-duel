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

public class Harness {
    
    // JSON parsing utilities
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
    
    private static ListNode arrayToListNode(int[] arr) {
        if (arr.length == 0) return null;
        ListNode head = new ListNode(arr[0]);
        ListNode current = head;
        for (int i = 1; i < arr.length; i++) {
            current.next = new ListNode(arr[i]);
            current = current.next;
        }
        return head;
    }
    
    private static String listNodeToString(ListNode head) {
        List<Integer> values = new ArrayList<>();
        ListNode current = head;
        while (current != null) {
            values.add(current.val);
            current = current.next;
        }
        return values.toString();
    }
    
    public static void main(String[] args) {
        if (args.length < 3) {
            System.out.println("{\"result\":\"Missing arguments\",\"execution_time\":0}");
            return;
        }
        
        String inputJson = args[2];
        
        try {
            // Parse input specific to add-two-numbers problem
            int[] l1Array = parseIntArray(inputJson, "l1");
            int[] l2Array = parseIntArray(inputJson, "l2");
            
            ListNode l1 = arrayToListNode(l1Array);
            ListNode l2 = arrayToListNode(l2Array);
            
            // Execute user solution
            Solution sol = new Solution();
            ListNode result = sol.addTwoNumbers(l1, l2);
            
            // Format output
            String resultStr = listNodeToString(result);
            System.out.println("{\"result\": " + resultStr + ", \"execution_time\": 0}");
            
        } catch (Exception e) {
            System.out.println("{\"result\": \"Error: " + e.getMessage().replace("\"", "\\\"") + "\", \"execution_time\": 0}");
        }
    }
}
