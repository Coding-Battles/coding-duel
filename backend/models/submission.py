from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class TimeComplexity(BaseModel):
    code: str


class TimeComplexityResponse(BaseModel):
    time_complexity: str


class TestCaseResult(BaseModel):
    input: Dict[str, Any]
    expected_output: Any
    actual_output: Optional[str]
    passed: bool
    error: Optional[str]
    execution_time: Optional[float]


class RunTestCasesRequest(BaseModel):
    code: str
    language: str
    question_name: str  # Changed from test_cases to question_name
    timeout: Optional[int] = 5


class RunTestCasesResponse(BaseModel):
    success: bool
    test_results: List[TestCaseResult]
    total_passed: int
    total_failed: int
    error: Optional[str]


class DockerRunRequest(BaseModel):
    code: str
    language: str
    test_input: dict
    timeout: int = 5
