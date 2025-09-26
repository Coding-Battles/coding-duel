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
        String pattern = "\"" + key + "\"\\s*:\\s*\\[(.*)\\]";
        Pattern p = Pattern.compile(pattern);
        Matcher m = p.matcher(json);
        if (m.find()) {
            String content = m.group(1);
            if (content.trim().isEmpty()) {
                return new int[0][0];
            }
            
            String[] rowStrings = content.split("\\],\\s*\\[");
            List<int[]> rows = new ArrayList<>();
            
            for (String rowStr : rowStrings) {
                rowStr = rowStr.replaceAll("\\[|\\]", "");
                if (!rowStr.trim().isEmpty()) {
                    String[] elements = rowStr.split(",");
                    int[] row = new int[elements.length];
                    for (int i = 0; i < elements.length; i++) {
                        row[i] = Integer.parseInt(elements[i].trim());
                    }
                    rows.add(row);
                }
            }
            return rows.toArray(new int[rows.size()][]);
        }
        return new int[0][0];
    }
    
    private static String matrixToString(int[][] matrix) {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        for (int i = 0; i < matrix.length; i++) {
            if (i > 0) sb.append(",");
            sb.append("[");
            for (int j = 0; j < matrix[i].length; j++) {
                if (j > 0) sb.append(",");
                sb.append(matrix[i][j]);
            }
            sb.append("]");
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
            int[][] matrix = parseIntMatrix(inputJson, "matrix");
            
            Solution solution = new Solution();
            solution.rotate(matrix);
            
            String resultStr = matrixToString(matrix);
            System.out.println("{\"result\": " + resultStr + ", \"execution_time\": 0}");
            
        } catch (Exception e) {
            System.out.println("{\"result\": \"Error: " + e.getMessage().replace("\"", "\\\"") + "\", \"execution_time\": 0}");
        }
    }
}
