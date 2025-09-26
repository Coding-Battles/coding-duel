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

class Solution {
    public List<String> wordBreak(String s, List<String> wordDict) {
        return new ArrayList<>();
    }

    // Data structure definitions for linked list and tree problems
    static class ListNode {
        int val;
        ListNode next;
        ListNode() {}
        ListNode(int val) { this.val = val; }
        ListNode(int val, ListNode next) { this.val = val; this.next = next; }
    }
    
    static class TreeNode {
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
    
    // Embedded signature information for type conversion (base64 encoded)
    private static final String SIGNATURE_B64 = "eyJwYXJhbWV0ZXJzIjogW3sibmFtZSI6ICJzIiwgInR5cGUiOiAic3RyaW5nIn0sIHsibmFtZSI6ICJ3b3JkRGljdCIsICJ0eXBlIjogInN0cmluZ1tdIn1dLCAicmV0dXJuVHlwZSI6ICJzdHJpbmdbXSJ9";

    // Injected main method for wrapper functionality
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("{\"result\": \"Missing arguments: expected method name and input data\", \"execution_time\": 0}");
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
                int n = extractIntValue(inputJson, "n");
                int bad = extractIntValue(inputJson, "bad");
                
                VersionControl.setBadVersion(bad);
                
                java.lang.reflect.Method method = Solution.class.getMethod("firstBadVersion", int.class);
                result = method.invoke(sol, n);
            } else {
                // Generic method calling using reflection with signature-based parameter conversion
                java.lang.reflect.Method targetMethod = null;
                java.lang.reflect.Method[] methods = Solution.class.getMethods();
                for (java.lang.reflect.Method method : methods) {
                    if (method.getName().equals(methodName)) {
                        targetMethod = method;
                        break;
                    }
                }
                
                if (targetMethod == null) {
                    throw new RuntimeException("Method " + methodName + " not found in Solution class");
                }
                
                Object[] params = extractParametersWithSignature(inputJson, methodName);
                result = targetMethod.invoke(sol, params);
            }
            
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            
            // Format output
            if (result instanceof int[]) {
                int[] arr = (int[]) result;
                StringBuilder sb = new StringBuilder("[");
                for (int i = 0; i < arr.length; i++) {
                    if (i > 0) sb.append(", ");
                    sb.append(arr[i]);
                }
                sb.append("]");
                System.out.println("{\"result\": " + sb.toString() + ", \"execution_time\": " + executionTime + "}");
            } else if (result instanceof Integer) {
                System.out.println("{\"result\": " + result + ", \"execution_time\": " + executionTime + "}");
            } else if (result instanceof Boolean) {
                System.out.println("{\"result\": " + result + ", \"execution_time\": " + executionTime + "}");
            } else if (result instanceof String) {
                System.out.println("{\"result\": \"" + result.toString().replace("\"", "\\\"") + "\", \"execution_time\": " + executionTime + "}");
            } else {
                System.out.println("{\"result\": \"" + String.valueOf(result).replace("\"", "\\\"") + "\", \"execution_time\": " + executionTime + "}");
            }
            
        } catch (Exception e) {
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            System.out.println("{\"result\": \"" + e.getMessage().replace("\"", "\\\"") + "\", \"execution_time\": " + executionTime + "}");
        }
    }
    
    // Helper methods
    private static int extractIntValue(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*(-?\\d+)";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            return Integer.parseInt(m.group(1));
        }
        throw new RuntimeException("Could not find key: " + key);
    }
    
    private static Object[] extractParametersWithSignature(String json, String methodName) {
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        try {
            // Parse signature information - decode base64 first
            if (!SIGNATURE_B64.isEmpty()) {
                System.err.println("🔧 [SIGNATURE] Using signature-based parameter conversion for " + methodName);
                
                // Decode base64 signature
                String signatureJson = new String(java.util.Base64.getDecoder().decode(SIGNATURE_B64));
                System.err.println("🔧 [SIGNATURE] Decoded signature: " + signatureJson);
                
                // Simple JSON parsing for signature information  
                // Extract params array from signature JSON
                String paramsSection = extractJsonSection(signatureJson, "params");
                if (paramsSection != null) {
                    String[] paramDefs = parseParamDefinitions(paramsSection);
                    
                    for (String paramDef : paramDefs) {
                        String paramName = extractJsonValue(paramDef, "name");
                        String paramType = extractJsonValue(paramDef, "type");
                        
                        if (paramName != null && paramType != null) {
                            System.err.println("🔧 [SIGNATURE] Processing param: " + paramName + " (" + paramType + ")");
                            Object value = convertParameterByType(json, paramName, paramType);
                            params.add(value);
                        }
                    }
                    
                    return params.toArray();
                }
            }
            
            // Fallback to legacy hardcoded patterns if no signature
            System.err.println("⚠️  [SIGNATURE] No signature available, using legacy parameter extraction");
            return extractParametersInJsonOrder(json);
            
        } catch (Exception e) {
            System.err.println("❌ [SIGNATURE] Error in signature-based conversion: " + e.getMessage());
            // Fallback to legacy method
            return extractParametersInJsonOrder(json);
        }
    }
    
    private static String extractJsonSection(String json, String key) {
        try {
            String pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]+)\\]";
            java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
            java.util.regex.Matcher m = p.matcher(json);
            if (m.find()) {
                return m.group(1);
            }
        } catch (Exception e) {
            System.err.println("Error extracting JSON section: " + e.getMessage());
        }
        return null;
    }
    
    private static String[] parseParamDefinitions(String paramsSection) {
        // Simple parsing for parameter definitions
        java.util.List<String> paramDefs = new java.util.ArrayList<>();
        int braceLevel = 0;
        StringBuilder current = new StringBuilder();
        
        for (int i = 0; i < paramsSection.length(); i++) {
            char c = paramsSection.charAt(i);
            if (c == '{') {
                braceLevel++;
                current.append(c);
            } else if (c == '}') {
                braceLevel--;
                current.append(c);
                if (braceLevel == 0) {
                    paramDefs.add(current.toString());
                    current = new StringBuilder();
                }
            } else if (c == ',' && braceLevel == 0) {
                // Skip comma at top level
            } else {
                current.append(c);
            }
        }
        
        return paramDefs.toArray(new String[0]);
    }
    
    private static String extractJsonValue(String jsonObject, String key) {
        try {
            String pattern = "\"" + key + "\"\\s*:\\s*\"([^\"]+)\"";
            java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
            java.util.regex.Matcher m = p.matcher(jsonObject);
            if (m.find()) {
                return m.group(1);
            }
        } catch (Exception e) {
            System.err.println("Error extracting JSON value: " + e.getMessage());
        }
        return null;
    }
    
    private static Object convertParameterByType(String json, String paramName, String paramType) {
        try {
            switch (paramType) {
                case "int":
                    return extractIntValue(json, paramName);
                case "string":
                    return extractStringValue(json, paramName);
                case "boolean":
                    return extractBooleanValue(json, paramName);
                case "int[]":
                    return extractIntArray(json, paramName);
                case "int[][]":
                    return extract2DIntArray(json, paramName);
                case "ListNode":
                    int[] listArray = extractIntArray(json, paramName);
                    return arrayToListNode(listArray);
                case "TreeNode":
                    Integer[] treeArray = extractIntArrayWithNulls(json, paramName);
                    return arrayToTreeNode(treeArray);
                case "string[]":
                    return extractStringArray(json, paramName);
                case "list<string>":
                    return extractStringArray(json, paramName);
                case "ListNode[]":
                    // Handle array of ListNodes (for merge-k-sorted-lists)
                    String pattern = "\"" + paramName + "\"\\s*:\\s*\\[([^\\]]+)\\]";
                    java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
                    java.util.regex.Matcher m = p.matcher(json);
                    if (m.find()) {
                        String arrayContent = m.group(1);
                        // Split by ], [ to get individual list arrays
                        String[] listStrings = arrayContent.split("\\],\\s*\\[");
                        ListNode[] result = new ListNode[listStrings.length];
                        for (int i = 0; i < listStrings.length; i++) {
                            String listStr = listStrings[i].replaceAll("^\\[|\\]$", "");
                            int[] listArray = parseIntArray(listStr);
                            result[i] = arrayToListNode(listArray);
                        }
                        return result;
                    }
                    return new ListNode[0];
                default:
                    System.err.println("⚠️  [SIGNATURE] Unknown parameter type: " + paramType + ", treating as string");
                    return extractStringValue(json, paramName);
            }
        } catch (Exception e) {
            System.err.println("❌ [SIGNATURE] Error converting parameter " + paramName + " (" + paramType + "): " + e.getMessage());
            throw new RuntimeException("Parameter conversion failed for " + paramName + ": " + e.getMessage());
        }
    }
    
    private static String extractStringValue(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\"([^\"]+)\"";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            return m.group(1);
        }
        throw new RuntimeException("Could not find string key: " + key);
    }
    
    private static boolean extractBooleanValue(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*(true|false)";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            return Boolean.parseBoolean(m.group(1));
        }
        throw new RuntimeException("Could not find boolean key: " + key);
    }
    
    private static String[] extractStringArray(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]+)\\]";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            String arrayContent = m.group(1);
            String[] elements = arrayContent.split(",");
            String[] result = new String[elements.length];
            for (int i = 0; i < elements.length; i++) {
                String element = elements[i].trim();
                if (element.startsWith("\\\"") && element.endsWith("\\\"")) {
                    element = element.substring(1, element.length() - 1);
                }
                result[i] = element;
            }
            return result;
        }
        return new String[0];
    }
                    element = element.substring(1, element.length() - 1);
                }
                result[i] = element;
            }
            return result;
        }
        return new String[0];
    }
    
    // Legacy parameter extraction methods (kept as fallback)
    private static Object[] extractParametersInJsonOrder(String json) {
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        try {
            // Enhanced JSON parsing for complex data structures
            if (json.contains("\"nums\"") && json.contains("\"target\"")) {
                // twoSum pattern: {"nums": [2, 7, 11, 15], "target": 9}
                int[] nums = extractIntArray(json, "nums");
                int target = extractIntValue(json, "target");
                params.add(nums);
                params.add(target);
            } else if (json.contains("\"l1\"") && json.contains("\"l2\"")) {
                // addTwoNumbers pattern: {"l1": [2, 4, 3], "l2": [5, 6, 4]}
                ListNode l1 = arrayToListNode(extractIntArray(json, "l1"));
                ListNode l2 = arrayToListNode(extractIntArray(json, "l2"));
                params.add(l1);
                params.add(l2);
            } else if (json.contains("\"list1\"") && json.contains("\"list2\"")) {
                // mergeTwoLists pattern: {"list1": [1, 2, 4], "list2": [1, 3, 4]}
                ListNode list1 = arrayToListNode(extractIntArray(json, "list1"));
                ListNode list2 = arrayToListNode(extractIntArray(json, "list2"));
                params.add(list1);
                params.add(list2);
            } else if (json.contains("\"root\"")) {
                // Tree problems pattern: {"root": [4, 2, 7, 1, 3, 6, 9]}
                TreeNode root = arrayToTreeNode(extractIntArrayWithNulls(json, "root"));
                params.add(root);
            } else if (json.contains("\"p\"") && json.contains("\"q\"")) {
                // Same tree pattern: {"p": [1, 2, 3], "q": [1, 2, 3]}
                TreeNode p = arrayToTreeNode(extractIntArrayWithNulls(json, "p"));
                TreeNode q = arrayToTreeNode(extractIntArrayWithNulls(json, "q"));
                params.add(p);
                params.add(q);
            } else if (json.contains("\"a\"") && json.contains("\"b\"")) {
                // String problems like add-binary: {"a": "11", "b": "1"}
                String a = extractStringValue(json, "a");
                String b = extractStringValue(json, "b");
                params.add(a);
                params.add(b);
            } else if (json.contains("\"intervals\"")) {
                // Intervals pattern: {"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]}
                int[][] intervals = extract2DIntArray(json, "intervals");
                params.add(intervals);
            } else {
                // Generic fallback - extract all values in order from JSON
                java.util.regex.Pattern pattern = java.util.regex.Pattern.compile("\"([^\"]+)\"\\s*:\\s*([^,}]+)");
                java.util.regex.Matcher matcher = pattern.matcher(json);
                while (matcher.find()) {
                    String value = matcher.group(2).trim();
                    if (value.startsWith("\"") && value.endsWith("\"")) {
                        // String value
                        params.add(value.substring(1, value.length() - 1));
                    } else if (value.startsWith("[") && value.endsWith("]")) {
                        // Array value - try to parse as int array
                        try {
                            String arrayContent = value.substring(1, value.length() - 1);
                            if (arrayContent.trim().isEmpty()) {
                                params.add(new int[0]);
                            } else {
                                String[] elements = arrayContent.split(",");
                                int[] intArray = new int[elements.length];
                                for (int i = 0; i < elements.length; i++) {
                                    intArray[i] = Integer.parseInt(elements[i].trim());
                                }
                                params.add(intArray);
                            }
                        } catch (NumberFormatException e) {
                            // If not integers, treat as string array
                            params.add(value);
                        }
                    } else {
                        // Try to parse as integer, fall back to string
                        try {
                            params.add(Integer.parseInt(value));
                        } catch (NumberFormatException e) {
                            params.add(value);
                        }
                    }
                }
            }
        } catch (Exception e) {
            // If parsing fails, return empty array to trigger error
            System.err.println("Error parsing parameters: " + e.getMessage());
        }
        
        return params.toArray();
    }
    
    private static int[] extractIntArray(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]+)\\]";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            String arrayContent = m.group(1);
            String[] elements = arrayContent.split(",");
            int[] result = new int[elements.length];
            for (int i = 0; i < elements.length; i++) {
                result[i] = Integer.parseInt(elements[i].trim());
            }
            return result;
        }
        return new int[0];
    }
    
    private static Integer[] extractIntArrayWithNulls(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]+)\\]";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            String arrayContent = m.group(1);
            String[] elements = arrayContent.split(",");
            Integer[] result = new Integer[elements.length];
            for (int i = 0; i < elements.length; i++) {
                String element = elements[i].trim();
                if (element.equals("null")) {
                    result[i] = null;
                } else {
                    result[i] = Integer.parseInt(element);
                }
            }
            return result;
        }
        return new Integer[0];
    }
    
    private static int[][] extract2DIntArray(String json, String key) {
        // Implementation for 2D array extraction
        return new int[0][0]; // Placeholder
    }
    
    private static int[] parseIntArray(String arrayStr) {
        if (arrayStr.trim().isEmpty()) return new int[0];
        String[] elements = arrayStr.split(",");
        int[] result = new int[elements.length];
        for (int i = 0; i < elements.length; i++) {
            result[i] = Integer.parseInt(elements[i].trim());
        }
        return result;
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
    
    private static TreeNode arrayToTreeNode(Integer[] arr) {
        if (arr.length == 0 || arr[0] == null) return null;
        TreeNode root = new TreeNode(arr[0]);
        java.util.Queue<TreeNode> queue = new java.util.LinkedList<>();
        queue.offer(root);
        int i = 1;
        while (!queue.isEmpty() && i < arr.length) {
            TreeNode node = queue.poll();
            if (i < arr.length && arr[i] != null) {
                node.left = new TreeNode(arr[i]);
                queue.offer(node.left);
            }
            i++;
            if (i < arr.length && arr[i] != null) {
                node.right = new TreeNode(arr[i]);
                queue.offer(node.right);
            }
            i++;
        }
        return root;
    }
}

