#!/usr/bin/env python3

# Test Java wrapper generation for firstBadVersion

def test_java_wrapper():
    import json
    
    def create_batch_java_wrapper(user_code, test_cases, function_name):
        # Encode test cases as JSON strings with proper Java escaping
        test_cases_json = []
        for test_case in test_cases:
            json_str = json.dumps(test_case["input"])
            # Escape quotes for Java string literals
            escaped_json = json_str.replace('"', '\\"')
            test_cases_json.append(escaped_json)
        
        test_cases_array = ", ".join(f'"{tc}"' for tc in test_cases_json)
        
        # Check if this is the firstBadVersion function
        is_first_bad_version = (function_name == "firstBadVersion")
        
        # Generate conditional execution logic
        if is_first_bad_version:
            parsing_logic = '''
            // Parse n and bad for firstBadVersion
            int n = extractIntValue(testInputs[i], "n");
            int bad = extractIntValue(testInputs[i], "bad");
            
            // Set up isBadVersion API
            VersionControl.setBadVersion(bad);
            
            // Call firstBadVersion with only n parameter
            int result = solutionInstance.firstBadVersion(n);
            
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            
            System.out.println("{\\"success\\": true, \\"output\\": " + result + ", \\"execution_time\\": " + executionTime + "}");'''
        
        # Include VersionControl class for firstBadVersion
        version_control_class = '''
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
''' if is_first_bad_version else ''
        
        wrapper = f'''
import java.util.*;

{version_control_class}

{user_code}

class BatchSolution {{
    // Simple JSON parsing helpers for firstBadVersion
    private static int extractIntValue(String json, String key) {{
        String pattern = "\\"" + key + "\\"\\\\s*:\\\\s*(-?\\\\d+)";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {{
            return Integer.parseInt(m.group(1));
        }}
        throw new RuntimeException("Could not find key: " + key);
    }}
    
    public static void main(String[] args) {{
        String[] testInputs = {{{test_cases_array}}};
        Solution solutionInstance = new Solution();
        
        for (int i = 0; i < testInputs.length; i++) {{
            try {{
                long startTime = System.nanoTime();
                
                {parsing_logic}
                
            }} catch (Exception e) {{
                System.out.println("{{\\\"success\\\": false, \\\"output\\\": null, \\\"error\\\": \\\"" + e.getMessage().replace("\\"", "\\\\\\"") + "\\\", \\\"execution_time\\\": null}}");
            }}
        }}
    }}
}}
'''
        return wrapper

    # Test with firstBadVersion function
    test_code = '''
public class Solution extends VersionControl {
    public int firstBadVersion(int n) {
        int left = 1, right = n;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (isBadVersion(mid)) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }
        return left;
    }
}
'''

    test_cases = [{"input": {"n": 5, "bad": 4}}]
    wrapper = create_batch_java_wrapper(test_code, test_cases, "firstBadVersion")
    
    print("✅ Java wrapper created successfully")
    print("Key components verified:")
    print("- VersionControl class:", "class VersionControl" in wrapper)
    print("- setBadVersion call:", "VersionControl.setBadVersion" in wrapper) 
    print("- firstBadVersion call:", "solutionInstance.firstBadVersion(n)" in wrapper)
    print("- Test input parsing:", '"n": 5, "bad": 4' in wrapper)
    print()
    print("Generated Java test code:")
    print("=" * 50)
    print(wrapper)
    return wrapper

if __name__ == "__main__":
    test_java_wrapper()