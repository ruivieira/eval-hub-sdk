"""EvalHub SDK Models - Standard request/response models for framework adapters."""

from .api import (
    BenchmarkInfo,
    ErrorResponse,
    EvaluationJob,
    # Core API models
    EvaluationRequest,
    EvaluationResponse,
    EvaluationResult,
    EvaluationStatus,
    FrameworkInfo,
    HealthResponse,
    # Status and metadata
    JobStatus,
    ModelConfig,
)
from .framework import (
    AdapterConfig,
    AdapterMetadata,
    # Framework adapter models
    FrameworkAdapter,
)

__all__ = [
    # API models
    "EvaluationRequest",
    "EvaluationResponse",
    "EvaluationJob",
    "EvaluationResult",
    "BenchmarkInfo",
    "ModelConfig",
    "FrameworkInfo",
    "JobStatus",
    "EvaluationStatus",
    "ErrorResponse",
    "HealthResponse",
    # Framework models
    "FrameworkAdapter",
    "AdapterConfig",
    "AdapterMetadata",
]
