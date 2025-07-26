#!/bin/bash

echo "🧪 Testing missing-number performance with new Java batch runner..."

# Java solution for missing-number
JAVA_CODE='class Solution {
    public int missingNumber(int[] nums) {
        int n = nums.length;
        int expectedSum = n * (n + 1) / 2;
        int actualSum = 0;
        for (int num : nums) {
            actualSum += num;
        }
        return expectedSum - actualSum;
    }
}'

# Test the /run endpoint
echo "Making request to test missing-number..."

START_TIME=$(python3 -c "import time; print(int(time.time() * 1000))")

curl -X POST "http://localhost:8001/api/run-test-cases" \
  -H "Content-Type: application/json" \
  -d "{
    \"code\": \"$JAVA_CODE\",
    \"language\": \"java\",
    \"question_name\": \"missing-number\"
  }" -s | python3 -m json.tool

END_TIME=$(python3 -c "import time; print(int(time.time() * 1000))")
TOTAL_TIME=$((END_TIME - START_TIME))

echo ""
echo "🚀 Total request time: ${TOTAL_TIME}ms"

if [ $TOTAL_TIME -lt 1000 ]; then
    echo "✅ Performance target achieved! (<1000ms)"
else
    echo "❌ Still slow (target: <1000ms)"
fi