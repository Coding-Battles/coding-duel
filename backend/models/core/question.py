"""
Question and test case related Pydantic models
Centralized models for problem, test case, and submission data structures
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ProgrammingLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    TYPESCRIPT = "typescript"


class Problem(BaseModel):
    id: int
    title: str
    difficulty: str = Field(..., pattern="^(Easy|Medium|Hard)$")
    status: str = Field(..., pattern="^(Solved|Attempted|Not Attempted)$")
    category: str
    submittedAt: Optional[str] = None


class TestCase(BaseModel):
    input: Dict[str, Any]
    expected_output: str
    actual_output: str
    passed: bool
    error: Optional[str] = None
    execution_time: float


class QuestionData(BaseModel):
    id: str
    title: str
    problemDescription: str
    examples: List[Dict[str, str]]
    constraints: List[str]
    starter_code: Dict[str, str] = Field(default_factory=dict)  # {language: code}
    test_cases: Optional[List[TestCase]] = None
    difficulty: DifficultyLevel | str
    category: Optional[str] = None


# Legacy models from existing questions.py
class TimeComplexity(BaseModel):
    code: str


class TimeComplexityResponse(BaseModel):
    time_complexity: str


class TestCaseResult(BaseModel):
    input: Dict[str, Any]
    expected_output: Any
    actual_output: Optional[str] = None
    passed: bool
    error: Optional[str] = None
    execution_time: Optional[float] = None


class CodeTestResult(BaseModel):
    message: str
    code: str
    player_id: str
    player_name: str
    success: bool
    test_results: List[TestCaseResult]
    total_passed: int
    total_failed: int
    error: Optional[str] = None
    complexity: Optional[str] = None
    implement_time: Optional[int] = None
    final_time: Optional[int] = None


class PlayerFinalStats(BaseModel):
    player_name: str
    player_id: str
    implement_time: int
    time_complexity: str
    final_time: int


class RunTestCasesRequest(BaseModel):
    player_id: str
    code: str
    language: str
    question_name: str
    timeout: Optional[int] = 5
    timer: int


class RunTestCasesResponse(BaseModel):
    success: bool
    test_results: List[TestCaseResult]
    total_passed: int
    total_failed: int
    error: Optional[str] = None


class DockerRunRequest(BaseModel):
    code: str
    language: str
    test_input: Dict
    timeout: int = 5
    function_name: Optional[str] = "solution"


class StarterCode(BaseModel):
    python: str
    javascript: str
    java: str
    cpp: str


class SolutionApproach(BaseModel):
    time_complexity: str
    space_complexity: str
    approach: str


class QuestionMetadata(BaseModel):
    acceptance_rate: str
    total_accepted: str
    total_submissions: str
    created_at: str
    last_updated: str


# Updated QuestionData that matches the original structure
class LegacyQuestionData(BaseModel):
    id: str
    title: str
    difficulty: str
    tags: Optional[List[str]] = None
    description_html: str
    starter_code: StarterCode