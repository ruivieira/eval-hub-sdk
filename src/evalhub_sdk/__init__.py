"""EvalHub SDK - Framework adapter SDK for integrating with TrustyAI EvalHub.

This SDK provides a standardized way to create framework adapters that can
be consumed by EvalHub, enabling a "Bring Your Own Framework" (BYOF) approach.
"""

# Core models and interfaces
# API components
from .api import AdapterAPIRouter, create_adapter_api

# Client components
from .client import AdapterClient, AdapterDiscovery
from .models import (
    AdapterConfig,
    AdapterMetadata,
    BenchmarkInfo,
    ErrorResponse,
    EvaluationJob,
    # API models
    EvaluationRequest,
    EvaluationResponse,
    EvaluationResult,
    EvaluationStatus,
    # Framework adapter models
    FrameworkAdapter,
    FrameworkInfo,
    HealthResponse,
    JobStatus,
    ModelConfig,
)

# Server components
from .server import AdapterServer

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Core API models
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
    # Framework adapter components
    "FrameworkAdapter",
    "AdapterConfig",
    "AdapterMetadata",
    # Server components
    "AdapterServer",
    "AdapterAPIRouter",
    "create_adapter_api",
    # Client components
    "AdapterClient",
    "AdapterDiscovery",
]

# Package metadata
__title__ = "evalhub-sdk"
__description__ = (
    "SDK for building framework adapters that integrate with TrustyAI EvalHub"
)
__author__ = "TrustyAI Team"
__author_email__ = "trustyai@redhat.com"
__license__ = "Apache 2.0"
