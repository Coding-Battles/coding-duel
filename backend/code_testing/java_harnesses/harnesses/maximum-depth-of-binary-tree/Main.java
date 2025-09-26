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
    
    private static TreeNode buildTree(String[] values, int index) {
        if (index >= values.length || values[index].equals("null")) {
            return null;
        }
        
        TreeNode node = new TreeNode(Integer.parseInt(values[index]));
        node.left = buildTree(values, 2 * index + 1);
        node.right = buildTree(values, 2 * index + 2);
        
        return node;
    }
    
    private static TreeNode parseTree(String json, String key) {
        // Find the array in JSON
        String pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]+)\\]";
        Pattern p = Pattern.compile(pattern);
        Matcher m = p.matcher(json);
        if (!m.find()) return null;
        
        String content = m.group(1).trim();
        if (content.isEmpty()) return null;
        
        // Split by comma and clean up
        String[] elements = content.split(",");
        for (int i = 0; i < elements.length; i++) {
            elements[i] = elements[i].trim().replaceAll("\"", "");
        }
        
        return buildTree(elements, 0);
    }
    
    public static void main(String[] args) {
        if (args.length < 3) {
            System.out.println("{\"result\":\"Missing arguments\",\"execution_time\":0}");
            return;
        }
        
        String inputJson = args[2];
        
        try {
            TreeNode root = parseTree(inputJson, "root");
            
            Solution solution = new Solution();
            int result = solution.maxDepth(root);
            
            System.out.println("{\"result\": " + result + ", \"execution_time\": 0}");
            
        } catch (Exception e) {
            System.out.println("{\"result\": \"Error: " + e.getMessage().replace("\"", "\\\"") + "\", \"execution_time\": 0}");
        }
    }
}
