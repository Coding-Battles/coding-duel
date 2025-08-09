import json
import logging
import time
from typing import List, Dict, Any, Tuple

from backend.models.questions import (
    TestCaseResult,
    DockerRunRequest,
    RunTestCasesRequest,
    RunTestCasesResponse,
)
from backend.code_testing.docker_runner import run_code_in_docker
from backend.code_testing.language_config import LANGUAGE_CONFIG

logger = logging.getLogger(__name__)


class TestExecutionService:
    """Service for handling test case execution logic."""

    @staticmethod
    def load_test_cases(question_name: str) -> List[Dict[str, Any]]:
        """Load test cases from JSON file based on question name."""
        test_file_path = f"backend/data/tests/{question_name}.json"
        logger.info(f"🐛 [DEBUG] Looking for test file: {test_file_path}")

        try:
            with open(test_file_path, "r") as f:
                test_cases = json.load(f)
            logger.info(
                f"🐛 [DEBUG] Test file loaded, found {len(test_cases)} test cases"
            )
            return test_cases
        except FileNotFoundError:
            logger.error(f"🐛 [DEBUG] Test file not found: {test_file_path}")
            raise FileNotFoundError(
                f"Test file not found for question: {question_name}"
            )

    @staticmethod
    def load_method_name(question_name: str) -> str:
        """Load method name from question data file."""
        question_file_path = f"backend/data/question-data/{question_name}.json"
        logger.info(f"🐛 [DEBUG] Looking for question file: {question_file_path}")

        try:
            with open(question_file_path, "r") as f:
                question_data = json.load(f)
            method_name = question_data.get("methodName", question_name)  # Fallback to question_name
            logger.info(f"🐛 [DEBUG] Method name loaded: {method_name}")
            return method_name
        except FileNotFoundError:
            logger.warning(f"🐛 [DEBUG] Question file not found: {question_file_path}, using question_name as method_name")
            return question_name  # Fallback to question_name
        except Exception as e:
            logger.warning(f"🐛 [DEBUG] Error loading method name: {str(e)}, using question_name as fallback")
            return question_name  # Fallback to question_name

    @staticmethod
    def load_question_signature(question_name: str) -> Dict[str, Any]:
        """Load signature metadata from question data file."""
        question_file_path = f"backend/data/question-data/{question_name}.json"
        logger.info(f"🐛 [DEBUG] Looking for signature in question file: {question_file_path}")

        try:
            with open(question_file_path, "r") as f:
                question_data = json.load(f)
            signature = question_data.get("signature")
            if signature:
                logger.info(f"🐛 [DEBUG] Signature loaded: {signature}")
                return signature
            else:
                logger.warning(f"🐛 [DEBUG] No signature found in question file: {question_file_path}")
                return None
        except FileNotFoundError:
            logger.warning(f"🐛 [DEBUG] Question file not found: {question_file_path}")
            return None
        except Exception as e:
            logger.warning(f"🐛 [DEBUG] Error loading signature: {str(e)}")
            return None

    @staticmethod
    def normalize_answer(answer: Any) -> Any:
        """Normalize answer to handle different formats (list vs string)."""
        if isinstance(answer, str):
            try:
                import ast

                return ast.literal_eval(answer)
            except:
                return answer
        return answer

    @staticmethod
    def check_answer_in_expected(actual: Any, expected_list: List[Any]) -> bool:
        """Check if the actual answer matches any of the expected answers."""
        actual_normalized = TestExecutionService.normalize_answer(actual)

        # If expected is a single answer (old format), convert to list
        if not isinstance(expected_list, list):
            expected_list = [expected_list]
        elif len(expected_list) > 0 and not isinstance(expected_list[0], list):
            expected_list = [expected_list]

        for expected in expected_list:
            expected_normalized = TestExecutionService.normalize_answer(expected)
            if actual_normalized == expected_normalized:
                return True

        return False

    @staticmethod
    def process_batch_results(
        test_cases: List[Dict[str, Any]], batch_results: List[Dict[str, Any]]
    ) -> Tuple[List[TestCaseResult], int, int]:
        """Process batch execution results and return test results with counts."""
        test_results = []
        total_passed = 0
        total_failed = 0

        for test_case, result in zip(test_cases, batch_results):
            expected = test_case["expected"]
            actual_output = result.get("output")

            if result.get("success", False):
                passed = TestExecutionService.check_answer_in_expected(
                    actual_output, expected
                )
            else:
                passed = False

            test_result = TestCaseResult(
                input=test_case["input"],
                expected_output=expected,
                actual_output=str(actual_output) if actual_output is not None else None,
                passed=passed,
                error=result.get("error"),
                execution_time=result.get("execution_time"),
            )

            test_results.append(test_result)

            if passed:
                total_passed += 1
            else:
                total_failed += 1

        return test_results, total_passed, total_failed

    @staticmethod
    def run_individual_test_cases(
        code: str, language: str, test_cases: List[Dict[str, Any]], timeout: int, function_name: str = "solution", signature: Dict[str, Any] = None
    ) -> Tuple[List[TestCaseResult], int, int]:
        """Run test cases individually (for non-batch languages or fallback)."""
        test_results = []
        total_passed = 0
        total_failed = 0

        for i, test_case in enumerate(test_cases):
            logger.info(f"🐛 [DEBUG] Running test case {i+1}/{len(test_cases)}")
            try:
                docker_start_time = time.time()
                docker_result = run_code_in_docker(
                    DockerRunRequest(
                        code=code,
                        language=language,
                        test_input=test_case["input"],
                        timeout=timeout,
                        function_name=function_name,
                        signature=signature,
                    )
                )
                docker_time = (time.time() - docker_start_time) * 1000
                logger.info(
                    f"🐛 [DEBUG] Docker execution took {docker_time:.0f}ms for test case {i+1}"
                )

                expected = test_case["expected"]
                actual_output = docker_result.get("output")

                if docker_result.get("success", False):
                    passed = TestExecutionService.check_answer_in_expected(
                        actual_output, expected
                    )
                else:
                    passed = False

                test_result = TestCaseResult(
                    input=test_case["input"],
                    expected_output=expected,
                    actual_output=(
                        str(actual_output) if actual_output is not None else None
                    ),
                    passed=passed,
                    error=docker_result.get("error"),
                    execution_time=docker_result.get("execution_time"),
                )

                test_results.append(test_result)

                if passed:
                    total_passed += 1
                else:
                    total_failed += 1

            except Exception as e:
                test_result = TestCaseResult(
                    input=test_case["input"],
                    expected_output=test_case["expected"],
                    actual_output=None,
                    passed=False,
                    error=str(e),
                    execution_time=None,
                )
                test_results.append(test_result)
                total_failed += 1

        return test_results, total_passed, total_failed

    @staticmethod
    def run_java_batch_execution(
        code: str, test_cases: List[Dict[str, Any]], timeout: int, function_name: str, question_name: str = None
    ) -> Tuple[List[TestCaseResult], int, int]:
        """Execute Java code using batch runner."""
        # Bypass old batch runner - force fallback to individual execution using simplified approach
        logger.info(f"🐛 [DEBUG] Bypassing Java batch runner, using simplified individual execution")
        raise Exception("Bypassing Java batch runner to use simplified approach")

    # C++ batch processing removed - now uses standard docker_runner execution like Java

    @staticmethod
    def validate_language(language: str) -> None:
        """Validate that the language is supported."""
        if language not in LANGUAGE_CONFIG:
            raise ValueError(f"Unsupported language: {language}")

    @staticmethod
    def execute_test_cases(request: RunTestCasesRequest) -> RunTestCasesResponse:
        """Main method to execute test cases with proper strategy selection."""
        start_time = time.time()
        logger.info(
            f"🐛 [DEBUG] Starting test execution for {request.language} - {request.question_name}"
        )

        try:
            # Validate language
            step_time = time.time()
            TestExecutionService.validate_language(request.language)
            logger.info(
                f"🐛 [DEBUG] Language validation took {(time.time() - step_time)*1000:.0f}ms"
            )

            # Load test cases
            step_time = time.time()
            test_cases = TestExecutionService.load_test_cases(request.question_name)
            logger.info(
                f"🐛 [DEBUG] Test file loading took {(time.time() - step_time)*1000:.0f}ms"
            )

            # Load method name from question data
            step_time = time.time()
            method_name = TestExecutionService.load_method_name(request.question_name)
            logger.info(
                f"🐛 [DEBUG] Method name loading took {(time.time() - step_time)*1000:.0f}ms"
            )

            # Load signature metadata from question data
            step_time = time.time()
            signature = TestExecutionService.load_question_signature(request.question_name)
            logger.info(
                f"🐛 [DEBUG] Signature loading took {(time.time() - step_time)*1000:.0f}ms"
            )
            logger.info(f"🐛 [DEBUG] Signature: {signature}")

            logger.info(
                f"🐛 [DEBUG] Starting execution of {len(test_cases)} test cases"
            )

            # Choose execution strategy based on language
            if request.language == "java":
                try:
                    test_results, total_passed, total_failed = (
                        TestExecutionService.run_java_batch_execution(
                            request.code, test_cases, request.timeout, method_name, request.question_name
                        )
                    )
                except Exception:
                    logger.info(
                        f"🐛 [DEBUG] Falling back to individual test case execution"
                    )
                    test_results, total_passed, total_failed = (
                        TestExecutionService.run_individual_test_cases(
                            request.code, request.language, test_cases, request.timeout, method_name, signature
                        )
                    )
            elif request.language == "cpp":
                # C++ now uses standard individual execution like Java (no batch processing)
                logger.info(f"🐛 [DEBUG] Using standard individual execution for C++")
                test_results, total_passed, total_failed = (
                    TestExecutionService.run_individual_test_cases(
                        request.code, request.language, test_cases, request.timeout, method_name, signature
                    )
                    )
            else:
                # For other languages, use individual execution
                test_results, total_passed, total_failed = (
                    TestExecutionService.run_individual_test_cases(
                        request.code, request.language, test_cases, request.timeout, method_name
                    )
                )

            total_time = (time.time() - start_time) * 1000
            logger.info(f"🐛 [DEBUG] Total test execution time: {total_time:.0f}ms")

            return RunTestCasesResponse(
                success=total_failed == 0,
                test_results=test_results,
                total_passed=total_passed,
                total_failed=total_failed,
                error=None,
            )

        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            logger.error(
                f"🐛 [DEBUG] Exception in test execution after {total_time:.0f}ms: {str(e)}"
            )
            return RunTestCasesResponse(
                success=False,
                test_results=[],
                total_passed=0,
                total_failed=0,
                error=f"Error executing code: {str(e)}",
            )

    @staticmethod
    def execute_sample_test_cases(request: RunTestCasesRequest) -> RunTestCasesResponse:
        """Execute only the first 3 test cases for quick feedback during development."""
        start_time = time.time()
        logger.info(
            f"🐛 [DEBUG] Starting SAMPLE test execution (first 3 tests) for {request.language} - {request.question_name}"
        )

        try:
            # Validate language
            step_time = time.time()
            TestExecutionService.validate_language(request.language)
            logger.info(
                f"🐛 [DEBUG] Language validation took {(time.time() - step_time)*1000:.0f}ms"
            )

            # Load test cases
            step_time = time.time()
            all_test_cases = TestExecutionService.load_test_cases(request.question_name)
            # Limit to first 3 test cases for sample execution
            test_cases = all_test_cases[:3]
            logger.info(
                f"🐛 [DEBUG] Test file loading took {(time.time() - step_time)*1000:.0f}ms"
            )

            # Load method name from question data
            step_time = time.time()
            method_name = TestExecutionService.load_method_name(request.question_name)
            logger.info(
                f"🐛 [DEBUG] Method name loading took {(time.time() - step_time)*1000:.0f}ms"
            )

            # Load signature metadata from question data
            step_time = time.time()
            signature = TestExecutionService.load_question_signature(request.question_name)
            logger.info(
                f"🐛 [DEBUG] Signature loading took {(time.time() - step_time)*1000:.0f}ms"
            )
            logger.info(f"🐛 [DEBUG] Signature: {signature}")
            
            logger.info(
                f"🐛 [DEBUG] Running SAMPLE execution with {len(test_cases)} test cases (out of {len(all_test_cases)} total)"
            )

            # Choose execution strategy based on language (same logic as full execution)
            if request.language == "java":
                try:
                    test_results, total_passed, total_failed = (
                        TestExecutionService.run_java_batch_execution(
                            request.code, test_cases, request.timeout, method_name, request.question_name
                        )
                    )
                except Exception:
                    logger.info(
                        f"🐛 [DEBUG] Falling back to individual test case execution for sample tests"
                    )
                    test_results, total_passed, total_failed = (
                        TestExecutionService.run_individual_test_cases(
                            request.code, request.language, test_cases, request.timeout, method_name, signature
                        )
                    )
            elif request.language == "cpp":
                # C++ now uses standard individual execution like Java (no batch processing)
                logger.info(f"🐛 [DEBUG] Using standard individual execution for C++ sample tests")
                test_results, total_passed, total_failed = (
                    TestExecutionService.run_individual_test_cases(
                        request.code, request.language, test_cases, request.timeout, method_name, signature
                    )
                    )
            else:
                # For other languages, use individual execution
                test_results, total_passed, total_failed = (
                    TestExecutionService.run_individual_test_cases(
                        request.code, request.language, test_cases, request.timeout, method_name
                    )
                )

            total_time = (time.time() - start_time) * 1000
            logger.info(f"🐛 [DEBUG] Total SAMPLE test execution time: {total_time:.0f}ms")

            return RunTestCasesResponse(
                success=total_failed == 0,
                test_results=test_results,
                total_passed=total_passed,
                total_failed=total_failed,
                error=None,
            )

        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            logger.error(
                f"🐛 [DEBUG] Exception in SAMPLE test execution after {total_time:.0f}ms: {str(e)}"
            )
            return RunTestCasesResponse(
                success=False,
                test_results=[],
                total_passed=0,
                total_failed=0,
                error=f"Error executing code: {str(e)}",
            )
