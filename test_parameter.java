import java.util.*;

class TestParameter {
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

    public static void main(String[] args) {
        String test1 = "{\"words\":[\"wrt\",\"wrf\",\"er\",\"ett\",\"rftt\"]}";
        String test2 = "{\"words\":[\"z\",\"x\"]}";
        
        System.out.println("Test 1: " + test1);
        java.util.List<String> words1 = extractStringList(test1, "words");
        System.out.println("Extracted: " + words1);
        String[] array1 = words1.toArray(new String[0]);
        System.out.println("Array: " + java.util.Arrays.toString(array1));
        
        System.out.println("\nTest 2: " + test2);
        java.util.List<String> words2 = extractStringList(test2, "words");
        System.out.println("Extracted: " + words2);
        String[] array2 = words2.toArray(new String[0]);
        System.out.println("Array: " + java.util.Arrays.toString(array2));
    }
}
