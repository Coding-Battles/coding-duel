#!/usr/bin/env node

/**
 * Quick test for missing-number to verify batch runner fixes
 */

const fs = require('fs');

const API_BASE_URL = 'http://localhost:8000';

async function testMissingNumber() {
    console.log('🧪 Testing missing-number with fixed batch runners...\n');
    
    // Test data
    const questionSlug = 'missing-number';
    const languages = ['python', 'java', 'cpp'];
    
    // Read our solution
    const solutions = {
        python: fs.readFileSync('/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/test-solutions/missing-number.py', 'utf8'),
        java: fs.readFileSync('/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/test-solutions/missing-number.java', 'utf8'),
        cpp: fs.readFileSync('/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/test-solutions/missing-number.cpp', 'utf8')
    };
    
    for (const language of languages) {
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
                    code: solutions[language],
                    language: language,
                    question_name: questionSlug,
                    timeout: 10,
                    timer: 0
                }),
                timeout: 30000
            });

            if (!response.ok) {
                console.log(`  ❌ ${language}: HTTP ${response.status}: ${response.statusText}`);
                continue;
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
            }
        } catch (error) {
            console.log(`  ❌ ${language}: ERROR - ${error.message}`);
        }
    }
}

testMissingNumber().catch(console.error);