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
        """Load test             elif request.language == "cpp":
        # C++ uses batch execution for better caching performance
        logger.info(
            f"|test_execution_service.py| [DEBUG] Using C++ batch execution for sample tests ({len(test_cases)} test cases)"
        )
        test_results, total_passed, total_failed = (
            TestExecutionService.run_cpp_batch_execution(
                request.code,
                test_cases,
                request.timeout,
                method_name,
                request.question_name,
            )
        )file based on question name."""
        test_file_path = f"backend/data/tests/{question_name}.json"
        logger.info(f"|test_execution_service.py| [DEBUG] Looking for test file: {test_file_path}")

        try:
            with open(test_file_path, "r") as f:
                test_cases = json.load(f)
            logger.info(
                f"|test_execution_service.py| [DEBUG] Test file loaded, found {len(test_cases)} test cases"
            )
            return test_cases
        except FileNotFoundError:
            logger.error(f"|test_execution_service.py| [DEBUG] Test file not found: {test_file_path}")
            raise FileNotFoundError(
                f"Test file not found for question: {question_name}"
            )

    @staticmethod
    def load_method_name(question_name: str) -> str:
        """Load method name from question data file."""
        question_file_path = f"backend/data/question-data/{question_name}.json"
        logger.info(f"|test_execution_service.py| [DEBUG] Looking for question file: {question_file_path}")

        try:
            with open(question_file_path, "r") as f:
                question_data = json.load(f)
            method_name = question_data.get(
                "methodName", question_name
            )  # Fallback to question_name
            logger.info(f"|test_execution_service.py| [DEBUG] Method name loaded: {method_name}")
            return method_name
        except FileNotFoundError:
            logger.warning(
                f"|test_execution_service.py| [DEBUG] Question file not found: {question_file_path}, using question_name as method_name"
            )
            return question_name  # Fallback to question_name
        except Exception as e:
            logger.warning(
                f"|test_execution_service.py| [DEBUG] Error loading method name: {str(e)}, using question_name as fallback"
            )
            return question_name  # Fallback to question_name

    @staticmethod
    def load_question_signature(question_name: str) -> Dict[str, Any]:
        """Load signature metadata from question data file."""
        question_file_path = f"backend/data/question-data/{question_name}.json"
        logger.info(
            f"|test_execution_service.py| [DEBUG] Looking for signature in question file: {question_file_path}"
        )

        try:
            with open(question_file_path, "r") as f:
                question_data = json.load(f)
            signature = question_data.get("signature")
            if signature:
                logger.info(f"|test_execution_service.py| [DEBUG] Signature loaded: {signature}")
                return signature
            else:
                logger.warning(
                    f"|test_execution_service.py| [DEBUG] No signature found in question file: {question_file_path}"
                )
                return None
        except FileNotFoundError:
            logger.warning(f"|test_execution_service.py| [DEBUG] Question file not found: {question_file_path}")
            return None
        except Exception as e:
            logger.warning(f"|test_execution_service.py| [DEBUG] Error loading signature: {str(e)}")
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
    def check_answer_in_expected(actual: Any, expected: Any) -> bool:
        """Check if the actual answer matches the expected answer."""
        actual_normalized = TestExecutionService.normalize_answer(actual)
        expected_normalized = TestExecutionService.normalize_answer(expected)

        # Direct equality check first (covers most cases)
        if actual_normalized == expected_normalized:
            return True

        # Use enhanced comparison for complex structures
        return TestExecutionService.compare_unordered_structures(
            actual_normalized, expected_normalized
        )

    @staticmethod
    def compare_unordered_structures(actual: Any, expected: Any) -> bool:
        """
        Compare two structures where order might not matter.
        Handles various scenarios using normalization approach.
        """
        # If types don't match, they're not equal
        if type(actual) != type(expected):
            return False

        # Handle non-list types directly
        if not isinstance(actual, list):
            return actual == expected

        # Both are lists - check length first
        if len(actual) != len(expected):
            return False

        # Empty lists are equal
        if len(actual) == 0:
            return True

        # Check if this looks like a list of lists (nested structure)
        if (
            len(actual) > 0
            and isinstance(actual[0], list)
            and len(expected) > 0
            and isinstance(expected[0], list)
        ):
            # Approach 3: Sort inner lists, then sort outer list
            try:

                def normalize_list_of_lists(lst):
                    # Sort each inner list, then sort the outer list
                    return sorted([sorted(inner) for inner in lst])

                return normalize_list_of_lists(actual) == normalize_list_of_lists(
                    expected
                )
            except (TypeError, AttributeError):
                # Fallback if sorting fails
                return actual == expected

        # Regular flat list - just sort and compare
        try:
            return sorted(actual) == sorted(expected)
        except TypeError:
            # If elements can't be sorted, try set comparison
            try:
                return set(actual) == set(expected)
            except TypeError:
                # If elements aren't hashable, exact comparison
                return actual == expected

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
        code: str,
        language: str,
        test_cases: List[Dict[str, Any]],
        timeout: int,
        function_name: str = "solution",
        signature: Dict[str, Any] = None,
        question_name: str = None,
    ) -> Tuple[List[TestCaseResult], int, int]:
        """Run test cases with compile-once-run-many approach for C++."""

        # For C++, use compile-once-run-many approach
        if language == "cpp":
            return TestExecutionService._run_cpp_compile_once(
                code, test_cases, timeout, function_name, question_name
            )

        # For other languages, fall back to the old individual approach
        import uuid
        from backend.code_testing.docker_runner import cleanup_submission_directory

        test_results = []
        total_passed = 0
        total_failed = 0

        # Generate ONE submission ID for all test cases to enable caching
        shared_submission_id = str(uuid.uuid4())[:8]
        logger.info(
            f"|test_execution_service.py| [DEBUG] Using shared submission ID: {shared_submission_id} for {len(test_cases)} test cases"
        )

        try:
            for i, test_case in enumerate(test_cases):
                logger.info(f"|test_execution_service.py| [DEBUG] Running test case {i+1}/{len(test_cases)}")
                try:
                    docker_start_time = time.time()
                    # Use shared submission ID and disable cleanup except for last test case
                    is_last_test = i == len(test_cases) - 1
                    docker_result = run_code_in_docker(
                        DockerRunRequest(
                            code=code,
                            language=language,
                            test_input=test_case["input"],
                            timeout=timeout,
                            function_name=function_name,
                            question_name=question_name,  # Pass question name if available
                            signature=signature,
                        ),
                        submission_id=shared_submission_id,
                        cleanup=False,  # Don't clean up until we're done with all tests
                    )
                    docker_time = (time.time() - docker_start_time) * 1000
                    logger.info(
                        f"|test_execution_service.py| [DEBUG] Docker execution took {docker_time:.0f}ms for test case {i+1}"
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

        finally:
            # Clean up the shared submission directory after all tests are done
            logger.info(
                f"|test_execution_service.py| [DEBUG] Cleaning up shared submission directory: {shared_submission_id}"
            )
            cleanup_submission_directory(language, shared_submission_id)

        return test_results, total_passed, total_failed

    @staticmethod
    def _run_cpp_compile_once(
        code: str,
        test_cases: List[Dict[str, Any]],
        timeout: int,
        function_name: str,
        question_name: str,
    ) -> Tuple[List[TestCaseResult], int, int]:
        """C++ specific: compile once, run multiple test cases."""
        import uuid
        from backend.code_testing.docker_runner import get_persistent_container
        from backend.code_testing.docker_runner import LANGUAGE_RUNNERS
        from backend.models.questions import DockerRunRequest

        test_results = []
        total_passed = 0
        total_failed = 0

        logger.info(
            f"|test_execution_service.py| [DEBUG] C++ compile-once-run-many for {len(test_cases)} test cases"
        )

        # Get container and runner
        container = get_persistent_container("cpp")
        runner_class = LANGUAGE_RUNNERS["cpp"]

        # Generate ONE submission ID for all test cases
        submission_id = str(uuid.uuid4())[:8]
        submission_dir = None

        try:
            # Step 1: Create submission directory ONCE
            submission_dir = runner_class.create_submission_directory(
                container, submission_id
            )
            logger.info(
                f"|test_execution_service.py| [DEBUG] Created shared submission directory: {submission_dir}"
            )

            # Step 2: Prepare and compile code ONCE
            first_request = DockerRunRequest(
                code=code,
                language="cpp",
                test_input=test_cases[0]["input"],
                timeout=timeout,
                function_name=function_name,
                question_name=question_name,
            )

            wrapped_code = runner_class.prepare_code(first_request)
            filename = runner_class.get_filename(first_request)
            file_path = f"{submission_dir}/{filename}"

            # Write code file ONCE
            runner_class.write_code_file(container, file_path, wrapped_code)

            # Compile ONCE
            compilation_result = runner_class.compile(
                container, first_request, file_path, wrapped_code
            )

            if not compilation_result["success"]:
                # If compilation fails, all test cases fail
                error_msg = compilation_result.get("error", "Compilation failed")
                for test_case in test_cases:
                    test_results.append(
                        TestCaseResult(
                            input=test_case["input"],
                            expected_output=test_case["expected"],
                            actual_output=None,
                            passed=False,
                            error=error_msg,
                            execution_time=None,
                        )
                    )
                    total_failed += 1
                return test_results, total_passed, total_failed

            logger.info(
                f"|test_execution_service.py| [DEBUG] Compilation successful, running {len(test_cases)} test cases"
            )
            logger.info(f"|test_execution_service.py| [DEBUG] Compilation result: {compilation_result}")

            # Step 3: Run each test case with the SAME compiled binary
            for i, test_case in enumerate(test_cases):
                try:
                    test_request = DockerRunRequest(
                        code=code,
                        language="cpp",
                        test_input=test_case["input"],
                        timeout=timeout,
                        function_name=function_name,
                        question_name=question_name,
                    )

                    # Get run command and execute
                    run_command = runner_class.get_run_command(
                        test_request, file_path, compilation_result
                    )
                    logger.info(f"|test_execution_service.py| [DEBUG] Run command: {run_command}")

                    exec_result = container.exec_run(
                        f"timeout {timeout} sh -c '{run_command}'", workdir="/tmp"
                    )
                    logger.info(f"|test_execution_service.py| [DEBUG] Exit code: {exec_result.exit_code}")

                    if exec_result.exit_code == 0:
                        logs = exec_result.output.decode("utf-8")
                        # Parse JSON output
                        import json

                        for line in reversed(logs.strip().split("\n")):
                            try:
                                output_data = json.loads(line)
                                if (
                                    isinstance(output_data, dict)
                                    and "result" in output_data
                                ):
                                    actual_output = output_data.get("result")
                                    break
                            except json.JSONDecodeError:
                                continue
                        else:
                            actual_output = None

                        expected = test_case["expected"]
                        if actual_output is not None:
                            passed = TestExecutionService.check_answer_in_expected(
                                actual_output, expected
                            )
                        else:
                            passed = False

                        test_results.append(
                            TestCaseResult(
                                input=test_case["input"],
                                expected_output=expected,
                                actual_output=(
                                    str(actual_output)
                                    if actual_output is not None
                                    else None
                                ),
                                passed=passed,
                                error=None,
                                execution_time=0.0,  # Harnesses return 0
                            )
                        )

                        if passed:
                            total_passed += 1
                        else:
                            total_failed += 1
                    else:
                        # Execution failed
                        test_results.append(
                            TestCaseResult(
                                input=test_case["input"],
                                expected_output=test_case["expected"],
                                actual_output=None,
                                passed=False,
                                error=f"Execution failed with exit code {exec_result.exit_code}",
                                execution_time=None,
                            )
                        )
                        total_failed += 1

                except Exception as e:
                    test_results.append(
                        TestCaseResult(
                            input=test_case["input"],
                            expected_output=test_case["expected"],
                            actual_output=None,
                            passed=False,
                            error=str(e),
                            execution_time=None,
                        )
                    )
                    total_failed += 1

        finally:
            # Step 4: Clean up submission directory ONCE
            if submission_dir:
                try:
                    cleanup_result = container.exec_run(
                        f"rm -rf {submission_dir}", workdir="/tmp"
                    )
                    logger.info(
                        f"|test_execution_service.py| [CLEANUP] Removed submission directory: {submission_dir}"
                    )
                except Exception as e:
                    logger.error(
                        f"❌ [CLEANUP] Error cleaning up {submission_dir}: {e}"
                    )

        return test_results, total_passed, total_failed

    @staticmethod
    def run_java_batch_execution(
        code: str,
        test_cases: List[Dict[str, Any]],
        timeout: int,
        function_name: str,
        question_name: str = None,
    ) -> Tuple[List[TestCaseResult], int, int]:
        """Execute Java code using batch runner."""
        # Bypass old batch runner - force fallback to individual execution using simplified approach
        logger.info(
            f"|test_execution_service.py| [DEBUG] Bypassing Java batch runner, using simplified individual execution"
        )
        raise Exception("Bypassing Java batch runner to use simplified approach")

    @staticmethod
    def run_cpp_batch_execution(
        code: str,
        test_cases: List[Dict[str, Any]],
        timeout: int,
        function_name: str,
        question_name: str = None,
    ) -> Tuple[List[TestCaseResult], int, int]:
        """C++ compile-once-run-many execution for optimal performance."""
        logger.info("|test_execution_service.py| [OPTIMIZATION] Starting C++ compile-once-run-many approach!")
        try:
            result = TestExecutionService._run_cpp_compile_once(
                code, test_cases, timeout, function_name, question_name
            )
            logger.info(
                "|test_execution_service.py| [OPTIMIZATION] C++ compile-once approach completed successfully!"
            )
            return result
        except Exception as e:
            logger.error(f"❌ [OPTIMIZATION] C++ compile-once failed: {e}")
            logger.info("|test_execution_service.py| [OPTIMIZATION] Falling back to old batch execution")
            # Import the old batch function as backup
            from backend.code_testing.docker_runner import run_cpp_batch_in_docker

            test_results = []
            total_passed = 0
            total_failed = 0

            if not test_cases:
                return test_results, total_passed, total_failed

            # Extract test inputs
            test_inputs = [test_case["input"] for test_case in test_cases]

            # Use old batch execution function as fallback
            docker_results = run_cpp_batch_in_docker(
                code=code,
                test_inputs=test_inputs,
                timeout=timeout,
                function_name=function_name,
                question_name=question_name,
            )

            # Process results
            for i, (test_case, docker_result) in enumerate(
                zip(test_cases, docker_results)
            ):
                expected = test_case["expected"]

                if docker_result.get("success", False):
                    passed = TestExecutionService.check_answer_in_expected(
                        docker_result.get("output"), expected
                    )
                    if passed:
                        total_passed += 1
                    else:
                        total_failed += 1

                    test_results.append(
                        TestCaseResult(
                            input=test_case["input"],
                            expected_output=expected,
                            actual_output=docker_result.get("output"),
                            passed=passed,
                            execution_time=docker_result.get("execution_time", 0),
                            error=docker_result.get("error"),
                        )
                    )
                else:
                    total_failed += 1
                    test_results.append(
                        TestCaseResult(
                            input=test_case["input"],
                            expected_output=expected,
                            actual_output=None,
                            passed=False,
                            execution_time=docker_result.get("execution_time", 0),
                            error=docker_result.get("error", "Execution failed"),
                        )
                    )

            return test_results, total_passed, total_failed

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
            f"|test_execution_service.py| [DEBUG] Starting test execution for {request.language} - {request.question_name}"
        )

        try:
            # Validate language
            step_time = time.time()
            TestExecutionService.validate_language(request.language)
            logger.info(
                f"|test_execution_service.py| [DEBUG] Language validation took {(time.time() - step_time)*1000:.0f}ms"
            )

            # Load test cases
            step_time = time.time()
            test_cases = TestExecutionService.load_test_cases(request.question_name)
            logger.info(
                f"|test_execution_service.py| [DEBUG] Test file loading took {(time.time() - step_time)*1000:.0f}ms"
            )

            # Load method name from question data
            step_time = time.time()
            method_name = TestExecutionService.load_method_name(request.question_name)
            logger.info(
                f"|test_execution_service.py| [DEBUG] Method name loading took {(time.time() - step_time)*1000:.0f}ms"
            )

            # Load signature metadata from question data
            step_time = time.time()
            signature = TestExecutionService.load_question_signature(
                request.question_name
            )
            logger.info(
                f"|test_execution_service.py| [DEBUG] Signature loading took {(time.time() - step_time)*1000:.0f}ms"
            )
            logger.info(f"|test_execution_service.py| [DEBUG] Signature: {signature}")

            logger.info(
                f"|test_execution_service.py| [DEBUG] Starting execution of {len(test_cases)} test cases"
            )

            # Choose execution strategy based on language
            if request.language == "java":
                try:
                    test_results, total_passed, total_failed = (
                        TestExecutionService.run_java_batch_execution(
                            request.code,
                            test_cases,
                            request.timeout,
                            method_name,
                            request.question_name,
                        )
                    )
                except Exception:
                    logger.info(
                        f"|test_execution_service.py| [DEBUG] Falling back to individual test case execution"
                    )
                    test_results, total_passed, total_failed = (
                        TestExecutionService.run_individual_test_cases(
                            request.code,
                            request.language,
                            test_cases,
                            request.timeout,
                            method_name,
                            signature,
                            request.question_name,  # Pass question name
                        )
                    )
            elif request.language == "cpp":
                # C++ now uses batch execution - compile once, run multiple test cases
                logger.info(
                    f"|test_execution_service.py| [DEBUG] Using C++ batch execution for {len(test_cases)} test cases"
                )
                test_results, total_passed, total_failed = (
                    TestExecutionService.run_cpp_batch_execution(
                        request.code,
                        test_cases,
                        request.timeout,
                        method_name,
                        request.question_name,
                    )
                )
            else:
                # For other languages, use individual execution
                test_results, total_passed, total_failed = (
                    TestExecutionService.run_individual_test_cases(
                        request.code,
                        request.language,
                        test_cases,
                        request.timeout,
                        method_name,
                        signature,
                        request.question_name,  # Pass question name
                    )
                )

            total_time = (time.time() - start_time) * 1000
            logger.info(f"|test_execution_service.py| [DEBUG] Total test execution time: {total_time:.0f}ms")

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
                f"|test_execution_service.py| [DEBUG] Exception in test execution after {total_time:.0f}ms: {str(e)}"
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
            f"|test_execution_service.py| [DEBUG] Starting SAMPLE test execution (first 3 tests) for {request.language} - {request.question_name}"
        )

        try:
            # Validate language
            step_time = time.time()
            TestExecutionService.validate_language(request.language)
            logger.info(
                f"|test_execution_service.py| [DEBUG] Language validation took {(time.time() - step_time)*1000:.0f}ms"
            )

            # Load test cases
            step_time = time.time()
            all_test_cases = TestExecutionService.load_test_cases(request.question_name)
            # Limit to first 3 test cases for sample execution
            test_cases = all_test_cases[:3]
            logger.info(
                f"|test_execution_service.py| [DEBUG] Test file loading took {(time.time() - step_time)*1000:.0f}ms"
            )

            # Load method name from question data
            step_time = time.time()
            method_name = TestExecutionService.load_method_name(request.question_name)
            logger.info(
                f"🐛 [DEBUG] Method name loading took {(time.time() - step_time)*1000:.0f}ms"
            )

            # Load signature metadata from question data
            step_time = time.time()
            signature = TestExecutionService.load_question_signature(
                request.question_name
            )
            logger.info(
                f"|test_execution_service.py| [DEBUG] Signature loading took {(time.time() - step_time)*1000:.0f}ms"
            )
            logger.info(f"|test_execution_service.py| [DEBUG] Signature: {signature}")

            logger.info(
                f"|test_execution_service.py| [DEBUG] Running SAMPLE execution with {len(test_cases)} test cases (out of {len(all_test_cases)} total)"
            )

            # Choose execution strategy based on language (same logic as full execution)
            if request.language == "java":
                try:
                    test_results, total_passed, total_failed = (
                        TestExecutionService.run_java_batch_execution(
                            request.code,
                            test_cases,
                            request.timeout,
                            method_name,
                            request.question_name,
                        )
                    )
                except Exception:
                    logger.info(
                        f"|test_execution_service.py| [DEBUG] Falling back to individual test case execution for sample tests"
                    )
                    test_results, total_passed, total_failed = (
                        TestExecutionService.run_individual_test_cases(
                            request.code,
                            request.language,
                            test_cases,
                            request.timeout,
                            method_name,
                            signature,
                            request.question_name,  # Pass question name
                        )
                    )
            elif request.language == "cpp":
                # C++ uses individual execution with improved caching
                logger.info(
                    f"|test_execution_service.py| [DEBUG] Using individual execution with caching for C++ sample tests"
                )
                test_results, total_passed, total_failed = (
                    TestExecutionService.run_individual_test_cases(
                        request.code,
                        request.language,
                        test_cases,
                        request.timeout,
                        method_name,
                        signature,
                        request.question_name,
                    )
                )
            else:
                # For other languages, use individual execution
                test_results, total_passed, total_failed = (
                    TestExecutionService.run_individual_test_cases(
                        request.code,
                        request.language,
                        test_cases,
                        request.timeout,
                        method_name,
                        signature,
                        request.question_name,  # Pass question name
                    )
                )

            total_time = (time.time() - start_time) * 1000
            logger.info(
                f"|test_execution_service.py| [DEBUG] Total SAMPLE test execution time: {total_time:.0f}ms"
            )

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
                f"|test_execution_service.py| [DEBUG] Exception in SAMPLE test execution after {total_time:.0f}ms: {str(e)}"
            )
            return RunTestCasesResponse(
                success=False,
                test_results=[],
                total_passed=0,
                total_failed=0,
                error=f"Error executing code: {str(e)}",
            )
