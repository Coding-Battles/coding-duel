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

public class Solution {
    public int maxDepth(TreeNode root) {
        if (root == null) return 0;
        return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
    }

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
                // Generic method calling using reflection
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
                
                Object[] params = extractParametersInJsonOrder(inputJson);
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
    
    private static Object[] extractParametersInJsonOrder(String json) {
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        // Simple JSON parsing - handle specific patterns
        if (json.contains("\"nums\"") && json.contains("\"target\"")) {
            // twoSum pattern: {"nums": [2, 7, 11, 15], "target": 9}
            int[] nums = extractIntArray(json, "nums");
            int target = extractIntValue(json, "target");
            params.add(nums);
            params.add(target);
        } else {
            // Generic fallback - extract all integer values in order
            String cleanJson = json.replaceAll("[{}\"\\[\\]]", "");
            String[] pairs = cleanJson.split(",");
            for (String pair : pairs) {
                if (pair.contains(":")) {
                    String value = pair.split(":")[1].trim();
                    try {
                        params.add(Integer.parseInt(value));
                    } catch (NumberFormatException e) {
                        params.add(value);
                    }
                }
            }
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
}

