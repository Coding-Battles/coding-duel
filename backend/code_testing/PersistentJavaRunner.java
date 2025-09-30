import java.io.*;
import java.util.*;
import java.util.concurrent.*;
import javax.tools.*;
import java.net.*;

public class PersistentJavaRunner {
    private static final Map<String, ClassLoader> userClassLoaders = new ConcurrentHashMap<>();
    private static final ExecutorService executor = Executors.newSingleThreadExecutor();
    
    // Code caching for compilation optimization
    private static final Map<String, Class<?>> COMPILED_CLASS_CACHE = new ConcurrentHashMap<>();
    private static final Map<String, byte[]> BYTECODE_CACHE = new ConcurrentHashMap<>();
    private static final int MAX_CACHE_SIZE = 100;
    
    public static void main(String[] args) {
        System.err.println("PersistentJavaRunner started - listening on port 8899");
        
        // Pre-warm the JIT compiler
        System.err.println("|PersistentJavaRunner.java| [JIT WARMUP] Starting JIT pre-warming...");
        preWarmJITCompiler();
        System.err.println("|PersistentJavaRunner.java| [JIT WARMUP] JIT pre-warming completed");

        try (ServerSocket serverSocket = new ServerSocket(8899)) {
            // Set socket options for performance
            serverSocket.setReuseAddress(true);
            serverSocket.setReceiveBufferSize(32768);
            System.err.println("Socket server listening on port 8899");
            
            while (true) {
                try (Socket clientSocket = serverSocket.accept()) {
                    // Optimize socket settings
                    clientSocket.setTcpNoDelay(true);
                    clientSocket.setSoTimeout(30000); // 30 second timeout
                    clientSocket.setReceiveBufferSize(16384);
                    clientSocket.setSendBufferSize(16384);
                    
                    try (BufferedReader reader = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()), 8192);
                         PrintWriter writer = new PrintWriter(clientSocket.getOutputStream(), true)) {
                        
                        System.err.println("Client connected");
                        
                        String requestLine = reader.readLine();
                        if (requestLine != null) {
                            String response = processRequestWithResponse(requestLine);
                            writer.println(response);
                            writer.flush(); // Ensure immediate send
                            System.err.println("Response sent to client");
                        }
                        
                    }
                } catch (Exception e) {
                    System.err.println("Client processing error: " + e.getMessage());
                }
            }
        } catch (IOException e) {
            System.err.println("Server socket error: " + e.getMessage());
        }
    }
    
    private static void preWarmJITCompiler() {
        // Warm up common Java operations that we'll use
        try {
            // Warm up JSON parsing
            String warmupJson = "{\"code\":\"class Solution { public int test() { return 42; } }\",\"test_cases\":[{\"input\":{\"nums\":[1,2,3]}}],\"function_name\":\"test\"}";
            for (int i = 0; i < 5; i++) {
                parseJson(warmupJson);
            }
            
            // Warm up string operations
            String testString = "public class Solution { public int warmup() { return 1; } }";
            for (int i = 0; i < 10; i++) {
                testString.replace("warmup", "test" + i);
                testString.substring(0, testString.length() / 2);
            }
            
            // Warm up compilation infrastructure
            JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
            if (compiler != null) {
                StandardJavaFileManager fileManager = compiler.getStandardFileManager(null, null, null);
                fileManager.close();
            }
            
            // Warm up reflection
            Class.forName("java.lang.String").getMethods();
            
            // Pre-compile common code patterns to warm up compilation cache
            String[] commonPatterns = {
                "class Solution { public int missingNumber(int[] nums) { return 0; } }",
                "class Solution { public int[] twoSum(int[] nums, int target) { return new int[]{0, 1}; } }",
                "class Solution { public boolean isPalindrome(String s) { return true; } }"
            };
            
            for (String pattern : commonPatterns) {
                try {
                    String hash = String.valueOf(pattern.hashCode());
                    UserCodeClassLoader loader = new UserCodeClassLoader(hash, pattern);
                    loader.loadClass("Solution");
                    System.err.println("|PersistentJavaRunner.java| [JIT WARMUP] Pre-compiled pattern: " + pattern.substring(0, 30) + "...");
                } catch (Exception e) {
                    // Ignore warming errors
                }
            }
            
            System.err.println("|PersistentJavaRunner.java| [JIT WARMUP] Basic operations and compilation cache warmed up");
        } catch (Exception e) {
            System.err.println("|PersistentJavaRunner.java| [JIT WARMUP] Warning: " + e.getMessage());
        }
    }
    
    private static String processRequestWithResponse(String requestJson) {
        long totalStart = System.nanoTime();
        System.err.println("|PersistentJavaRunner.java| [SERVER] Processing new request");
        System.err.println("|PersistentJavaRunner.java| [SERVER] Request JSON (first 500 chars): " + requestJson.substring(0, Math.min(500, requestJson.length())));
        
        try {
            // Parse request - expecting format: {"code":"...","test_cases":[...],"function_name":"...","method_signature":...}
            long parseStart = System.nanoTime();
            Map<String, Object> request = parseJson(requestJson);
            String userCode = (String) request.get("code");
            List<Map<String, Object>> testCases = (List<Map<String, Object>>) request.get("test_cases");
            String functionName = (String) request.getOrDefault("function_name", "solution");
            Map<String, Object> methodSignature = (Map<String, Object>) request.get("method_signature");
            long parseTime = (System.nanoTime() - parseStart) / 1_000_000;
            System.err.println("|PersistentJavaRunner.java| [PARSE] Request parsing took " + parseTime + "ms");
            System.err.println("|PersistentJavaRunner.java| [PARSE] Parsed function_name: " + functionName);
            System.err.println("|PersistentJavaRunner.java| [PARSE] Parsed test_cases count: " + (testCases != null ? testCases.size() : "null"));
            System.err.println("|PersistentJavaRunner.java| [PARSE] Parsed method_signature: " + methodSignature);
            
            // Create isolated class loader for user code
            long classLoaderStart = System.nanoTime();
            String codeHash = String.valueOf(userCode.hashCode());
            UserCodeClassLoader classLoader = new UserCodeClassLoader(codeHash, userCode);
            long classLoaderTime = (System.nanoTime() - classLoaderStart) / 1_000_000;
            System.err.println("🔧 [SETUP] ClassLoader setup took " + classLoaderTime + "ms");
            
            // Load user solution class (this triggers compilation)
            long loadStart = System.nanoTime();
            Class<?> solutionClass = classLoader.loadClass("Solution");
            Object solutionInstance = solutionClass.newInstance();
            long loadTime = (System.nanoTime() - loadStart) / 1_000_000;
            System.err.println("|PersistentJavaRunner.java| [LOAD] Class loading + instantiation took " + loadTime + "ms");
            
            // Execute all test cases
            long execStart = System.nanoTime();
            List<Map<String, Object>> results = new ArrayList<>();
            for (int i = 0; i < testCases.size(); i++) {
                Map<String, Object> testCase = testCases.get(i);
                Map<String, Object> result = executeTestCase(solutionInstance, testCase, functionName, methodSignature);
                results.add(result);
                System.err.println("|PersistentJavaRunner.java| [TEST] Test case " + (i+1) + " completed");
            }
            long execTime = (System.nanoTime() - execStart) / 1_000_000;
            System.err.println("|PersistentJavaRunner.java| [EXEC] All test execution took " + execTime + "ms");
            
            long totalTime = (System.nanoTime() - totalStart) / 1_000_000;
            System.err.println("|PersistentJavaRunner.java| [TOTAL] Complete request processing took " + totalTime + "ms");
            
            return toJson(results);
            
        } catch (Exception e) {
            long totalTime = (System.nanoTime() - totalStart) / 1_000_000;
            System.err.println("❌ [ERROR] Request failed after " + totalTime + "ms: " + e.getMessage());
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("error", "Failed to process request: " + e.getMessage());
            return toJson(errorResult);
        }
    }
    
    private static Map<String, Object> executeTestCase(Object solutionInstance, Map<String, Object> testCase, String functionName, Map<String, Object> methodSignature) {
        Map<String, Object> result = new HashMap<>();
        
        try {
            long startTime = System.nanoTime();
            
            // Get input data
            Map<String, Object> input = (Map<String, Object>) testCase.get("input");
            
            // Use universal method resolution
            Object output = callSolutionMethodUniversal(solutionInstance, functionName, input, methodSignature);
            
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            
            result.put("success", true);
            result.put("output", output);
            result.put("execution_time", executionTime);
            result.put("error", null);
            
        } catch (Exception e) {
            result.put("success", false);
            result.put("output", null);
            result.put("execution_time", null);
            result.put("error", e.getMessage());
        }
        
        return result;
    }
    
    private static Object callSolutionMethodUniversal(Object solutionInstance, String functionName, Map<String, Object> input, Map<String, Object> methodSignature) throws Exception {
        System.err.println("|PersistentJavaRunner.java| [PYTHON-STYLE] Calling method: " + functionName + " with input: " + input);
        
        // Python-style approach: Extract ALL parameters from JSON generically
        // No signatures needed! No hardcoded parameter names! Just like Python!
        return callMethodPythonStyle(solutionInstance, functionName, input);
    }
    
    // Python-style method calling - Simple and Universal!
    // This replaces ALL the complex signature/parsing logic with 10 lines
    private static Object callMethodPythonStyle(Object instance, String methodName, Map<String, Object> input) throws Exception {
        Class<?> clazz = instance.getClass();
        
        // Convert all input values to an Object array (like Python does)
        Object[] values = convertInputToArgs(input);
        
        // Try to find a method that matches our argument count and types
        for (java.lang.reflect.Method method : clazz.getMethods()) {
            if (method.getName().equals(methodName) && method.getParameterCount() == values.length) {
                try {
                    System.err.println("|PersistentJavaRunner.java| [PYTHON-STYLE] Trying method: " + method + " with args: " + java.util.Arrays.toString(values));
                    return method.invoke(instance, values);
                } catch (Exception e) {
                    // Try next method signature
                    continue;
                }
            }
        }
        
        throw new RuntimeException("No matching method found for: " + methodName + " with " + values.length + " parameters");
    }
    
    // Simple converter: JSON input → Java method arguments
    // Works for ANY method, just like Python's **kwargs!
    private static Object[] convertInputToArgs(Map<String, Object> input) {
        System.err.println("|PersistentJavaRunner.java| [DEBUG] Converting input to args: " + input);
        List<Object> args = new ArrayList<>();
        
        for (Map.Entry<String, Object> entry : input.entrySet()) {
            String key = entry.getKey();
            Object value = entry.getValue();
            System.err.println("|PersistentJavaRunner.java| [DEBUG] Processing key=" + key + ", value=" + value + ", type=" + value.getClass().getSimpleName());
            
            if (value instanceof List) {
                // Convert List<Number> to int[] (most common case)
                List<?> list = (List<?>) value;
                if (!list.isEmpty() && list.get(0) instanceof Number) {
                    int[] array = list.stream().mapToInt(n -> ((Number) n).intValue()).toArray();
                    System.err.println("|PersistentJavaRunner.java| [DEBUG] Converted list to int[]: " + java.util.Arrays.toString(array));
                    args.add(array);
                } else {
                    System.err.println("|PersistentJavaRunner.java| [DEBUG] Keeping list as-is: " + list);
                    args.add(value); // Keep as-is for other types
                }
            } else if (value instanceof Number) {
                int intValue = ((Number) value).intValue();
                System.err.println("|PersistentJavaRunner.java| [DEBUG] Converted number to int: " + intValue);
                args.add(intValue); // Convert to int
            } else {
                System.err.println("|PersistentJavaRunner.java| [DEBUG] Keeping value as-is: " + value);
                args.add(value); // String, boolean, etc.
            }
        }
        
        Object[] result = args.toArray();
        System.err.println("|PersistentJavaRunner.java| [DEBUG] Final args array: " + java.util.Arrays.toString(result));
        return result;
    }
    
    
    
    
    
    // Simple JSON parsing - handles basic structure
    private static Map<String, Object> parseJson(String json) {
        // This is a simplified parser for our specific use case
        // In production, you'd use a proper JSON library
        Map<String, Object> result = new HashMap<>();
        
        json = json.trim();
        if (json.startsWith("{") && json.endsWith("}")) {
            json = json.substring(1, json.length() - 1);
        }
        
        // Extract each field properly by finding the right boundaries
        result.put("code", extractJsonStringValue(json, "code"));
        result.put("test_cases", parseTestCases(extractJsonValue(json, "test_cases")));
        result.put("function_name", extractJsonStringValue(json, "function_name"));
        // Skip method signature - we don't need it anymore!
        // Python-style approach works without signatures
        result.put("method_signature", null);
        
        return result;
    }
    
    private static String extractJsonStringValue(String json, String key) {
        String keyPattern = "\"" + key + "\"";
        int keyStart = json.indexOf(keyPattern);
        if (keyStart == -1) return null;
        
        int valueStart = json.indexOf(":", keyStart) + 1;
        while (valueStart < json.length() && Character.isWhitespace(json.charAt(valueStart))) {
            valueStart++;
        }
        
        if (valueStart >= json.length() || json.charAt(valueStart) != '"') return null;
        
        // Find the end of the string value, handling escaped quotes
        int valueEnd = valueStart + 1;
        while (valueEnd < json.length()) {
            char c = json.charAt(valueEnd);
            if (c == '"' && json.charAt(valueEnd - 1) != '\\') {
                break;
            }
            valueEnd++;
        }
        
        if (valueEnd >= json.length()) return null;
        
        return json.substring(valueStart + 1, valueEnd);
    }
    
    private static String extractJsonValue(String json, String key) {
        String keyPattern = "\"" + key + "\"";
        int keyStart = json.indexOf(keyPattern);
        if (keyStart == -1) return null;
        
        int valueStart = json.indexOf(":", keyStart) + 1;
        while (valueStart < json.length() && Character.isWhitespace(json.charAt(valueStart))) {
            valueStart++;
        }
        
        if (valueStart >= json.length()) return null;
        
        char startChar = json.charAt(valueStart);
        if (startChar == '[') {
            // Find matching closing bracket
            int depth = 0;
            int valueEnd = valueStart;
            while (valueEnd < json.length()) {
                char c = json.charAt(valueEnd);
                if (c == '[') depth++;
                else if (c == ']') {
                    depth--;
                    if (depth == 0) break;
                }
                valueEnd++;
            }
            return json.substring(valueStart, valueEnd + 1);
        } else if (startChar == '{') {
            // Find matching closing brace
            int depth = 0;
            int valueEnd = valueStart;
            while (valueEnd < json.length()) {
                char c = json.charAt(valueEnd);
                if (c == '{') depth++;
                else if (c == '}') {
                    depth--;
                    if (depth == 0) break;
                }
                valueEnd++;
            }
            return json.substring(valueStart, valueEnd + 1);
        } else {
            // Simple value (string, number, etc.)
            return extractJsonStringValue(json, key);
        }
    }
    
    private static List<Map<String, Object>> parseTestCases(String testCasesStr) {
        System.err.println("|PersistentJavaRunner.java| [TEST CASES] Parsing test cases from: " + testCasesStr.substring(0, Math.min(200, testCasesStr.length())));
        
        // Simple JSON parsing for test cases array
        List<Map<String, Object>> testCases = new ArrayList<>();
        
        String arrayContent;
        
        // Check if this is a full JSON with "test_cases": or just the array part
        if (testCasesStr.contains("\"test_cases\":")) {
            // Full JSON format: "test_cases":[{"input":{"nums":[...], ...}}, ...]
            int startIdx = testCasesStr.indexOf("\"test_cases\":");
            int arrayStart = testCasesStr.indexOf("[", startIdx) + 1;
            int arrayEnd = findMatchingBracket(testCasesStr, arrayStart - 1);
            
            if (arrayEnd == -1) {
                System.err.println("|PersistentJavaRunner.java| [TEST CASES] Could not parse test cases array from full JSON");
                return createDefaultTestCase();
            }
            
            arrayContent = testCasesStr.substring(arrayStart, arrayEnd);
        } else if (testCasesStr.trim().startsWith("[") && testCasesStr.trim().endsWith("]")) {
            // Just the array part: [{"input":{"nums":[...], ...}}, ...]
            String trimmed = testCasesStr.trim();
            arrayContent = trimmed.substring(1, trimmed.length() - 1);
        } else {
            System.err.println("|PersistentJavaRunner.java| [TEST CASES] Unrecognized format, creating default");
            return createDefaultTestCase();
        }
        
        System.err.println("|PersistentJavaRunner.java| [TEST CASES] Array content: " + arrayContent.substring(0, Math.min(100, arrayContent.length())) + "...");
        
        // Split by test case objects - look for {"input":
        String[] parts = arrayContent.split("\\{\"input\":");
        
        for (int i = 1; i < parts.length; i++) { // Skip first empty part
            String part = parts[i];
            
            // Find the input object
            int inputEnd = findMatchingBrace(part, 0);
            if (inputEnd == -1) continue;
            
            String inputStr = part.substring(0, inputEnd + 1);
            
            Map<String, Object> testCase = new HashMap<>();
            Map<String, Object> input = parseInputObject(inputStr);
            testCase.put("input", input);
            testCases.add(testCase);
        }
        
        System.err.println("|PersistentJavaRunner.java| [TEST CASES] Parsed " + testCases.size() + " test cases");
        return testCases;
    }
    
    private static List<Map<String, Object>> createDefaultTestCase() {
        List<Map<String, Object>> testCases = new ArrayList<>();
        Map<String, Object> testCase = new HashMap<>();
        Map<String, Object> input = new HashMap<>();
        input.put("nums", Arrays.asList(3, 0, 1));
        testCase.put("input", input);
        testCases.add(testCase);
        System.err.println("|PersistentJavaRunner.java| [TEST CASES] Created default test case");
        return testCases;
    }
    
    private static int findMatchingBracket(String str, int startIdx) {
        int depth = 0;
        for (int i = startIdx; i < str.length(); i++) {
            char c = str.charAt(i);
            if (c == '[') depth++;
            else if (c == ']') {
                depth--;
                if (depth == 0) return i;
            }
        }
        return -1;
    }
    
    private static int findMatchingBrace(String str, int startIdx) {
        int depth = 0;
        for (int i = startIdx; i < str.length(); i++) {
            char c = str.charAt(i);
            if (c == '{') depth++;
            else if (c == '}') {
                depth--;
                if (depth == 0) return i;
            }
        }
        return -1;
    }
    
    // Simple generic JSON object parsing - works for ANY input!
    // No hardcoded "nums" or "target" - just like Python!
    private static Map<String, Object> parseInputObject(String inputStr) {
        Map<String, Object> input = new HashMap<>();
        
        System.err.println("|PersistentJavaRunner.java| [SIMPLE PARSE] Parsing input: " + inputStr);
        
        // Generic key-value extraction using regex patterns
        // This works for {"x": 121}, {"nums": [1,2], "target": 3}, etc.
        String content = inputStr.trim();
        if (content.startsWith("{") && content.endsWith("}")) {
            content = content.substring(1, content.length() - 1);
        }
        
        // Split by commas but respect arrays and nested objects
        String[] pairs = splitKeyValuePairs(content);
        
        for (String pair : pairs) {
            int colonIndex = pair.indexOf(":");
            if (colonIndex > 0) {
                String key = pair.substring(0, colonIndex).trim().replace("\"", "");
                String valueStr = pair.substring(colonIndex + 1).trim();
                
                Object value = parseGenericValue(valueStr);
                input.put(key, value);
            }
        }
        
        System.err.println("|PersistentJavaRunner.java| [SIMPLE PARSE] Result: " + input);
        return input;
    }
    
    // Generic value parser - handles arrays, numbers, strings, booleans
    private static Object parseGenericValue(String valueStr) {
        valueStr = valueStr.trim();
        
        if (valueStr.startsWith("[") && valueStr.endsWith("]")) {
            // Array parsing
            String arrayContent = valueStr.substring(1, valueStr.length() - 1);
            String[] elements = arrayContent.split(",");
            List<Object> list = new ArrayList<>();
            
            for (String element : elements) {
                element = element.trim();
                if (element.matches("-?\\d+")) {
                    list.add(Integer.parseInt(element));
                } else if (element.startsWith("\"") && element.endsWith("\"")) {
                    list.add(element.substring(1, element.length() - 1));
                } else {
                    list.add(element);
                }
            }
            return list;
        } else if (valueStr.startsWith("\"") && valueStr.endsWith("\"")) {
            // String value
            return valueStr.substring(1, valueStr.length() - 1);
        } else if (valueStr.matches("-?\\d+")) {
            // Integer value
            return Integer.parseInt(valueStr);
        } else if ("true".equals(valueStr) || "false".equals(valueStr)) {
            // Boolean value
            return Boolean.parseBoolean(valueStr);
        } else {
            // Default to string
            return valueStr;
        }
    }
    
    // Split key-value pairs respecting arrays and nested structures
    private static String[] splitKeyValuePairs(String content) {
        List<String> pairs = new ArrayList<>();
        int start = 0;
        int depth = 0;
        boolean inString = false;
        
        for (int i = 0; i < content.length(); i++) {
            char c = content.charAt(i);
            
            if (c == '\"' && (i == 0 || content.charAt(i-1) != '\\')) {
                inString = !inString;
            } else if (!inString) {
                if (c == '[' || c == '{') {
                    depth++;
                } else if (c == ']' || c == '}') {
                    depth--;
                } else if (c == ',' && depth == 0) {
                    pairs.add(content.substring(start, i));
                    start = i + 1;
                }
            }
        }
        
        if (start < content.length()) {
            pairs.add(content.substring(start));
        }
        
        return pairs.toArray(new String[0]);
    }
    
    // Cache management methods
    private static void logCacheStats() {
        System.err.println("|PersistentJavaRunner.java| [CACHE STATS] Size: " + COMPILED_CLASS_CACHE.size() + " classes cached");
    }
    
    private static void evictOldestIfNeeded() {
        if (COMPILED_CLASS_CACHE.size() >= MAX_CACHE_SIZE) {
            // Simple eviction - remove first entry (could improve with LRU later)
            String oldestKey = COMPILED_CLASS_CACHE.keySet().iterator().next();
            COMPILED_CLASS_CACHE.remove(oldestKey);
            BYTECODE_CACHE.remove(oldestKey);
            System.err.println("|PersistentJavaRunner.java| [CACHE EVICT] Removed oldest entry: " + oldestKey);
        }
    }
    
    private static String toJson(Object obj) {
        if (obj instanceof List) {
            List<?> list = (List<?>) obj;
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < list.size(); i++) {
                if (i > 0) sb.append(",");
                sb.append(toJson(list.get(i)));
            }
            sb.append("]");
            return sb.toString();
        } else if (obj instanceof Map) {
            Map<?, ?> map = (Map<?, ?>) obj;
            StringBuilder sb = new StringBuilder("{");
            boolean first = true;
            for (Map.Entry<?, ?> entry : map.entrySet()) {
                if (!first) sb.append(",");
                sb.append("\"").append(entry.getKey()).append("\":");
                sb.append(toJson(entry.getValue()));
                first = false;
            }
            sb.append("}");
            return sb.toString();
        } else if (obj instanceof String) {
            return "\"" + obj.toString().replace("\"", "\\\"") + "\"";
        } else if (obj instanceof int[]) {
            int[] arr = (int[]) obj;
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < arr.length; i++) {
                if (i > 0) sb.append(",");
                sb.append(arr[i]);
            }
            sb.append("]");
            return sb.toString();
        } else if (obj == null) {
            return "null";
        } else {
            return obj.toString();
        }
    }
    
    // Custom class loader for isolating user code
    private static class UserCodeClassLoader extends ClassLoader {
        private final String codeHash;
        private final String userCode;
        
        public UserCodeClassLoader(String codeHash, String userCode) {
            super(ClassLoader.getSystemClassLoader());
            this.codeHash = codeHash;
            this.userCode = userCode;
        }
        
        @Override
        protected Class<?> findClass(String name) throws ClassNotFoundException {
            if ("Solution".equals(name)) {
                // Check cache first using the codeHash
                if (COMPILED_CLASS_CACHE.containsKey(codeHash)) {
                    System.err.println("|PersistentJavaRunner.java| [CACHE HIT] Using cached class for hash: " + codeHash);
                    logCacheStats();
                    // Return cached bytecode to defineClass
                    byte[] cachedBytes = BYTECODE_CACHE.get(codeHash);
                    return defineClass(name, cachedBytes, 0, cachedBytes.length);
                }
                
                // Cache miss - compile and cache
                System.err.println("|PersistentJavaRunner.java| [CACHE MISS] Compiling new class for hash: " + codeHash);
                try {
                    // Compile user code - fix escaped newlines from JSON
                    String cleanUserCode = userCode.replace("\\n", "\n").replace("\\t", "\t").replace("\\\"", "\"");
                    // Ensure Solution class is public for reflection access
                    String publicUserCode = cleanUserCode.replace("class Solution", "public class Solution");
                    String fullCode = "import java.util.*;\n" + publicUserCode;
                    
                    byte[] classBytes = compileCode("Solution", fullCode);
                    Class<?> compiledClass = defineClass(name, classBytes, 0, classBytes.length);
                    
                    // Cache both bytecode and class (with eviction check)
                    evictOldestIfNeeded();
                    BYTECODE_CACHE.put(codeHash, classBytes);
                    COMPILED_CLASS_CACHE.put(codeHash, compiledClass);
                    
                    System.err.println("|PersistentJavaRunner.java| [CACHED] Stored compiled class for hash: " + codeHash);
                    logCacheStats();
                    return compiledClass;
                } catch (Exception e) {
                    throw new ClassNotFoundException("Failed to compile user code", e);
                }
            }
            return super.findClass(name);
        }
        
        private byte[] compileCode(String className, String code) throws Exception {
            long compileStart = System.nanoTime();
            System.err.println("|PersistentJavaRunner.java| [COMPILE] Starting optimized in-memory compilation for " + className);
            
            // Get the Java compiler
            JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
            if (compiler == null) {
                throw new RuntimeException("No Java compiler available");
            }
            
            // Create in-memory file manager
            StandardJavaFileManager fileManager = compiler.getStandardFileManager(null, null, null);
            InMemoryFileManager memoryFileManager = new InMemoryFileManager(fileManager);
            
            // Create source file object
            JavaFileObject sourceFile = new InMemoryJavaFileObject(className, code);
            
            // Optimized compiler options for faster compilation
            List<String> options = Arrays.asList(
                "-g:none",           // Don't generate debug info
                "-nowarn",           // Suppress warnings
                "-Xlint:none",       // Disable all lint warnings
                "-proc:none"         // Disable annotation processing
            );
            
            // Compile with optimizations
            JavaCompiler.CompilationTask task = compiler.getTask(
                null, // Writer for additional output
                memoryFileManager, // File manager
                null, // Diagnostic listener  
                options, // Compiler options for speed
                null, // Classes for annotation processing
                Arrays.asList(sourceFile) // Source files
            );
            
            boolean success = task.call();
            if (!success) {
                throw new RuntimeException("Optimized in-memory compilation failed");
            }
            
            // Get compiled bytecode
            byte[] classBytes = memoryFileManager.getCompiledClass(className);
            if (classBytes == null) {
                throw new RuntimeException("No bytecode generated for " + className);
            }
            
            long compileTime = (System.nanoTime() - compileStart) / 1_000_000;
            System.err.println("|PersistentJavaRunner.java| [COMPILE] Optimized compilation completed in " + compileTime + "ms");
            
            return classBytes;
        }
    }
    
    // In-memory file manager for compilation
    private static class InMemoryFileManager extends ForwardingJavaFileManager<StandardJavaFileManager> {
        private final Map<String, InMemoryClassFile> compiledClasses = new HashMap<>();
        
        public InMemoryFileManager(StandardJavaFileManager fileManager) {
            super(fileManager);
        }
        
        @Override
        public JavaFileObject getJavaFileForOutput(Location location, String className,
                JavaFileObject.Kind kind, FileObject sibling) throws IOException {
            if (kind == JavaFileObject.Kind.CLASS) {
                InMemoryClassFile classFile = new InMemoryClassFile(className);
                compiledClasses.put(className, classFile);
                return classFile;
            }
            return super.getJavaFileForOutput(location, className, kind, sibling);
        }
        
        public byte[] getCompiledClass(String className) {
            InMemoryClassFile classFile = compiledClasses.get(className);
            return classFile != null ? classFile.getBytes() : null;
        }
    }
    
    // In-memory source file
    private static class InMemoryJavaFileObject extends SimpleJavaFileObject {
        private final String code;
        
        public InMemoryJavaFileObject(String className, String code) {
            super(URI.create("string:///" + className.replace('.', '/') + Kind.SOURCE.extension), Kind.SOURCE);
            this.code = code;
        }
        
        @Override
        public CharSequence getCharContent(boolean ignoreEncodingErrors) {
            return code;
        }
    }
    
    // In-memory class file for compiled output
    private static class InMemoryClassFile extends SimpleJavaFileObject {
        private final ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        
        public InMemoryClassFile(String className) {
            super(URI.create("mem:///" + className.replace('.', '/') + Kind.CLASS.extension), Kind.CLASS);
        }
        
        @Override
        public OutputStream openOutputStream() throws IOException {
            return outputStream;
        }
        
        public byte[] getBytes() {
            return outputStream.toByteArray();
        }
    }
}