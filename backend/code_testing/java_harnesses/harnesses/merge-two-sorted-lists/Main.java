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
    
    private static ListNode buildListNode(int[] values) {
        if (values.length == 0) return null;
        
        ListNode dummy = new ListNode(0);
        ListNode current = dummy;
        
        for (int val : values) {
            current.next = new ListNode(val);
            current = current.next;
        }
        
        return dummy.next;
    }
    
    private static int[] parseIntArray(String json, String key) {
        // Find the array in JSON
        String pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]+)\\]";
        Pattern p = Pattern.compile(pattern);
        Matcher m = p.matcher(json);
        if (!m.find()) return new int[0];
        
        String content = m.group(1).trim();
        if (content.isEmpty()) return new int[0];
        
        // Clean any remaining brackets and split
        content = content.replaceAll("[\\[\\]]", "");
        String[] elements = content.split(",");
        int[] result = new int[elements.length];
        for (int i = 0; i < elements.length; i++) {
            result[i] = Integer.parseInt(elements[i].trim());
        }
        
        return result;
    }
    
    private static List<Integer> listToArray(ListNode head) {
        List<Integer> result = new ArrayList<>();
        while (head != null) {
            result.add(head.val);
            head = head.next;
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
            int[] list1Array = parseIntArray(inputJson, "list1");
            int[] list2Array = parseIntArray(inputJson, "list2");
            
            ListNode list1 = buildListNode(list1Array);
            ListNode list2 = buildListNode(list2Array);
            
            Solution solution = new Solution();
            ListNode result = solution.mergeTwoLists(list1, list2);
            
            List<Integer> resultArray = listToArray(result);
            
            // Format as JSON array
            System.out.print("{\"result\": [");
            for (int i = 0; i < resultArray.size(); i++) {
                if (i > 0) System.out.print(",");
                System.out.print(resultArray.get(i));
            }
            System.out.println("], \"execution_time\": 0}");
            
        } catch (Exception e) {
            System.out.println("{\"result\": \"Error: " + e.getMessage().replace("\"", "\\\"") + "\", \"execution_time\": 0}");
        }
    }
}
