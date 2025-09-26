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
    
    private static void serializeTree(TreeNode root, List<String> result) {
        if (root == null) {
            result.add("null");
            return;
        }
        
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        
        while (!queue.isEmpty()) {
            TreeNode node = queue.poll();
            if (node == null) {
                result.add("null");
            } else {
                result.add(String.valueOf(node.val));
                queue.offer(node.left);
                queue.offer(node.right);
            }
        }
        
        // Remove trailing nulls
        while (result.size() > 0 && result.get(result.size() - 1).equals("null")) {
            result.remove(result.size() - 1);
        }
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
            TreeNode result = solution.invertTree(root);
            
            // Serialize tree back to array
            List<String> serialized = new ArrayList<>();
            if (result != null) {
                serializeTree(result, serialized);
            }
            
            // Format as JSON array
            System.out.print("{\"result\": [");
            for (int i = 0; i < serialized.size(); i++) {
                if (i > 0) System.out.print(",");
                if (serialized.get(i).equals("null")) {
                    System.out.print("null");
                } else {
                    System.out.print(serialized.get(i));
                }
            }
            System.out.println("], \"execution_time\": 0}");
            
        } catch (Exception e) {
            System.out.println("{\"result\": \"Error: " + e.getMessage().replace("\"", "\\\"") + "\", \"execution_time\": 0}");
        }
    }
}
