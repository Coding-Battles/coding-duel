"""
Java-specific runner implementation.
"""

import os
import uuid
import base64
import time
from typing import Dict, Any
from backend.models.questions import DockerRunRequest
from .base_runner import BaseRunner


class JavaRunner(BaseRunner):
    """Java-specific code runner with static methods."""

    @staticmethod
    def prepare_code(request: DockerRunRequest) -> str:
        """Prepare Java code with harness system."""
        # Special processing for Java firstBadVersion to avoid class conflicts
        processed_code = request.code

        if request.function_name == "firstBadVersion":
            # Remove "extends VersionControl" from user code if present to avoid conflicts
            processed_code = processed_code.replace(
                "extends VersionControl", ""
            ).replace("  {", " {")
            print(f"🔧 [JAVA] Cleaned code for firstBadVersion")

        question_name = getattr(request, "question_name", None)
        return JavaRunner._generate_java_wrapper(
            request.function_name, processed_code, question_name
        )

    @staticmethod
    def get_filename(request: DockerRunRequest) -> str:
        """Generate unique filename for Java submission."""
        submission_id = str(uuid.uuid4())[:8]
        # For Java, we need to keep Main.java since harnesses expect this name
        return "Main.java"

    @staticmethod
    def compile(
        container, request: DockerRunRequest, filename: str, wrapped_code: str
    ) -> Dict[str, Any]:
        """Compile Java code using compilation server or fallback to javac."""
        # Try Java compilation server first
        compilation_dir = JavaRunner._use_java_compilation_server(
            container, wrapped_code
        )

        if compilation_dir:
            print(
                f"🔥 [JAVA] Compilation server successful, output in: {compilation_dir}"
            )
            return {
                "success": True,
                "output_dir": compilation_dir,
                "method": "compilation_server",
            }
        else:
            # Fallback to traditional javac compilation
            print(f"⚠️ [JAVA] Compilation server failed, falling back to javac")

            # Get submission directory from full file path
            submission_dir = os.path.dirname(filename)
            base_filename = os.path.basename(filename)

            compile_cmd = f"cd {submission_dir} && javac {base_filename}"
            compile_result = container.exec_run(
                f"timeout 10 sh -c '{compile_cmd}'", workdir="/tmp"
            )

            if compile_result.exit_code == 0:
                return {
                    "success": True,
                    "output_dir": submission_dir,
                    "method": "javac",
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
        """Generate run command for Java."""
        output_dir = compilation_result["output_dir"]

        if compilation_result["method"] == "compilation_server":
            # Run from compilation server directory
            run_command = f"cd {output_dir}; java HarnessMain"
        else:
            # Run from javac compilation directory
            # For harness system, always use HarnessMain class
            run_command = f"cd {output_dir} && java HarnessMain"

        # Add function name and input arguments - Java harnesses expect 3 args
        import json

        function_name = getattr(request, "function_name", "solution")
        input_json = json.dumps(request.test_input).replace('"', '\\"')
        # Java harnesses expect: class_name, function_name, input_json
        run_command += f' "HarnessMain" "{function_name}" "{input_json}"'

        return run_command

    @staticmethod
    def _strip_everything_above_class_or_public(user_code: str) -> str:
        """Remove everything above the first 'class' or 'public' keyword."""
        lines = user_code.split("\n")

        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line.startswith("class ") or stripped_line.startswith(
                "public "
            ):
                # Found the start of actual code, return everything from here down
                result_lines = lines[i:]

                # If first line starts with 'public class', remove 'public' to avoid filename conflicts
                if result_lines[0].strip().startswith("public class"):
                    result_lines[0] = result_lines[0].replace(
                        "public class", "class", 1
                    )
                    print(
                        f"🔧 [JAVA] Converted 'public class' to 'class' to avoid filename conflicts"
                    )

                return "\n".join(result_lines).strip()

        # If no class/public found, return original code (fallback)
        return user_code.strip()

    @staticmethod
    def _generate_java_wrapper(
        function_name: str, user_code: str, question_name: str = None
    ) -> str:
        """Generate Java wrapper using harness system."""
        if not question_name:
            return JavaRunner._generate_java_fallback_wrapper(function_name, user_code)

        # Look for dedicated harness file
        harness_path = (
            f"backend/code_testing/java_harnesses/harnesses/{question_name}/Main.java"
        )

        if os.path.exists(harness_path):
            print(f"🔧 [JAVA] Using dedicated harness for question: {question_name}")

            with open(harness_path, "r") as f:
                harness_content = f.read()

            # Clean user code - remove everything above first 'class' or 'public' keyword
            cleaned_user_code = JavaRunner._strip_everything_above_class_or_public(
                user_code
            )

            print(f"🔧 [JAVA] Stripped imports and declarations above class/public")

            # Replace USER_CODE_PLACEHOLDER with cleaned user code
            wrapped_code = harness_content.replace(
                "// USER_CODE_PLACEHOLDER", cleaned_user_code
            )

            return wrapped_code
        else:
            print(f"❌ [JAVA] No harness found for question: {question_name}")
            print(f"❌ [JAVA] Expected harness at: {harness_path}")
            return JavaRunner._generate_java_fallback_wrapper(function_name, user_code)

    @staticmethod
    def _generate_java_fallback_wrapper(function_name: str, user_code: str) -> str:
        """Fallback Java wrapper for questions without dedicated harness."""
        java_wrapper = f"""import java.util.*;

{user_code}

public class Main {{
    public static void main(String[] args) {{
        if (args.length < 2) {{
            System.out.println("{{\\\"result\\\": \\\"Missing arguments\\\", \\\"execution_time\\\": 0}}");
            return;
        }}
        
        System.out.println("{{\\\"result\\\": \\\"No harness available for this question\\\", \\\"execution_time\\\": 0}}");
    }}
}}"""
        return java_wrapper

    @staticmethod
    def _use_java_compilation_server(container, source_code: str) -> str:
        """Use the Java compilation server to compile source code."""
        try:
            # Check if compilation server is ready
            if (
                not hasattr(container, "_java_compilation_server_ready")
                or not container._java_compilation_server_ready
            ):
                print("❌ [JAVA] Compilation server not ready")
                return None

            compile_start = time.time()
            print(f"🔥 [JAVA] Sending {len(source_code)} chars to compilation server")

            # Encode source code for safe transmission
            encoded_source = base64.b64encode(source_code.encode("utf-8")).decode(
                "ascii"
            )

            # Communication script for TCP connection
            comm_script = f"""#!/bin/bash
# Connect to compilation server and send source code
exec 3<>/dev/tcp/localhost/8901

# Send source code length
echo "{len(source_code)}" >&3

# Send base64-encoded source code and decode it
echo "{encoded_source}" | base64 -d >&3

# Read response
read -u 3 status
read -u 3 result

echo "STATUS:$status"
echo "RESULT:$result"

exec 3<&-
exec 3>&-
"""

            # Write and execute communication script
            script_encoded = base64.b64encode(comm_script.encode()).decode()
            script_create = container.exec_run(
                f"timeout 10 sh -c 'echo {script_encoded} | base64 -d > /tmp/compile_comm.sh && chmod +x /tmp/compile_comm.sh'",
                workdir="/tmp",
            )

            if script_create.exit_code != 0:
                print(f"❌ [JAVA] Failed to create communication script")
                return None

            # Execute the communication script with timeout
            comm_result = container.exec_run(
                f"timeout 10 bash /tmp/compile_comm.sh", workdir="/tmp"
            )

            compile_time = (time.time() - compile_start) * 1000
            print(f"🔥 [JAVA] Communication took {compile_time:.0f}ms")

            if comm_result.exit_code != 0:
                print(f"❌ [JAVA] Communication failed: {comm_result.output.decode()}")
                return None

            # Parse response
            output = comm_result.output.decode("utf-8").strip()
            lines = output.split("\n")

            status_line = None
            result_line = None

            for line in lines:
                if line.startswith("STATUS:"):
                    status_line = line[7:]  # Remove "STATUS:" prefix
                elif line.startswith("RESULT:"):
                    result_line = line[7:]  # Remove "RESULT:" prefix

            if status_line == "SUCCESS" and result_line:
                print(f"✅ [JAVA] Compilation successful, output: {result_line}")
                return result_line
            else:
                print(f"❌ [JAVA] Compilation failed: {result_line}")
                return None

        except Exception as e:
            print(f"❌ [JAVA] Compilation server error: {e}")
            return None
