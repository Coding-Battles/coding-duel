import java.util.*;
import java.lang.reflect.*;


// VersionControl API for first-bad-version problem
class VersionControl {
    private static int badVersion = 0;
    
    public static void setBadVersion(int bad) {
        badVersion = bad;
    }
    
    public static boolean isBadVersion(int version) {
        return version >= badVersion;
    }
}

// TreeNode definition for binary tree problems
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

// ListNode definition for linked list problems
class ListNode {
    int val;
    ListNode next;
    ListNode() {}
    ListNode(int val) { this.val = val; }
    ListNode(int val, ListNode next) { this.val = val; this.next = next; }
}

// Main wrapper class containing all helper methods
class TestRunner {
    // Helper method to serialize TreeNode to array format (level-order)
    public static void serializeTreeNode(TreeNode root, java.util.List<Object> result) {
        if (root == null) {
            return;
        }
        
        java.util.Queue<TreeNode> queue = new java.util.LinkedList<>();
        queue.offer(root);
        
        while (!queue.isEmpty()) {
            TreeNode node = queue.poll();
            if (node == null) {
                result.add(null);
            } else {
                result.add(node.val);
                queue.offer(node.left);
                queue.offer(node.right);
            }
        }
        
        // Remove trailing nulls
        while (!result.isEmpty() && result.get(result.size() - 1) == null) {
            result.remove(result.size() - 1);
        }
    }

    // Helper method to extract 2-D int array from JSON
    public static int[][] extractIntArrayArray(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\\[(.*?)\\](?=\\s*[,}])";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern, java.util.regex.Pattern.DOTALL);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            String arrayContent = m.group(1);
            // Parse nested arrays [[1,2],[3,4]] format
            java.util.List<int[]> arrays = new java.util.ArrayList<>();
            String[] subArrays = arrayContent.split(",\\],\\s*\\[");
            for (String subArray : subArrays) {
                subArray = subArray.replaceAll("[\\[\\]]", "").trim();
                if (!subArray.isEmpty()) {
                    String[] elements = subArray.split(",");
                    int[] arr = new int[elements.length];
                    for (int i = 0; i < elements.length; i++) {
                        arr[i] = Integer.parseInt(elements[i].trim());
                    }
                    arrays.add(arr);
                }
            }
            return arrays.toArray(new int[0][]);
        }
        return new int[0][];
    }

    // Helper method to convert int array to ListNode
    public static ListNode arrayToListNode(int[] arr) {
        if (arr == null || arr.length == 0) return null;
        
        ListNode head = new ListNode(arr[0]);
        ListNode current = head;
        
        for (int i = 1; i < arr.length; i++) {
            current.next = new ListNode(arr[i]);
            current = current.next;
        }
        
        return head;
    }

    // Helper method to convert int array to TreeNode
    public static TreeNode arrayToTreeNode(int[] arr) {
        if (arr.length == 0 || arr[0] == Integer.MAX_VALUE) return null;
        
        TreeNode root = new TreeNode(arr[0]);
        java.util.Queue<TreeNode> queue = new java.util.LinkedList<>();
        queue.offer(root);
        
        int i = 1;
        while (!queue.isEmpty() && i < arr.length) {
            TreeNode current = queue.poll();
            
            // Left child
            if (i < arr.length) {
                if (arr[i] != Integer.MAX_VALUE) {
                    current.left = new TreeNode(arr[i]);
                    queue.offer(current.left);
                }
                i++;
            }
            
            // Right child
            if (i < arr.length) {
                if (arr[i] != Integer.MAX_VALUE) {
                    current.right = new TreeNode(arr[i]);
                    queue.offer(current.right);
                }
                i++;
            }
        }
        
        return root;
    }

    // Helper method to extract int value from JSON
    public static int extractIntValue(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*(\\d+)";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        return m.find() ? Integer.parseInt(m.group(1)) : 0;
    }

    // Helper method to extract string value from JSON
    public static String extractStringValue(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\"(.*?)\"";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        return m.find() ? m.group(1) : "";
    }

    // Helper method to extract int array from JSON
    public static int[] extractIntArray(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\\[(.*?)\\]";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
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

    // Helper method to extract 2-D int matrix from JSON
    public static int[][] extractIntMatrix(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\\[(.*?)\\](?=\\s*[,}])";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern, java.util.regex.Pattern.DOTALL);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            String arrayContent = m.group(1);
            // Parse nested arrays [[1,2],[3,4]] format
            java.util.List<int[]> arrays = new java.util.ArrayList<>();
            String[] subArrays = arrayContent.split(",\\],\\s*\\[");
            for (String subArray : subArrays) {
                subArray = subArray.replaceAll("[\\[\\]]", "").trim();
                if (!subArray.isEmpty()) {
                    String[] elements = subArray.split(",");
                    int[] arr = new int[elements.length];
                    for (int i = 0; i < elements.length; i++) {
                        arr[i] = Integer.parseInt(elements[i].trim());
                    }
                    arrays.add(arr);
                }
            }
            return arrays.toArray(new int[0][]);
        }
        return new int[0][];
    }

    // Helper method to extract string array from JSON
    public static String[] extractStringArray(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\\[(.*?)\\]";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            String arrayContent = m.group(1);
            if (arrayContent.trim().isEmpty()) {
                return new String[0];
            }
            String[] elements = arrayContent.split(",");
            String[] result = new String[elements.length];
            for (int i = 0; i < elements.length; i++) {
                result[i] = elements[i].trim().replaceAll(",\"", "");
            }
            return result;
        }
        return new String[0];
    }

    // Helper method to extract parameters in JSON order
    public static Object[] extractParametersInJsonOrder(String inputJson) {
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        // Parse JSON manually to extract all key-value pairs
        // Remove outer braces and split by commas (simple parsing)
        String content = inputJson.trim();
        if (content.startsWith("{") && content.endsWith("}")) {
            content = content.substring(1, content.length() - 1);
        }
        
        // Split by commas but be careful with nested structures
        java.util.List<String> pairs = new java.util.ArrayList<>();
        int depth = 0;
        StringBuilder current = new StringBuilder();
        
        for (int i = 0; i < content.length(); i++) {
            char c = content.charAt(i);
            if (c == '[' || c == '{') {
                depth++;
            } else if (c == ']' || c == '}') {
                depth--;
            } else if (c == ',' && depth == 0) {
                pairs.add(current.toString().trim());
                current = new StringBuilder();
                continue;
            }
            current.append(c);
        }
        if (current.length() > 0) {
            pairs.add(current.toString().trim());
        }
        
        // Extract values from each key-value pair
        for (String pair : pairs) {
            String[] keyValue = pair.split(":", 2);
            if (keyValue.length == 2) {
                String key = keyValue[0].trim().replaceAll("\"", "");
                String value = keyValue[1].trim();
                
                // Determine the type and convert accordingly
                if (value.startsWith("[") && value.endsWith("]")) {
                    // Array type
                    if (value.contains("\"")) {
                        // String array
                        params.add(TestRunner.extractStringArray(inputJson, key));
                    } else if (value.contains("[")) {
                        // 2D int array
                        params.add(TestRunner.extractIntArrayArray(inputJson, key));
                    } else {
                        // Int array
                        params.add(TestRunner.extractIntArray(inputJson, key));
                    }
                } else if (value.startsWith("\"") && value.endsWith("\"")) {
                    // String type
                    params.add(TestRunner.extractStringValue(inputJson, key));
                } else {
                    // Number type
                    params.add(TestRunner.extractIntValue(inputJson, key));
                }
            }
        }
        
        return params.toArray(new Object[0]);
    }

    // Helper method to extract parameters based on method signature
    public static Object[] extractParametersForMethod(String inputJson, Method method) {
        Class<?>[] paramTypes = method.getParameterTypes();
        Object[] params = new Object[paramTypes.length];
        
        // Get all JSON keys in order
        java.util.List<String> keys = new java.util.ArrayList<>();
        String content = inputJson.trim();
        if (content.startsWith("{") && content.endsWith("}")) {
            content = content.substring(1, content.length() - 1);
        }
        
        // Extract keys in order
        int depth = 0;
        StringBuilder current = new StringBuilder();
        for (int i = 0; i < content.length(); i++) {
            char c = content.charAt(i);
            if (c == '[' || c == '{') {
                depth++;
            } else if (c == ']' || c == '}') {
                depth--;
            } else if (c == ',' && depth == 0) {
                String pair = current.toString().trim();
                if (pair.contains(":")) {
                    String key = pair.split(":", 2)[0].trim().replaceAll("\"", "");
                    keys.add(key);
                }
                current = new StringBuilder();
                continue;
            }
            current.append(c);
        }
        if (current.length() > 0) {
            String pair = current.toString().trim();
            if (pair.contains(":")) {
                String key = pair.split(":", 2)[0].trim().replaceAll("\"", "");
                keys.add(key);
            }
        }
        
        // Convert parameters based on method signature
        for (int i = 0; i < paramTypes.length && i < keys.size(); i++) {
            String key = keys.get(i);
            Class<?> paramType = paramTypes[i];
            
            if (paramType == String.class) {
                params[i] = TestRunner.extractStringValue(inputJson, key);
            } else if (paramType == int.class || paramType == Integer.class) {
                params[i] = TestRunner.extractIntValue(inputJson, key);
            } else if (paramType == int[].class) {
                params[i] = TestRunner.extractIntArray(inputJson, key);
            } else if (paramType == int[][].class) {
                params[i] = TestRunner.extractIntArrayArray(inputJson, key);
            } else if (paramType == String[].class) {
                params[i] = TestRunner.extractStringArray(inputJson, key);
            } else if (paramType.getSimpleName().equals("ListNode")) {
                int[] array = TestRunner.extractIntArray(inputJson, key);
                params[i] = TestRunner.arrayToListNode(array);
            } else if (paramType.getSimpleName().equals("TreeNode")) {
                int[] array = TestRunner.extractIntArray(inputJson, key);
                params[i] = TestRunner.arrayToTreeNode(array);
            } else {
                // Default: try to extract as string
                params[i] = TestRunner.extractStringValue(inputJson, key);
            }
        }
        
        return params;
    }
}

class Solution {
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        return null;
    }

    // Injected main method for wrapper functionality
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("{{\"result\": \"Missing arguments: expected method name and input data\", \"execution_time\": 0}}");
            return;
        }
        
        String methodName = args[0];
        String inputJson = args[1];
        long startTime = System.nanoTime();
        
        try {
            Solution sol = new Solution();
            Object result = null;
            
            // Special handling for first-bad-version problem
            if ("firstBadVersion".equals(methodName)) {
                int n = TestRunner.extractIntValue(inputJson, "n");
                int bad = TestRunner.extractIntValue(inputJson, "bad");
                
                VersionControl.setBadVersion(bad);
                
                java.lang.reflect.Method method = Solution.class.getMethod("firstBadVersion", int.class);
                result = method.invoke(sol, n);
            } else if ("rotate".equals(methodName)) {
                // Special handling for rotate method which modifies matrix in place
                int[][] matrix = TestRunner.extractIntMatrix(inputJson, "matrix");
                java.lang.reflect.Method method = Solution.class.getMethod("rotate", int[][].class);
                method.invoke(sol, (Object) matrix);
                result = matrix; // Return the modified matrix
            } else {
                // Generic method calling using reflection
                java.lang.reflect.Method targetMethod = null;
                java.lang.reflect.Method[] methods = Solution.class.getMethods();
                for (java.lang.reflect.Method method : methods) {
                    if (method.getName().equals(methodName)) {
                        targetMethod = method;
                        break;
                    }
                }
                
                if (targetMethod == null) {{
                    throw new RuntimeException("Method " + methodName + " not found in Solution class");
                }}
                
                Object[] params = TestRunner.extractParametersForMethod(inputJson, targetMethod);
                result = targetMethod.invoke(sol, params);
            }
            
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            
            // Format output
            if (result instanceof int[][]) {
                int[][] matrix = (int[][]) result;
                StringBuilder sb = new StringBuilder("[");
                for (int i = 0; i < matrix.length; i++) {
                    if (i > 0) sb.append(", ");
                    sb.append("[");
                    for (int j = 0; j < matrix[i].length; j++) {
                        if (j > 0) sb.append(", ");
                        sb.append(matrix[i][j]);
                    }
                    sb.append("]");
                }
                sb.append("]");
                System.out.println("{{\"result\": " + sb.toString() + ", \"execution_time\": " + executionTime + "}}");
            } else if (result instanceof int[]) {
                int[] arr = (int[]) result;
                StringBuilder sb = new StringBuilder("[");
                for (int i = 0; i < arr.length; i++) {
                    if (i > 0) sb.append(", ");
                    sb.append(arr[i]);
                }
                sb.append("]");
                System.out.println("{{\"result\": " + sb.toString() + ", \"execution_time\": " + executionTime + "}}");
            } else if (result instanceof java.util.List) {
                java.util.List<?> list = (java.util.List<?>) result;
                // Check if this is a List<List<String>> (like group-anagrams)
                boolean isListOfLists = !list.isEmpty() && list.get(0) instanceof java.util.List;
                
                if (isListOfLists) {
                    // Handle List<List<String>>
                    StringBuilder sb = new StringBuilder("[");
                    for (int i = 0; i < list.size(); i++) {
                        if (i > 0) sb.append(", ");
                        java.util.List<?> innerList = (java.util.List<?>) list.get(i);
                        sb.append("[");
                        for (int j = 0; j < innerList.size(); j++) {
                            if (j > 0) sb.append(", ");
                            Object item = innerList.get(j);
                            if (item instanceof String) {
                                sb.append("\"").append(item.toString().replace("\"", "\\\"")).append("\"");
                            } else {
                                sb.append(item.toString());
                            }
                        }
                        sb.append("]");
                    }
                    sb.append("]");
                    System.out.println("{\"result\": " + sb.toString() + ", \"execution_time\": " + executionTime + "}");
                } else {
                    // Handle regular List<String> or List<Integer>
                    StringBuilder sb = new StringBuilder("[");
                    for (int i = 0; i < list.size(); i++) {
                        if (i > 0) sb.append(", ");
                        Object item = list.get(i);
                        if (item instanceof String) {
                            sb.append("\"").append(item.toString().replace("\"", "\\\"")).append("\"");
                        } else {
                            sb.append(item.toString());
                        }
                    }
                    sb.append("]");
                    System.out.println("{\"result\": " + sb.toString() + ", \"execution_time\": " + executionTime + "}");
                }
            } else if (result instanceof Integer) {
                System.out.println("{\"result\": " + result + ", \"execution_time\": " + executionTime + "}");
            } else if (result instanceof Boolean) {
                System.out.println("{\"result\": " + result + ", \"execution_time\": " + executionTime + "}");
            }} else if (result instanceof String) {{
                System.out.println("{{\"result\": \"" + result.toString().replace("\"", "\\\"") + "\", \"execution_time\": " + executionTime + "}}");
            }} else if (result instanceof ListNode) {{
                // Serialize ListNode to array format
                java.util.List<Integer> listArray = new java.util.ArrayList<>();
                ListNode current = (ListNode) result;
                while (current != null) {{
                    listArray.add(current.val);
                    current = current.next;
                }}
                StringBuilder sb = new StringBuilder("[");
                for (int i = 0; i < listArray.size(); i++) {{
                    if (i > 0) sb.append(", ");
                    sb.append(listArray.get(i));
                }}
                sb.append("]");
                System.out.println("{{\"result\": " + sb.toString() + ", \"execution_time\": " + executionTime + "}}");
            }} else if (result instanceof TreeNode) {{
                // Serialize TreeNode to array format
                java.util.List<Object> treeArray = new java.util.ArrayList<>();
                TestRunner.serializeTreeNode((TreeNode) result, treeArray);
                StringBuilder sb = new StringBuilder("[");
                for (int i = 0; i < treeArray.size(); i++) {
                    if (i > 0) sb.append(", ");
                    if (treeArray.get(i) == null) {
                        sb.append("null");
                    } else {
                        sb.append(treeArray.get(i).toString());
                    }
                }
                sb.append("]");
                System.out.println("{\"result\": " + sb.toString() + ", \"execution_time\": " + executionTime + "}");
            } else {
                System.out.println("{\"result\": \"" + String.valueOf(result).replace("\"", "\\\"") + "\", \"execution_time\": " + executionTime + "}");
            }
            
        } catch (Exception e) {
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            System.out.println("{\"result\": \"" + e.getMessage().replace("\"", "\\\"") + "\", \"execution_time\": " + executionTime + "}");
        }
    }

}

