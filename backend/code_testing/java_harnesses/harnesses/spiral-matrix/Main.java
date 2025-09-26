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
        // Find the matrix array in JSON
        String pattern = "\"" + key + "\"\\s*:\\s*\\[(.*)\\]";
        Pattern p = Pattern.compile(pattern);
        Matcher m = p.matcher(json);
        if (!m.find()) return new int[0][0];
        
        String content = m.group(1).trim();
        if (content.isEmpty()) return new int[0][0];
        
        // Split by "],["  to get individual rows
        String[] rowStrings;
        if (content.contains("],[")) {
            rowStrings = content.split("\\],\\s*\\[");
            // Clean up first and last elements
            rowStrings[0] = rowStrings[0].replaceFirst("^\\[", "");
            rowStrings[rowStrings.length-1] = rowStrings[rowStrings.length-1].replaceFirst("\\]$", "");
        } else {
            // Single row case
            rowStrings = new String[]{content.replaceAll("\\[|\\]", "")};
        }
        
        List<int[]> rows = new ArrayList<>();
        for (String rowStr : rowStrings) {
            if (!rowStr.trim().isEmpty()) {
                String[] elements = rowStr.split(",");
                int[] row = new int[elements.length];
                for (int i = 0; i < elements.length; i++) {
                    row[i] = Integer.parseInt(elements[i].trim());
                }
                rows.add(row);
            }
        }
        
        return rows.toArray(new int[0][]);
    }
    
    public static void main(String[] args) {
        if (args.length < 3) {
            System.out.println("{\"result\":\"Missing arguments\",\"execution_time\":0}");
            return;
        }
        
        String inputJson = args[2];
        
        try {
            int[][] matrix = parseIntMatrix(inputJson, "matrix");
            
            Solution solution = new Solution();
            List<Integer> result = solution.spiralOrder(matrix);
            
            // Format as JSON array
            System.out.print("{\"result\": [");
            for (int i = 0; i < result.size(); i++) {
                if (i > 0) System.out.print(",");
                System.out.print(result.get(i));
            }
            System.out.println("], \"execution_time\": 0}");
            
        } catch (Exception e) {
            System.out.println("{\"result\": \"Error: " + e.getMessage().replace("\"", "\\\"") + "\", \"execution_time\": 0}");
        }
    }
}
