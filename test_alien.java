import java.util.*;

class TestAlien {
    public static void main(String[] args) {
        // Test the exact same code that would be generated
        String inputJson = "{\"words\":[\"z\",\"x\"]}";
        
        try {
            System.out.println("Testing JSON: " + inputJson);
            
            if (inputJson.contains("\"words\"")) {
                System.out.println("Found words key");
                java.util.List<String> wordsList = extractStringList(inputJson, "words");
                System.out.println("Extracted list: " + wordsList);
                String[] words = wordsList.toArray(new String[0]);
                System.out.println("Converted to array: " + java.util.Arrays.toString(words));
                
                // Test calling the method
                TestSolution sol = new TestSolution();
                String result = sol.alienOrder(words);
                System.out.println("Result: " + result);
            }
            
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    private static java.util.List<String> extractStringList(String json, String key) {
        String pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]+)\\]";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            String arrayContent = m.group(1);
            String[] elements = arrayContent.split(",");
            java.util.List<String> result = new java.util.ArrayList<>();
            for (int i = 0; i < elements.length; i++) {
                String element = elements[i].trim();
                // Remove quotes from string elements
                if (element.startsWith("\"") && element.endsWith("\"")) {
                    element = element.substring(1, element.length() - 1);
                }
                result.add(element);
            }
            return result;
        }
        return new java.util.ArrayList<>();
    }
}

class TestSolution {
    public String alienOrder(String[] words) {
        System.out.println("alienOrder called with: " + java.util.Arrays.toString(words));
        return "zx";
    }
}
