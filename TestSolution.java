import java.util.*;
import java.lang.reflect.*;


class Solution {
    public int[] twoSum(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++) {
            for (int j = i + 1; j < nums.length; j++) {
                if (nums[i] + nums[j] == target) {
                    return new int[]{i, j};
                }
            }
        }
        return new int[]{};
    }
}


class Main {
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("{\"result\": \"Missing arguments\", \"execution_time\": 0}");
            return;
        }
        
        String methodName = args[0];
        String inputJson = args[1];
        long startTime = System.nanoTime();
        
        try {
            Solution sol = new Solution();
            
            // Super basic parameter extraction - just get it working
            if (methodName.equals("twoSum")) {
                // Parse target and nums array manually
                int target = 0;
                int[] nums = new int[0];
                
                // Extract target
                String[] parts = inputJson.split("target\":");
                if (parts.length > 1) {
                    String targetPart = parts[1].trim();
                    target = Integer.parseInt(targetPart.split("[,}]")[0].trim());
                }
                
                // Extract nums array
                parts = inputJson.split("nums\":");
                if (parts.length > 1) {
                    String arrayPart = parts[1].split("\\[")[1].split("\\]")[0];
                    String[] numStrings = arrayPart.split(",");
                    nums = new int[numStrings.length];
                    for (int i = 0; i < numStrings.length; i++) {
                        nums[i] = Integer.parseInt(numStrings[i].trim());
                    }
                }
                
                int[] result = sol.twoSum(nums, target);
                System.out.println("{\"result\": [" + result[0] + "," + result[1] + "], \"execution_time\": 1}");
            }
            else {
                System.out.println("{\"result\": \"Method not supported: " + methodName + "\", \"execution_time\": 0}");
            }
            
        } catch (Exception e) {
            System.out.println("{\"result\": \"Error: " + e.getMessage() + "\", \"execution_time\": 0}");
        }
    }
}
