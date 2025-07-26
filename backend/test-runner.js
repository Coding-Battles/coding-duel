#!/usr/bin/env node

/**
 * Automated Test Runner for Coding Duel
 * Tests all questions across all languages with working solutions
 */

const fs = require('fs');
const path = require('path');

// Configuration
const API_BASE_URL = 'http://localhost:8000';
const SOLUTIONS_DIR = path.join(__dirname, 'test-solutions');
const QUESTIONS_FILE = path.join(__dirname, 'data', 'questions.json');

// Language configuration
const LANGUAGES = {
    python: { ext: 'py', name: 'Python' },
    javascript: { ext: 'js', name: 'JavaScript' },
    java: { ext: 'java', name: 'Java' },
    cpp: { ext: 'cpp', name: 'C++' }
};

class TestRunner {
    constructor() {
        this.totalTests = 0;
        this.passedTests = 0;
        this.failures = [];
        this.startTime = Date.now();
    }

    async run() {
        console.log('🚀 Coding Duel Automated Test Runner');
        console.log('=====================================\n');

        // Health check
        if (!(await this.healthCheck())) {
            console.error('❌ Backend server not available at', API_BASE_URL);
            console.error('❌ Make sure to start the backend server first: npm run dev');
            process.exit(1);
        }

        // Load questions and filter for those with solutions
        const allQuestions = this.loadQuestions();
        const questionsWithSolutions = this.filterQuestionsWithSolutions(allQuestions);
        
        console.log(`📝 Found ${allQuestions.length} total questions`);
        console.log(`✅ Testing ${questionsWithSolutions.length} questions with solutions`);
        console.log(`🔧 Testing ${Object.keys(LANGUAGES).length} languages`);
        console.log(`🎯 Total test combinations: ${questionsWithSolutions.length * Object.keys(LANGUAGES).length}\n`);

        if (questionsWithSolutions.length === 0) {
            console.error('❌ No questions found with complete solution sets');
            console.error('📁 Please add solution files to:', SOLUTIONS_DIR);
            process.exit(1);
        }

        // Run tests
        for (const question of questionsWithSolutions) {
            console.log(`Testing ${question.slug}...`);
            
            for (const [langKey, langConfig] of Object.entries(LANGUAGES)) {
                await this.testQuestionLanguage(question, langKey, langConfig);
            }
            console.log(''); // Empty line between questions
        }

        // Final summary
        this.printSummary();
        process.exit(this.failures.length > 0 ? 1 : 0);
    }

    async healthCheck() {
        try {
            const fetch = (await import('node-fetch')).default;
            const response = await fetch(`${API_BASE_URL}/api/health`, {
                timeout: 5000
            });
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    loadQuestions() {
        try {
            const questionsData = JSON.parse(fs.readFileSync(QUESTIONS_FILE, 'utf8'));
            
            // Flatten all questions from all difficulty levels
            const allQuestions = [];
            for (const [difficulty, questions] of Object.entries(questionsData.questions)) {
                allQuestions.push(...questions);
            }
            
            return allQuestions.sort((a, b) => parseInt(a.id) - parseInt(b.id));
        } catch (error) {
            console.error('❌ Failed to load questions:', error.message);
            process.exit(1);
        }
    }

    filterQuestionsWithSolutions(questions) {
        return questions.filter(question => {
            // Check if all 4 languages have solution files
            for (const [langKey, langConfig] of Object.entries(LANGUAGES)) {
                const solutionPath = path.join(SOLUTIONS_DIR, `${question.slug}.${langConfig.ext}`);
                if (!fs.existsSync(solutionPath)) {
                    return false;
                }
            }
            return true;
        });
    }

    async testQuestionLanguage(question, langKey, langConfig) {
        this.totalTests++;
        
        try {
            // Load solution
            const solution = this.loadSolution(question.slug, langKey, langConfig.ext);
            if (!solution) {
                this.recordFailure(question.slug, langKey, 'Solution file not found');
                return;
            }

            // Test solution
            const result = await this.executeTest(question.slug, solution, langKey);
            
            if (result.success && result.allTestsPassed) {
                console.log(`  ✅ ${langConfig.name}: PASS (${result.totalPassed}/${result.totalTests} tests, ${result.executionTime}ms)`);
                this.passedTests++;
            } else {
                const reason = result.error || `${result.totalPassed}/${result.totalTests} tests passed`;
                console.log(`  ❌ ${langConfig.name}: FAIL - ${reason}`);
                this.recordFailure(question.slug, langKey, reason);
            }
        } catch (error) {
            console.log(`  ❌ ${langConfig.name}: FAIL - ${error.message}`);
            this.recordFailure(question.slug, langKey, error.message);
        }
    }

    loadSolution(questionSlug, langKey, extension) {
        const solutionPath = path.join(SOLUTIONS_DIR, `${questionSlug}.${extension}`);
        
        try {
            return fs.readFileSync(solutionPath, 'utf8');
        } catch (error) {
            return null;
        }
    }

    async executeTest(questionSlug, code, language) {
        const fetch = (await import('node-fetch')).default;
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/${questionSlug}/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    player_id: "test_runner",
                    code: code,
                    language: language,
                    question_name: questionSlug,
                    timeout: 10,
                    timer: 0
                }),
                timeout: 30000 // 30 second timeout
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            return {
                success: result.success,
                allTestsPassed: result.success && result.totalPassed === result.totalTests,
                totalPassed: result.totalPassed || 0,
                totalTests: result.totalTests || 0,
                executionTime: Math.round(result.totalTime || 0),
                error: result.error || null
            };
        } catch (error) {
            throw new Error(`API Error: ${error.message}`);
        }
    }

    recordFailure(questionSlug, language, reason) {
        this.failures.push({
            question: questionSlug,
            language: language,
            reason: reason
        });
    }

    printSummary() {
        const executionTime = Math.round((Date.now() - this.startTime) / 1000);
        const successRate = ((this.passedTests / this.totalTests) * 100).toFixed(1);
        
        console.log('\n=====================================');
        console.log('FINAL SUMMARY');
        console.log('=====================================');
        
        if (this.failures.length === 0) {
            console.log(`✅ OVERALL RESULT: ${this.passedTests}/${this.totalTests} tests PASSED`);
        } else {
            console.log(`❌ OVERALL RESULT: ${this.passedTests}/${this.totalTests} tests PASSED`);
            console.log(`\n❌ FAILURES (${this.failures.length}):`);
            
            for (const failure of this.failures) {
                console.log(`  - ${failure.question} (${failure.language}): ${failure.reason}`);
            }
        }
        
        console.log(`📊 Questions tested: ${this.totalTests / Object.keys(LANGUAGES).length}`);
        console.log(`🔧 Languages tested: ${Object.keys(LANGUAGES).length}`);
        console.log(`⏱️  Total execution time: ${executionTime}s`);
        console.log(`🎯 Success rate: ${successRate}%`);
        console.log('=====================================');
    }
}

// Run the test suite if called directly
if (require.main === module) {
    const runner = new TestRunner();
    runner.run().catch(error => {
        console.error('❌ Test runner failed:', error);
        process.exit(1);
    });
}

module.exports = TestRunner;