"""
C++ specific runner implementation.
"""

import os
import uuid
import time
import base64
from typing import Dict, Any
from backend.models.questions import DockerRunRequest
from .base_runner import BaseRunner


class CppRunner(BaseRunner):
    """C++ specific code runner with static methods."""

    @staticmethod
    def prepare_code(request: DockerRunRequest) -> str:
        """Prepare C++ code with harness system."""
        # Use question_name (not function_name) for harness directory lookup
        question_name = getattr(request, "question_name", None)
        if not question_name:
            raise ValueError(
                f"No question_name provided for C++ problem. Cannot find harness file."
            )

        harness_path = (
            f"backend/code_testing/cpp_harnesses/harnesses/{question_name}/harness.cpp"
        )

        if os.path.exists(harness_path):
            # Use dedicated harness file
            print(f"🔧 [CPP] Using dedicated harness for question: {question_name}")

            with open(harness_path, "r") as f:
                harness_content = f.read()

            # Replace #include "userfunc.h" with the actual user code
            # Ensure user code has access to standard namespace
            user_code_with_namespace = f"""// User solution code with namespace access
using namespace std;

{request.code}"""

            wrapped_code = harness_content.replace(
                '#include "userfunc.h"',
                user_code_with_namespace,
            )

            print(f"🔧 [CPP] Using harness file: {harness_path}")
            return wrapped_code
        else:
            # No harness file found - this is an error
            raise ValueError(
                f"No harness file found for C++ problem: {question_name}. Expected: {harness_path}"
            )

    @staticmethod
    def get_filename(request: DockerRunRequest) -> str:
        """Generate unique filename for C++ submission."""
        submission_id = str(uuid.uuid4())[:8]
        return f"solution_{submission_id}.cpp"

    @staticmethod
    def compile(
        container, request: DockerRunRequest, filename: str, wrapped_code: str
    ) -> Dict[str, Any]:
        """Compile C++ code with simple per-submission caching."""
        # Get submission directory from full file path
        submission_dir = os.path.dirname(filename)

        # Use simple per-submission caching
        binary_path = CppRunner._compile_cpp_with_cache(
            container, wrapped_code, request.function_name, submission_dir
        )

        if binary_path:
            return {"success": True, "binary_path": binary_path, "method": "simple"}
        else:
            # Fallback to traditional g++ compilation
            print(f"⚠️ [CPP] Simple compilation failed, falling back to traditional g++")

            base_filename = os.path.basename(filename)
            compile_cmd = f"g++ -std=c++17 -O2 -o solution {base_filename}"
            compile_result = container.exec_run(
                f"timeout 10 {compile_cmd}", workdir=submission_dir
            )

            if compile_result.exit_code == 0:
                return {
                    "success": True,
                    "binary_path": f"{submission_dir}/solution",
                    "method": "fallback",
                }
            else:
                return {
                    "success": False,
                    "error": f"Compilation failed: {compile_result.output.decode()}",
                }

    @staticmethod
    def get_run_command(
        request: DockerRunRequest, filename: str, compilation_result: Dict[str, Any]
    ) -> str:
        """Generate run command for C++."""
        submission_dir = os.path.dirname(filename)

        # Add input arguments - C++ harnesses expect function name and JSON input
        import json

        function_name = getattr(request, "function_name", "solution")
        input_json = json.dumps(request.test_input).replace('"', '\\"')

        # Simple approach: binary is always in submission directory
        binary_path = compilation_result["binary_path"]
        run_command = f'{binary_path} "{function_name}" "{input_json}"'

        return run_command

    @staticmethod
    def _compile_cpp_with_cache(
        container, source_code: str, function_name: str, submission_dir: str = "/tmp"
    ) -> str:
        """Compile C++ code with simple per-submission caching."""
        try:
            compile_start = time.time()

            # Simple approach: use submission directory as cache
            # Binary will be named after the function
            binary_name = f"{function_name}_binary"
            binary_path = f"{submission_dir}/{binary_name}"

            # Write source code to file
            source_filename = f"{function_name}_source.cpp"
            encoded_source = base64.b64encode(source_code.encode("utf-8")).decode(
                "ascii"
            )

            create_result = container.exec_run(
                f"timeout 10 sh -c 'echo {encoded_source} | base64 -d > {source_filename}'",
                workdir=submission_dir,
            )

            if create_result.exit_code != 0:
                print(
                    f"❌ [CPP] Failed to create source file: {create_result.output.decode()}"
                )
                return None

            # Compile directly in submission directory
            compile_cmd = f"g++ -std=c++17 -O2 -pipe -o {binary_name} {source_filename}"
            compile_result = container.exec_run(
                f"timeout 10 {compile_cmd}", workdir=submission_dir
            )

            compile_time = (time.time() - compile_start) * 1000

            # Clean up source file
            container.exec_run(f"rm -f {source_filename}", workdir=submission_dir)

            # Handle timeout error for compilation
            if compile_result.exit_code == 124:
                print(f"❌ [CPP] Compilation timed out after 10 seconds")
                return None

            if compile_result.exit_code == 0:
                print(f"✅ [CPP] Compiled binary: {binary_name} ({compile_time:.1f}ms)")
                return binary_path
            else:
                error_output = compile_result.output.decode()
                print(f"❌ [CPP] Compilation failed: {error_output}")
                return None

        except Exception as e:
            print(f"❌ [CPP] Compilation failed: {e}")
            return None
