#!/usr/bin/env node

/**
 * Comprehensive Test Runner for Coding Duel Frontend
 * 
 * This script provides a convenient interface to run different types of tests
 * with various options and configurations.
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function logSuccess(message) {
  log(`✅ ${message}`, colors.green);
}

function logError(message) {
  log(`❌ ${message}`, colors.red);
}

function logInfo(message) {
  log(`ℹ️  ${message}`, colors.blue);
}

function logWarning(message) {
  log(`⚠️  ${message}`, colors.yellow);
}

function execCommand(command, options = {}) {
  try {
    logInfo(`Running: ${command}`);
    const result = execSync(command, {
      stdio: 'inherit',
      cwd: process.cwd(),
      ...options
    });
    return { success: true, result };
  } catch (error) {
    logError(`Command failed: ${command}`);
    return { success: false, error };
  }
}

function checkDependencies() {
  logInfo('Checking dependencies...');
  
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  const requiredDeps = [
    'vitest',
    '@playwright/test', 
    '@testing-library/react',
    'msw'
  ];
  
  const missingDeps = requiredDeps.filter(dep => 
    !packageJson.devDependencies?.[dep] && !packageJson.dependencies?.[dep]
  );
  
  if (missingDeps.length > 0) {
    logError(`Missing required dependencies: ${missingDeps.join(', ')}`);
    logInfo('Run: npm install');
    return false;
  }
  
  logSuccess('All dependencies are installed');
  return true;
}

function runUnitTests(options = {}) {
  log('\n🧪 Running Unit Tests', colors.cyan);
  log('=' .repeat(50), colors.cyan);
  
  let command = 'npm run test';
  
  if (options.run) {
    command = 'npm run test:run';
  }
  
  if (options.coverage) {
    command = 'npm run test:coverage';
  }
  
  if (options.ui) {
    command = 'npm run test:ui';
  }
  
  if (options.filter) {
    command += ` -- --testNamePattern="${options.filter}"`;
  }
  
  if (options.file) {
    command += ` ${options.file}`;
  }
  
  const result = execCommand(command);
  
  if (result.success) {
    logSuccess('Unit tests completed successfully');
  } else {
    logError('Unit tests failed');
  }
  
  return result.success;
}

function runE2ETests(options = {}) {
  log('\n🎭 Running E2E Tests', colors.magenta);
  log('=' .repeat(50), colors.magenta);
  
  // Check if frontend server is running
  try {
    execSync('curl -f http://localhost:3000 > /dev/null 2>&1');
    logInfo('Frontend server is running');
  } catch (error) {
    logWarning('Frontend server may not be running. E2E tests might fail.');
    logInfo('Start server with: npm run dev');
  }
  
  let command = 'playwright test';
  
  if (options.ui) {
    command += ' --ui';
  }
  
  if (options.headed) {
    command += ' --headed';
  }
  
  if (options.debug) {
    command += ' --debug';
  }
  
  if (options.filter) {
    command += ` --grep="${options.filter}"`;
  }
  
  if (options.project) {
    command += ` --project=${options.project}`;
  }
  
  const result = execCommand(`npx ${command}`);
  
  if (result.success) {
    logSuccess('E2E tests completed successfully');
  } else {
    logError('E2E tests failed');
  }
  
  return result.success;
}

function runSolutionTests() {
  log('\n🔧 Testing All Language Solutions', colors.yellow);
  log('=' .repeat(50), colors.yellow);
  
  const questions = ['two-sum', 'add-two-numbers', 'longest-substring-without-repeating-characters'];
  const languages = ['python', 'javascript', 'java', 'cpp'];
  
  logInfo(`Testing ${questions.length} questions × ${languages.length} languages = ${questions.length * languages.length} combinations`);
  
  const result = execCommand('npm run test:run -- --testNamePattern="Solution.*"');
  
  if (result.success) {
    logSuccess('All solution tests passed!');
    log('\n📊 Solution Test Summary:', colors.green);
    questions.forEach(question => {
      languages.forEach(language => {
        log(`  ✅ ${question} (${language})`, colors.green);
      });
    });
  } else {
    logError('Some solution tests failed');
  }
  
  return result.success;
}

function runGameFlowTests() {
  log('\n🎮 Testing Complete Game Flow', colors.blue);
  log('=' .repeat(50), colors.blue);
  
  logInfo('Testing complete game experience...');
  
  const result = execCommand('npx playwright test --grep="Complete Game Flow"');
  
  if (result.success) {
    logSuccess('Game flow tests passed!');
  } else {
    logError('Game flow tests failed');
  }
  
  return result.success;
}

function runPerformanceTests() {
  log('\n⚡ Running Performance Tests', colors.cyan);
  log('=' .repeat(50), colors.cyan);
  
  const result = execCommand('npm run test:run -- --testNamePattern="Performance.*"');
  
  if (result.success) {
    logSuccess('Performance tests completed');
  } else {
    logError('Performance tests failed');
  }
  
  return result.success;
}

function generateTestReport() {
  log('\n📋 Generating Test Report', colors.magenta);
  log('=' .repeat(50), colors.magenta);
  
  // Run tests with coverage and generate reports
  const unitResult = execCommand('npm run test:coverage');
  const e2eResult = execCommand('npm run test:e2e -- --reporter=json');
  
  if (unitResult.success && e2eResult.success) {
    logSuccess('Test reports generated in test-results/');
  } else {
    logWarning('Some tests failed, reports may be incomplete');
  }
}

function runAll() {
  log('\n🚀 Running All Tests', colors.green);
  log('=' .repeat(50), colors.green);
  
  const results = {
    dependencies: checkDependencies(),
    unit: false,
    e2e: false,
    solutions: false,
    gameFlow: false,
    performance: false
  };
  
  if (!results.dependencies) {
    logError('Dependency check failed, aborting');
    return;
  }
  
  results.unit = runUnitTests({ run: true });
  results.solutions = runSolutionTests();
  results.performance = runPerformanceTests();
  results.e2e = runE2ETests();
  results.gameFlow = runGameFlowTests();
  
  // Summary
  log('\n📊 Test Summary', colors.blue);
  log('=' .repeat(50), colors.blue);
  
  Object.entries(results).forEach(([test, passed]) => {
    if (test === 'dependencies') return;
    const status = passed ? '✅ PASSED' : '❌ FAILED';
    const color = passed ? colors.green : colors.red;
    log(`  ${test.padEnd(12)}: ${status}`, color);
  });
  
  const totalPassed = Object.values(results).filter(Boolean).length - 1; // Exclude dependencies
  const totalTests = Object.keys(results).length - 1;
  
  log(`\nTotal: ${totalPassed}/${totalTests} test suites passed`, 
    totalPassed === totalTests ? colors.green : colors.red);
    
  if (totalPassed === totalTests) {
    logSuccess('🎉 All tests passed! Your Coding Duel app is ready to rock!');
  } else {
    logError('Some tests failed. Check the output above for details.');
  }
}

function showHelp() {
  log('\n🧪 Coding Duel Test Runner', colors.cyan);
  log('=' .repeat(50), colors.cyan);
  
  console.log(`
Usage: node test-runner.js [command] [options]

Commands:
  unit                Run unit tests
  e2e                 Run end-to-end tests  
  solutions           Test all language solutions
  gameflow            Test complete game flow
  performance         Run performance tests
  report              Generate test reports
  all                 Run all tests
  help                Show this help

Options:
  --ui                Run tests with UI (unit tests only)
  --coverage          Run with coverage report
  --headed            Run E2E tests in headed mode
  --debug             Run E2E tests in debug mode
  --filter=<pattern>  Filter tests by pattern
  --file=<path>       Run specific test file
  --project=<name>    Run specific Playwright project

Examples:
  node test-runner.js unit --coverage
  node test-runner.js e2e --headed --filter="Two Sum"
  node test-runner.js solutions
  node test-runner.js all
  
Environment:
  FRONTEND_URL        Frontend server URL (default: http://localhost:3000)
  BACKEND_URL         Backend server URL (default: http://localhost:8000)
`);
}

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';
  
  const options = {};
  
  args.forEach(arg => {
    if (arg.startsWith('--')) {
      const [key, value] = arg.substring(2).split('=');
      options[key] = value || true;
    }
  });
  
  return { command, options };
}

// Main execution
function main() {
  const { command, options } = parseArgs();
  
  log('🧪 Coding Duel Test Runner', colors.cyan);
  log(`⏰ ${new Date().toLocaleString()}\n`, colors.yellow);
  
  switch (command) {
    case 'unit':
      checkDependencies() && runUnitTests(options);
      break;
    case 'e2e':
      checkDependencies() && runE2ETests(options);
      break;
    case 'solutions':
      checkDependencies() && runSolutionTests();
      break;
    case 'gameflow':
      checkDependencies() && runGameFlowTests();
      break;
    case 'performance':
      checkDependencies() && runPerformanceTests();
      break;
    case 'report':
      checkDependencies() && generateTestReport();
      break;
    case 'all':
      runAll();
      break;
    case 'help':
    default:
      showHelp();
      break;
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  runUnitTests,
  runE2ETests,
  runSolutionTests,
  runGameFlowTests,
  runPerformanceTests,
  runAll
};