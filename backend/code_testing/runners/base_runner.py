"""
Base runner interface for all language-specific runners.
"""

import uuid
import base64
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from backend.models.questions import DockerRunRequest


class BaseRunner(ABC):
    """Base class for all language runners with static methods."""

    @staticmethod
    @abstractmethod
    def prepare_code(request: DockerRunRequest) -> str:
        """
        Prepare the user code with language-specific wrapper/harness.
        Returns the wrapped code ready for execution.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_filename(request: DockerRunRequest) -> str:
        """
        Generate a unique filename for this submission.
        Returns the filename to use for the code file.
        """
        pass

    @staticmethod
    @abstractmethod
    def compile(
        container, request: DockerRunRequest, filename: str, wrapped_code: str
    ) -> Dict[str, Any]:
        """
        Compile the code if needed.
        Returns compilation result with 'success', 'output_dir', 'binary_path', etc.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_run_command(
        request: DockerRunRequest, filename: str, compilation_result: Dict[str, Any]
    ) -> str:
        """
        Generate the run command for executing the code.
        Returns the command string to execute.
        """
        pass

    @staticmethod
    def create_submission_directory(container, submission_id: str) -> str:
        """
        Create a unique submission directory.
        Returns the directory path.
        """
        submission_dir = f"/tmp/submission_{submission_id}"

        dir_create_result = container.exec_run(
            f"timeout 10 mkdir -p {submission_dir}",
            workdir="/tmp",
        )

        if dir_create_result.exit_code != 0:
            raise Exception(
                f"Failed to create submission directory: {dir_create_result.output.decode('utf-8')}"
            )

        return submission_dir

    @staticmethod
    def write_code_file(container, file_path: str, code: str) -> None:
        """
        Write code to a file in the container.
        """
        encoded_code = base64.b64encode(code.encode("utf-8")).decode("ascii")

        create_result = container.exec_run(
            f"timeout 10 sh -c 'echo {encoded_code} | base64 -d > {file_path}'",
            workdir="/tmp",
        )

        if create_result.exit_code != 0:
            raise Exception(
                f"Failed to create file: {create_result.output.decode('utf-8')}"
            )
