"""Core API models for the EvalHub SDK common interface."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class JobStatus(str, Enum):
    """Standard job status values."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EvaluationStatus(str, Enum):
    """Evaluation-specific status values."""

    INITIALIZING = "initializing"
    LOADING_MODEL = "loading_model"
    LOADING_DATASET = "loading_dataset"
    EVALUATING = "evaluating"
    SCORING = "scoring"
    FINALIZING = "finalizing"


class ModelConfig(BaseModel):
    """Configuration for the model being evaluated."""

    model_config = ConfigDict(extra="allow")

    name: str = Field(..., description="Model name or identifier")
    provider: Optional[str] = Field(
        None, description="Model provider (e.g., 'vllm', 'transformers')"
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Model-specific parameters (temperature, max_tokens, etc.)",
    )
    device: Optional[str] = Field(None, description="Device specification")
    batch_size: Optional[int] = Field(None, description="Batch size for evaluation")

    def merge_with_defaults(self, defaults: dict[str, Any]) -> "ModelConfig":
        """Merge configuration with default values."""
        merged_params = {**defaults, **self.parameters}
        return self.model_copy(update={"parameters": merged_params})


class BenchmarkInfo(BaseModel):
    """Information about an available benchmark."""

    benchmark_id: str = Field(..., description="Unique benchmark identifier")
    name: str = Field(..., description="Human-readable benchmark name")
    description: Optional[str] = Field(None, description="Benchmark description")
    category: Optional[str] = Field(None, description="Benchmark category")
    tags: list[str] = Field(default_factory=list, description="Benchmark tags")
    metrics: list[str] = Field(default_factory=list, description="Available metrics")
    dataset_size: Optional[int] = Field(
        None, description="Number of examples in dataset"
    )
    supports_few_shot: bool = Field(
        True, description="Whether benchmark supports few-shot evaluation"
    )
    default_few_shot: Optional[int] = Field(
        None, description="Default number of few-shot examples"
    )
    custom_config_schema: Optional[dict[str, Any]] = Field(
        None, description="JSON schema for custom benchmark configuration"
    )


class EvaluationRequest(BaseModel):
    """Request to run an evaluation."""

    benchmark_id: str = Field(..., description="Benchmark to evaluate on")
    model: ModelConfig = Field(..., description="Model configuration")

    # Evaluation parameters
    num_examples: Optional[int] = Field(
        None, description="Number of examples to evaluate (None = all)"
    )
    num_few_shot: Optional[int] = Field(None, description="Number of few-shot examples")
    random_seed: Optional[int] = Field(
        42, description="Random seed for reproducibility"
    )

    # Custom benchmark configuration
    benchmark_config: dict[str, Any] = Field(
        default_factory=dict, description="Benchmark-specific configuration"
    )

    # Job metadata
    experiment_name: Optional[str] = Field(
        None, description="Name for this evaluation experiment"
    )
    tags: dict[str, str] = Field(
        default_factory=dict, description="Custom tags for the job"
    )
    priority: int = Field(0, description="Job priority (higher = more priority)")


class EvaluationResult(BaseModel):
    """Individual evaluation result."""

    metric_name: str = Field(..., description="Name of the metric")
    metric_value: Union[float, int, str, bool] = Field(..., description="Metric value")
    metric_type: str = Field(
        "float", description="Type of metric (float, int, accuracy, etc.)"
    )
    confidence_interval: Optional[tuple[float, float]] = Field(
        None, description="95% confidence interval if available"
    )

    # Additional metadata
    num_samples: Optional[int] = Field(
        None, description="Number of samples used for this metric"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metric-specific metadata"
    )


class EvaluationJob(BaseModel):
    """Evaluation job information."""

    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    evaluation_status: Optional[EvaluationStatus] = Field(
        None, description="Detailed evaluation status"
    )

    # Request information
    request: EvaluationRequest = Field(..., description="Original evaluation request")

    # Timing information
    submitted_at: datetime = Field(..., description="When the job was submitted")
    started_at: Optional[datetime] = Field(None, description="When evaluation started")
    completed_at: Optional[datetime] = Field(
        None, description="When evaluation completed"
    )

    # Progress information
    progress: Optional[float] = Field(
        None, description="Progress percentage (0.0 to 1.0)"
    )
    current_step: Optional[str] = Field(None, description="Current step description")
    total_steps: Optional[int] = Field(None, description="Total number of steps")
    completed_steps: Optional[int] = Field(
        None, description="Number of completed steps"
    )

    # Error information
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_details: Optional[dict[str, Any]] = Field(
        None, description="Detailed error information"
    )

    # Resource usage
    estimated_duration: Optional[int] = Field(
        None, description="Estimated duration in seconds"
    )
    actual_duration: Optional[int] = Field(
        None, description="Actual duration in seconds"
    )


class EvaluationResponse(BaseModel):
    """Response containing evaluation results."""

    job_id: str = Field(..., description="Job identifier")
    benchmark_id: str = Field(..., description="Benchmark that was evaluated")
    model_name: str = Field(..., description="Model that was evaluated")

    # Results
    results: list[EvaluationResult] = Field(..., description="Evaluation results")

    # Summary statistics
    overall_score: Optional[float] = Field(
        None, description="Overall score if applicable"
    )
    num_examples_evaluated: int = Field(
        ..., description="Number of examples actually evaluated"
    )

    # Metadata
    evaluation_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Framework-specific evaluation metadata"
    )
    completed_at: datetime = Field(..., description="When evaluation was completed")
    duration_seconds: float = Field(..., description="Total evaluation time")


class FrameworkInfo(BaseModel):
    """Information about a framework adapter."""

    framework_id: str = Field(..., description="Unique framework identifier")
    name: str = Field(..., description="Framework display name")
    version: str = Field(..., description="Framework version")
    description: Optional[str] = Field(None, description="Framework description")

    # Capabilities
    supported_benchmarks: list[BenchmarkInfo] = Field(
        default_factory=list, description="Benchmarks supported by this framework"
    )
    supported_model_types: list[str] = Field(
        default_factory=list,
        description="Model types supported (e.g., 'transformers', 'vllm')",
    )

    # Configuration schema
    default_model_config: dict[str, Any] = Field(
        default_factory=dict, description="Default model configuration"
    )
    config_schema: Optional[dict[str, Any]] = Field(
        None, description="JSON schema for framework configuration"
    )

    # Metadata
    author: Optional[str] = Field(None, description="Framework adapter author")
    contact: Optional[str] = Field(None, description="Contact information")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    repository_url: Optional[str] = Field(None, description="Source repository URL")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Human-readable error message")
    error_code: Optional[str] = Field(None, description="Framework-specific error code")
    details: Optional[dict[str, Any]] = Field(
        None, description="Additional error details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When error occurred"
    )
    request_id: Optional[str] = Field(None, description="Request ID for debugging")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(
        ..., description="Health status ('healthy', 'unhealthy', 'degraded')"
    )
    framework_id: str = Field(..., description="Framework identifier")
    version: str = Field(..., description="Framework adapter version")

    # Dependency status
    dependencies: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Status of framework dependencies"
    )

    # Resource information
    memory_usage: Optional[dict[str, Any]] = Field(
        None, description="Memory usage information"
    )
    gpu_usage: Optional[dict[str, Any]] = Field(
        None, description="GPU usage information"
    )

    # Timing
    uptime_seconds: Optional[float] = Field(
        None, description="Adapter uptime in seconds"
    )
    last_evaluation_time: Optional[datetime] = Field(
        None, description="Time of last evaluation"
    )

    # Additional info
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional health metadata"
    )
