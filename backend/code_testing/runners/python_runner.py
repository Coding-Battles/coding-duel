"""
Python-specific runner implementation.
"""

import os
import uuid
import json
from typing import Dict, Any
from backend.models.questions import DockerRunRequest
from backend.code_testing.language_config import LANGUAGE_CONFIG
from .base_runner import BaseRunner


class PythonRunner(BaseRunner):
    """Python-specific code runner with static methods."""

    @staticmethod
    def prepare_code(request: DockerRunRequest) -> str:
        """Prepare Python code with wrapper template."""
        config = LANGUAGE_CONFIG["python"]

        # Use string replacement instead of .format() to avoid issues with special characters
        wrapped_code = (
            config["wrapper_template"]
            .replace("{code}", request.code)
            .replace("{function_name}", request.function_name)
        )

        return wrapped_code

    @staticmethod
    def get_filename(request: DockerRunRequest) -> str:
        """Generate unique filename for Python submission."""
        submission_id = str(uuid.uuid4())[:8]
        return f"solution_{submission_id}.py"

    @staticmethod
    def compile(
        container, request: DockerRunRequest, filename: str, wrapped_code: str
    ) -> Dict[str, Any]:
        """Python doesn't need compilation."""
        submission_dir = os.path.dirname(filename)
        return {"success": True, "output_dir": submission_dir, "method": "interpreted"}

    @staticmethod
    def get_run_command(
        request: DockerRunRequest, filename: str, compilation_result: Dict[str, Any]
    ) -> str:
        """Generate run command for Python."""
        output_dir = compilation_result["output_dir"]
        base_filename = os.path.basename(filename)

        # Python run command with arguments
        function_name = getattr(request, "function_name", "solution")
        input_json = json.dumps(request.test_input).replace('"', '\\"')

        run_command = f'cd {output_dir} && python {base_filename} "{function_name}" "{input_json}"'

        return run_command
