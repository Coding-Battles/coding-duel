"""
Core models package
Centralized Pydantic models for the coding duel application
"""

# User models
from .user import (
    PlayerStatus,
    BaseUser,
    CustomUser,
    TestCase,
    TestResultsData,
    PlayerInfo,
    Player,
    OpponentData,
    GameParticipant,
    UserStats
)

# Game models
from .game import (
    GameStatus,
    DifficultyLevel,
    DifficultyState,
    GameState,
    PlayerGameState,
    GameUpdate,
    MatchFoundData,
    MatchFoundResponse,
    QueueStatus,
    QueueStatusResponse,
    GameHistoryItem,
    EmojiRequest
)

# Question models
from .question import (
    Problem,
    QuestionData,
    TimeComplexity,
    TimeComplexityResponse,
    TestCaseResult,
    CodeTestResult,
    PlayerFinalStats,
    RunTestCasesRequest,
    RunTestCasesResponse,
    DockerRunRequest,
    StarterCode,
    SolutionApproach,
    QuestionMetadata,
    LegacyQuestionData,
    ProgrammingLanguage
)

# Socket models
from .socket import (
    JoinGameData,
    CodeUpdateData,
    InstantCodeUpdateData,
    PlayerStatusUpdateData,
    SubmitSolutionData,
    LeaveGameData,
    JoinQueueData,
    LeaveQueueData,
    GameJoinedResponse,
    GameStartResponse,
    OpponentCodeReadyResponse,
    PlayerCodeUpdatedResponse,
    PlayerLanguageChangedResponse,
    PlayerStatusChangedResponse,
    SolutionSubmittedResponse,
    GameFinishedResponse,
    PlayerLeftResponse,
    ErrorResponse
)

# API models
from .api import (
    CreateGameRequest,
    UpdateGameRequest,
    SubmitCodeRequest,
    JoinQueueRequest,
    CreateGameResponse,
    GameStatusResponse,
    SubmitCodeResponse,
    QueueStatusResponse,
    GameHistoryResponse,
    UserStatsResponse,
    QuestionListResponse,
    QuestionDetailsResponse,
    ApiResponse,
    ApiError,
    PaginationParams,
    QueryParams
)

__all__ = [
    # User models
    "PlayerStatus", "BaseUser", "CustomUser", "TestCase", "TestResultsData",
    "PlayerInfo", "Player", "OpponentData", "GameParticipant", "UserStats",
    
    # Game models  
    "GameStatus", "DifficultyLevel", "DifficultyState", "GameState",
    "PlayerGameState", "GameUpdate", "MatchFoundData", "MatchFoundResponse",
    "QueueStatus", "QueueStatusResponse", "GameHistoryItem", "EmojiRequest",
    
    # Question models
    "Problem", "QuestionData", "TimeComplexity", "TimeComplexityResponse",
    "TestCaseResult", "CodeTestResult", "PlayerFinalStats", "RunTestCasesRequest",
    "RunTestCasesResponse", "DockerRunRequest", "StarterCode", "SolutionApproach",
    "QuestionMetadata", "LegacyQuestionData", "ProgrammingLanguage",
    
    # Socket models
    "JoinGameData", "CodeUpdateData", "InstantCodeUpdateData", "PlayerStatusUpdateData",
    "SubmitSolutionData", "LeaveGameData", "JoinQueueData", "LeaveQueueData",
    "GameJoinedResponse", "GameStartResponse", "OpponentCodeReadyResponse",
    "PlayerCodeUpdatedResponse", "PlayerLanguageChangedResponse", "PlayerStatusChangedResponse",
    "SolutionSubmittedResponse", "GameFinishedResponse", "PlayerLeftResponse", "ErrorResponse",
    
    # API models
    "CreateGameRequest", "UpdateGameRequest", "SubmitCodeRequest", "JoinQueueRequest",
    "CreateGameResponse", "GameStatusResponse", "SubmitCodeResponse", "QueueStatusResponse",
    "GameHistoryResponse", "UserStatsResponse", "QuestionListResponse", "QuestionDetailsResponse",
    "ApiResponse", "ApiError", "PaginationParams", "QueryParams"
]