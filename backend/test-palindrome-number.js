#!/usr/bin/env node

/**
 * Quick test for palindrome-number to verify signature fixes
 */

const fs = require('fs');

const API_BASE_URL = 'http://localhost:8000';

async function testPalindromeNumber() {
    console.log('🧪 Testing palindrome-number with fixed signatures...\n');
    
    // Test data
    const questionSlug = 'palindrome-number';
    const language = 'java';
    
    // Simple solution for testing
    const solution = `
class Solution {
    public boolean isPalindrome(int x) {
        if (x < 0) return false;
        if (x < 10) return true;
        
        int original = x;
        int reversed = 0;
        
        while (x > 0) {
            reversed = reversed * 10 + x % 10;
            x /= 10;
        }
        
        return original == reversed;
    }
}`;
    
    console.log(`Testing ${language}...`);
    
    try {
        const fetch = (await import('node-fetch')).default;
        const response = await fetch(`${API_BASE_URL}/api/${questionSlug}/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                player_id: "test_runner",
                code: solution,
                language: language,
                question_name: questionSlug,
                timeout: 10,
                timer: 0
            }),
            timeout: 30000
        });

        if (!response.ok) {
            console.log(`  ❌ ${language}: HTTP ${response.status}: ${response.statusText}`);
            return;
        }

        const result = await response.json();
        console.log(`     Raw result:`, JSON.stringify(result, null, 2));
        
        if (result.success && result.total_passed === result.total_tests) {
            console.log(`  ✅ ${language}: PASS (${result.total_passed}/${result.total_tests} tests)`);
        } else {
            console.log(`  ❌ ${language}: FAIL - ${result.total_passed}/${result.total_tests} tests passed`);
            if (result.error) {
                console.log(`     Error: ${result.error}`);
            }
            if (result.test_results) {
                result.test_results.forEach((test, index) => {
                    if (!test.passed) {
                        console.log(`     Test ${index + 1} failed: expected ${test.expected_output}, got ${test.actual_output}`);
                        if (test.error) {
                            console.log(`     Test error: ${test.error}`);
                        }
                    }
                });
            }
        }
    } catch (error) {
        console.log(`  ❌ ${language}: ERROR - ${error.message}`);
    }
}

testPalindromeNumber().catch(console.error);