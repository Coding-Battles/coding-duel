#!/usr/bin/env python3
"""
Comprehensive Practice Endpoint Testing Script

Tests all 46 questions across 4 languages (184 total tests) using Groq API
to generate solutions and validate against practice endpoints.
"""

import json
import os
import time
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from groq import Groq
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BASE_URL = "http://localhost:8000"
QUESTION_DATA_DIR = "backend/data/question-data"
LANGUAGES = ["python", "javascript", "java", "cpp"]
MAX_RETRIES = 2
REQUEST_DELAY = 0.1  # Small delay between requests to be respectful

# Initialize Groq client
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not found!")

client = Groq(api_key=GROQ_API_KEY)

class EndpointTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.successful_tests = 0
        self.failed_tests = 0
        self.start_time = datetime.now()
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def generate_solution_with_groq(self, question_data: Dict, language: str) -> Optional[str]:
        """Generate solution using Groq API"""
        for attempt in range(MAX_RETRIES + 1):
            try:
                # Extract relevant info
                title = question_data.get("title", "Unknown")
                description = question_data.get("description_html", "")
                starter_code = question_data.get("starter_code", {}).get(language, "")
                method_name = question_data.get("methodName", "")
                
                # Clean HTML from description for better prompt
                import re
                clean_description = re.sub(r'<[^>]+>', '', description)
                clean_description = re.sub(r'\s+', ' ', clean_description).strip()
                
                # Create comprehensive prompt
                prompt = f"""Complete this {language} coding solution:

Problem: {title}
{clean_description[:500]}...

Starter Code:
{starter_code}

Requirements:
- Complete the {method_name} method/function
- Return the correct data type as specified
- Handle all edge cases
- Write clean, efficient code
- Only return the completed code, no explanations

Complete the solution:"""

                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are an expert {language} programmer. Complete the given coding problem solution. Return only the complete, working code without any explanations or markdown formatting."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Lower temperature for more consistent code
                    max_tokens=1024,
                    top_p=0.9,
                )
                
                solution = completion.choices[0].message.content.strip()
                
                # Clean up common formatting issues
                if solution.startswith("```"):
                    lines = solution.split('\n')
                    solution = '\n'.join(lines[1:-1]) if len(lines) > 2 else solution
                
                return solution
                
            except Exception as e:
                if attempt < MAX_RETRIES:
                    self.log(f"Groq API error (attempt {attempt + 1}): {e}. Retrying...", "WARN")
                    time.sleep(1)  # Brief delay before retry
                else:
                    self.log(f"Failed to generate solution after {MAX_RETRIES + 1} attempts: {e}", "ERROR")
                    return None
                    
        return None
    
    def test_solution(self, question_slug: str, language: str, code: str) -> Dict:
        """Test solution against practice endpoint"""
        url = f"{BASE_URL}/api/{question_slug}/test-sample"
        
        payload = {
            "player_id": "automation-test",
            "code": code,
            "question_name": question_slug,
            "language": language,
            "timer": 0
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "total_passed": 0,
                    "total_failed": 3
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "total_passed": 0,
                "total_failed": 3
            }
    
    def get_all_questions(self) -> List[Tuple[str, Dict]]:
        """Discover all questions from JSON files"""
        questions = []
        question_dir = Path(QUESTION_DATA_DIR)
        
        if not question_dir.exists():
            raise FileNotFoundError(f"Question directory not found: {question_dir}")
            
        for json_file in sorted(question_dir.glob("*.json")):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    question_data = json.load(f)
                    question_slug = json_file.stem
                    questions.append((question_slug, question_data))
            except Exception as e:
                self.log(f"Error loading {json_file}: {e}", "ERROR")
                
        return questions
    
    def process_question_language(self, question_slug: str, question_data: Dict, language: str) -> Dict:
        """Process a single question+language combination"""
        result = {
            "question": question_slug,
            "language": language,
            "title": question_data.get("title", "Unknown"),
            "success": False,
            "tests_passed": 0,
            "tests_failed": 3,
            "error": None,
            "execution_time": 0,
            "groq_success": False
        }
        
        # Check if starter code exists for this language
        starter_code = question_data.get("starter_code", {}).get(language)
        if not starter_code:
            result["error"] = f"No starter code available for {language}"
            return result
        
        # Generate solution with Groq
        self.log(f"Generating {language} solution for {question_slug}...")
        solution = self.generate_solution_with_groq(question_data, language)
        
        if not solution:
            result["error"] = "Failed to generate solution with Groq"
            return result
            
        result["groq_success"] = True
        
        # Test the solution
        self.log(f"Testing {question_slug} [{language}]...")
        test_result = self.test_solution(question_slug, language, solution)
        
        # Update result with test outcome
        result["success"] = test_result.get("success", False)
        result["tests_passed"] = test_result.get("total_passed", 0)
        result["tests_failed"] = test_result.get("total_failed", 3)
        result["error"] = test_result.get("error")
        
        # Log result
        if result["success"]:
            self.log(f"✅ {question_slug} [{language}]: {result['tests_passed']}/3 tests passed", "SUCCESS")
            self.successful_tests += 1
        else:
            error_msg = result["error"] or "Unknown error"
            self.log(f"❌ {question_slug} [{language}]: {result['tests_passed']}/3 tests passed - {error_msg}", "FAIL")
            self.failed_tests += 1
            
        return result
    
    def run_comprehensive_test(self):
        """Run comprehensive test across all questions and languages"""
        self.log("🚀 Starting comprehensive practice endpoint testing...")
        
        # Discover all questions
        questions = self.get_all_questions()
        self.log(f"Found {len(questions)} questions to test")
        
        # Calculate total tests
        total_combinations = 0
        for _, question_data in questions:
            available_languages = [lang for lang in LANGUAGES 
                                 if question_data.get("starter_code", {}).get(lang)]
            total_combinations += len(available_languages)
            
        self.total_tests = total_combinations
        self.log(f"Total tests to run: {self.total_tests}")
        
        # Process each question+language combination
        test_count = 0
        for question_slug, question_data in questions:
            title = question_data.get("title", "Unknown")
            self.log(f"\n--- Processing: {title} ({question_slug}) ---")
            
            for language in LANGUAGES:
                if not question_data.get("starter_code", {}).get(language):
                    self.log(f"Skipping {language} (no starter code)")
                    continue
                    
                test_count += 1
                progress = f"[{test_count}/{self.total_tests}]"
                self.log(f"{progress} Testing {question_slug} in {language}")
                
                # Process this combination
                result = self.process_question_language(question_slug, question_data, language)
                self.results.append(result)
                
                # Small delay to be respectful to the API
                time.sleep(REQUEST_DELAY)
        
        # Generate reports
        self.generate_reports()
    
    def generate_reports(self):
        """Generate comprehensive test reports"""
        elapsed_time = datetime.now() - self.start_time
        
        # Console summary
        success_rate = (self.successful_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print("\n" + "="*70)
        print("🎯 COMPREHENSIVE TEST RESULTS")
        print("="*70)
        print(f"Total Tests Run: {self.total_tests}")
        print(f"Successful: {self.successful_tests} ({success_rate:.1f}%)")
        print(f"Failed: {self.failed_tests}")
        print(f"Execution Time: {elapsed_time}")
        print()
        
        # Language breakdown
        language_stats = {}
        for lang in LANGUAGES:
            lang_results = [r for r in self.results if r["language"] == lang]
            lang_success = sum(1 for r in lang_results if r["success"])
            lang_total = len(lang_results)
            language_stats[lang] = (lang_success, lang_total)
            
        print("📊 LANGUAGE BREAKDOWN:")
        for lang, (success, total) in language_stats.items():
            rate = (success / total * 100) if total > 0 else 0
            print(f"  {lang:12}: {success:3}/{total:3} ({rate:5.1f}%)")
        
        # Save detailed CSV report
        csv_filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["question", "language", "title", "success", "tests_passed", 
                         "tests_failed", "groq_success", "error"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
            
        print(f"\n📁 Detailed results saved to: {csv_filename}")
        
        # Show failed tests if any
        failed_results = [r for r in self.results if not r["success"]]
        if failed_results:
            print(f"\n❌ FAILED TESTS ({len(failed_results)}):")
            for result in failed_results[:10]:  # Show first 10 failures
                error = result["error"] or "Unknown error"
                print(f"  {result['question']} [{result['language']}]: {error}")
            if len(failed_results) > 10:
                print(f"  ... and {len(failed_results) - 10} more (see CSV for details)")

def main():
    """Main execution function"""
    tester = EndpointTester()
    
    try:
        # Verify server is running
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            raise Exception(f"Server not responding correctly: {response.status_code}")
        
        tester.log("✅ Server is running and accessible")
        
        # Run comprehensive test
        tester.run_comprehensive_test()
        
    except KeyboardInterrupt:
        tester.log("Test interrupted by user", "WARN")
    except Exception as e:
        tester.log(f"Test failed with error: {e}", "ERROR")
        raise

if __name__ == "__main__":
    main()