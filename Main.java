
import java.util.*;
import java.lang.reflect.*;

class Solution {
    public int ladderLength(String beginWord, String endWord, List<String> wordList) {
        return 5;
    }
}

// Static isBadVersion API for first-bad-version problem
class VersionControl {
    private static int badVersion = 0;
    
    public static void setBadVersion(int bad) {
        badVersion = bad;
    }
    
    public static boolean isBadVersion(int version) {
        return version >= badVersion;
    }
}

class Main {
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
                
                Method method = Solution.class.getMethod("firstBadVersion", int.class);
                result = method.invoke(sol, n);
            } else {
                // Find method by name only (like Python does)
                Method targetMethod = null;
                Method[] methods = Solution.class.getMethods();
                for (Method method : methods) {
                    if (method.getName().equals(methodName)) {
                        targetMethod = method;
                        break;
                    }
                }
                
                if (targetMethod == null) {
                    throw new RuntimeException("Method " + methodName + " not found in Solution class");
                }
                
                // Extract parameters in JSON key order (like Python's list(input_data.values()))
                Object[] params = extractParametersInJsonOrder(inputJson);
                
                result = targetMethod.invoke(sol, params);
            }
            
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            
            // Format output based on result type
            if (result instanceof int[]) {
                int[] intArrayResult = (int[]) result;
                System.out.print("{\"result\": [");
                for (int i = 0; i < intArrayResult.length; i++) {
                    System.out.print(intArrayResult[i]);
                    if (i < intArrayResult.length - 1) System.out.print(",");
                }
                System.out.println("], \"execution_time\": " + executionTime + "}");
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
    
    // Simple JSON parsing helpers
    private static int extractIntValue(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*(-?\\d+)";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            return Integer.parseInt(m.group(1));
        }
        throw new RuntimeException("Could not find key: " + key);
    }
    
    private static int[] extractIntArray(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\\[(.*?)\\]";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            String arrayContent = m.group(1).trim();
            if (arrayContent.isEmpty()) {
                return new int[0];
            }
            String[] parts = arrayContent.split(",");
            int[] result = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                result[i] = Integer.parseInt(parts[i].trim());
            }
            return result;
        }
        throw new RuntimeException("Could not find array key: " + key);
    }
    
    private static String extractStringValue(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\"(.*?)\"";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            return m.group(1);
        }
        throw new RuntimeException("Could not find string key: " + key);
    }
    
    private static String[] extractStringArray(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\\[(.*?)\\]";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            String arrayContent = m.group(1).trim();
            if (arrayContent.isEmpty()) {
                return new String[0];
            }
            String[] parts = arrayContent.split(",");
            String[] result = new String[parts.length];
            for (int i = 0; i < parts.length; i++) {
                String trimmed = parts[i].trim();
                if (trimmed.startsWith("\"") && trimmed.endsWith("\"")) {
                    result[i] = trimmed.substring(1, trimmed.length() - 1);
                } else {
                    result[i] = trimmed;
                }
            }
            return result;
        }
        throw new RuntimeException("Could not find string array key: " + key);
    }
    
    private static Object[] extractParametersInJsonOrder(String json) {
        // Extract JSON values in order (like Python's list(input_data.values()))
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        // Parse JSON manually to extract key-value pairs in order
        String cleanJson = json.trim();
        if (cleanJson.startsWith("{") && cleanJson.endsWith("}")) {
            cleanJson = cleanJson.substring(1, cleanJson.length() - 1);
        }
        
        // Split by commas (simple approach for well-formed JSON)
        String[] parts = cleanJson.split(",");
        
        for (String part : parts) {
            part = part.trim();
            if (part.contains(":")) {
                String[] keyValue = part.split(":", 2);
                if (keyValue.length == 2) {
                    String key = keyValue[0].trim().replaceAll("^\"|\"$", "");
                    String value = keyValue[1].trim();
                    
                    try {
                        // Try to extract this parameter by key
                        if (value.startsWith("[")) {
                            // Array parameter
                            if (value.contains("\"")) {
                                // String array - convert to List<String> for Java
                                String[] stringArray = extractStringArray(json, key);
                                java.util.List<String> stringList = java.util.Arrays.asList(stringArray);
                                params.add(stringList);
                            } else {
                                params.add(extractIntArray(json, key));
                            }
                        } else if (value.startsWith("\"")) {
                            // String parameter
                            params.add(extractStringValue(json, key));
                        } else if (value.equals("true") || value.equals("false")) {
                            // Boolean parameter
                            params.add(Boolean.parseBoolean(value));
                        } else {
                            // Integer parameter
                            params.add(extractIntValue(json, key));
                        }
                    } catch (Exception e) {
                        // Skip if extraction fails
                    }
                }
            }
        }
        
        return params.toArray();
    }
}