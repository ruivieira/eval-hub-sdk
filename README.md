# EvalHub SDK

**Framework Adapter SDK for TrustyAI EvalHub Integration**

The EvalHub SDK provides a standardized way to create framework adapters that can be consumed by EvalHub, enabling a "Bring Your Own Framework" (BYOF) approach for evaluation frameworks.

## Overview

The SDK creates a common API layer that allows EvalHub to communicate with ANY evaluation framework. Users only need to write minimal "glue" code to connect their framework to the standardized interface.

```
EvalHub → (Standard API) → Your Framework Adapter → Your Evaluation Framework
```

## Architecture

```
┌─────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│   EvalHub   │───▶│  Framework Adapter  │───▶│ Your Framework   │
│             │    │  (SDK + Glue Code)  │    │ (LMEval, Custom, │
│             │◀───│                     │◀───│  RAGAS, etc.)    │
└─────────────┘    └─────────────────────┘    └──────────────────┘
      │                        │
      │            ┌─────────────────────┐
      └───────────▶│   Standard API      │
                   │ /health             │
                   │ /info               │
                   │ /benchmarks         │
                   │ /evaluations        │
                   └─────────────────────┘
```

### Key Components

1. **Standard API**: Common REST endpoints that all adapters must implement
2. **Framework Adapter Base Class**: Abstract base class with the adapter contract
3. **Server Components**: FastAPI-based server for exposing the standard API
4. **Client Components**: HTTP client for EvalHub to communicate with adapters
5. **Data Models**: Pydantic models for requests, responses, and metadata

## Quick Start

### 1. Installation

```bash
# Install from PyPI (when available)
pip install evalhub-sdk

# Install from source
git clone https://github.com/trustyai-explainability/evalhub-sdk.git
cd evalhub-sdk
pip install -e .[dev]
```

### 2. Create Your Adapter

Create a new Python file for your adapter:

```python
# my_framework_adapter.py
from evalhub_sdk import FrameworkAdapter, AdapterConfig, BenchmarkInfo
from evalhub_sdk.models import *

class MyFrameworkAdapter(FrameworkAdapter):
    async def initialize(self):
        """Initialize your framework here"""
        # Load your evaluation framework
        pass

    async def list_benchmarks(self) -> List[BenchmarkInfo]:
        """Return available benchmarks from your framework"""
        return [
            BenchmarkInfo(
                benchmark_id="my_benchmark",
                name="My Custom Benchmark",
                description="A custom benchmark",
                category="reasoning",
                metrics=["accuracy", "f1_score"]
            )
        ]

    async def submit_evaluation(self, request: EvaluationRequest) -> EvaluationJob:
        """Submit evaluation to your framework"""
        # Translate request to your framework's format
        # Run evaluation
        # Return job information
        pass

    # Implement other required methods...
```

### 3. Run Your Adapter

```python
# run_adapter.py
from evalhub_sdk import AdapterServer, AdapterConfig
from my_framework_adapter import MyFrameworkAdapter

config = AdapterConfig(
    framework_id="my_framework",
    adapter_name="My Framework Adapter",
    port=8080
)

adapter = MyFrameworkAdapter(config)
server = AdapterServer(adapter)
server.run()
```

### 4. Test Your Adapter

```bash
# Run your adapter
python run_adapter.py

# Test health check
curl http://localhost:8080/api/v1/health

# Get framework info
curl http://localhost:8080/api/v1/info

# List benchmarks
curl http://localhost:8080/api/v1/benchmarks
```

## Complete Examples

### LightEval Framework Example
See [examples/lighteval_adapter/](examples/lighteval_adapter/) for a production-ready example with:

- ✅ **Real Framework Integration** - Complete LightEval wrapper
- ✅ **Container Deployment** - Docker/Podman container with health checks
- ✅ **External Client Demo** - Jupyter notebook making HTTP requests to containerized adapter
- ✅ **API Testing** - All endpoints tested with real evaluation jobs from external client
- ✅ **Production Ready** - Configuration, logging, error handling

Try the demo (notebook runs **outside** the container):
```bash
# Container: LightEval + adapter
# Notebook: External HTTP client
cd examples/
jupyter notebook lighteval_demo_external.ipynb
```

## Standard API Endpoints

All framework adapters expose the same REST API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/info` | GET | Framework information |
| `/benchmarks` | GET | List available benchmarks |
| `/benchmarks/{id}` | GET | Get benchmark details |
| `/evaluations` | POST | Submit evaluation job |
| `/evaluations/{job_id}` | GET | Get job status |
| `/evaluations/{job_id}/results` | GET | Get evaluation results |
| `/evaluations/{job_id}` | DELETE | Cancel job |
| `/evaluations/{job_id}/stream` | GET | Stream job updates |

### Example API Usage

```bash
# Submit evaluation
curl -X POST http://localhost:8080/api/v1/evaluations \
  -H "Content-Type: application/json" \
  -d '{
    "benchmark_id": "my_benchmark",
    "model": {
      "name": "gpt-4",
      "provider": "openai",
      "parameters": {
        "temperature": 0.1,
        "max_tokens": 100
      }
    },
    "num_examples": 100,
    "experiment_name": "test_evaluation"
  }'

# Check job status
curl http://localhost:8080/api/v1/evaluations/{job_id}

# Get results
curl http://localhost:8080/api/v1/evaluations/{job_id}/results
```

## Framework Adapter Interface

### Required Methods

Your adapter must implement these abstract methods:

```python
class FrameworkAdapter(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the framework"""

    @abstractmethod
    async def get_framework_info(self) -> FrameworkInfo:
        """Get framework information"""

    @abstractmethod
    async def list_benchmarks(self) -> List[BenchmarkInfo]:
        """List available benchmarks"""

    @abstractmethod
    async def get_benchmark_info(self, benchmark_id: str) -> Optional[BenchmarkInfo]:
        """Get benchmark details"""

    @abstractmethod
    async def submit_evaluation(self, request: EvaluationRequest) -> EvaluationJob:
        """Submit evaluation job"""

    @abstractmethod
    async def get_job_status(self, job_id: str) -> Optional[EvaluationJob]:
        """Get job status"""

    @abstractmethod
    async def get_evaluation_results(self, job_id: str) -> Optional[EvaluationResponse]:
        """Get evaluation results"""

    @abstractmethod
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel job"""

    @abstractmethod
    async def health_check(self) -> HealthResponse:
        """Perform health check"""

    @abstractmethod
    async def shutdown(self) -> None:
        """Graceful shutdown"""
```

### Data Models

Key data models for requests and responses:

```python
# Evaluation request from EvalHub
class EvaluationRequest(BaseModel):
    benchmark_id: str
    model: ModelConfig
    num_examples: Optional[int] = None
    num_few_shot: Optional[int] = None
    benchmark_config: Dict[str, Any] = {}
    experiment_name: Optional[str] = None

# Model configuration
class ModelConfig(BaseModel):
    name: str
    provider: Optional[str] = None
    parameters: Dict[str, Any] = {}
    device: Optional[str] = None
    batch_size: Optional[int] = None

# Evaluation job tracking
class EvaluationJob(BaseModel):
    job_id: str
    status: JobStatus  # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    request: EvaluationRequest
    submitted_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: Optional[float] = None  # 0.0 to 1.0
    error_message: Optional[str] = None

# Evaluation results
class EvaluationResponse(BaseModel):
    job_id: str
    benchmark_id: str
    model_name: str
    results: List[EvaluationResult]
    overall_score: Optional[float] = None
    num_examples_evaluated: int
    completed_at: datetime
    duration_seconds: float

# Individual metric result
class EvaluationResult(BaseModel):
    metric_name: str
    metric_value: Union[float, int, str, bool]
    metric_type: str = "float"
    num_samples: Optional[int] = None
```

## CLI Usage

The SDK includes a CLI tool for running and testing adapters:

```bash
# Run an adapter
evalhub-adapter run my_adapter:MyAdapter --port 8080

# Get adapter info
evalhub-adapter info http://localhost:8080

# Check adapter health
evalhub-adapter health http://localhost:8080

# Discover multiple adapters
evalhub-adapter discover http://adapter1:8080 http://adapter2:8081
```

## EvalHub Integration

### Client Usage

EvalHub uses the provided client to communicate with adapters:

```python
from evalhub_sdk import AdapterClient, EvaluationRequest, ModelConfig

async with AdapterClient("http://adapter:8080") as client:
    # Get framework info
    info = await client.get_framework_info()
    print(f"Framework: {info.name}")

    # List benchmarks
    benchmarks = await client.list_benchmarks()
    print(f"Available benchmarks: {len(benchmarks)}")

    # Submit evaluation
    request = EvaluationRequest(
        benchmark_id="custom_benchmark",
        model=ModelConfig(
            name="llama-7b",
            provider="vllm",
            parameters={"temperature": 0.1}
        ),
        num_examples=100
    )

    job = await client.submit_evaluation(request)
    print(f"Job submitted: {job.job_id}")

    # Wait for completion
    final_job = await client.wait_for_completion(job.job_id)

    # Get results
    if final_job.status == JobStatus.COMPLETED:
        results = await client.get_evaluation_results(job.job_id)
        print(f"Results: {len(results.results)} metrics")
```

### Discovery Service

EvalHub can automatically discover and manage multiple adapters:

```python
from evalhub_sdk import AdapterDiscovery

discovery = AdapterDiscovery()

# Register adapters
discovery.register_adapter("http://lmeval-adapter:8080")
discovery.register_adapter("http://ragas-adapter:8081")

# Start health monitoring
await discovery.start_health_monitoring()

# Get healthy adapters
healthy_adapters = discovery.get_healthy_adapters()

# Find adapter for specific framework
lmeval_adapter = discovery.get_adapter_for_framework("lm_evaluation_harness")
```

## Configuration

### Adapter Configuration

```python
config = AdapterConfig(
    framework_id="my_framework",
    adapter_name="My Framework Adapter",
    version="1.0.0",
    host="0.0.0.0",
    port=8080,
    max_concurrent_jobs=5,
    job_timeout_seconds=3600,
    log_level="INFO",
    framework_config={
        # Framework-specific settings
        "model_cache_dir": "/models",
        "device": "cuda",
        "batch_size": 8
    }
)
```

### Configuration File

```yaml
# adapter_config.yaml
framework_id: "my_framework"
adapter_name: "My Framework Adapter"
version: "1.0.0"
host: "0.0.0.0"
port: 8080
max_concurrent_jobs: 10
job_timeout_seconds: 7200
log_level: "DEBUG"

framework_config:
  model_cache_dir: "/data/models"
  device: "cuda:0"
  batch_size: 16
  enable_caching: true
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

COPY . /app
WORKDIR /app

RUN pip install evalhub-sdk
RUN pip install -e .  # Install your adapter

EXPOSE 8080

CMD ["evalhub-adapter", "run", "my_adapter:MyAdapter", "--port", "8080"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-framework-adapter
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-framework-adapter
  template:
    metadata:
      labels:
        app: my-framework-adapter
    spec:
      containers:
      - name: adapter
        image: my-framework-adapter:latest
        ports:
        - containerPort: 8080
        env:
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: my-framework-adapter
spec:
  selector:
    app: my-framework-adapter
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
```

## Development

### Project Structure

The SDK uses a modern Python project structure:

```
evalhub-sdk/
├── src/evalhub_sdk/     # Source code (src layout)
│   ├── api/             # API endpoints and routing
│   ├── client/          # HTTP client for EvalHub
│   ├── models/          # Pydantic data models
│   ├── server/          # FastAPI server components
│   └── utils/           # Utilities and helpers
├── tests/               # Test suite
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── examples/            # Example adapters
│   ├── custom_framework_adapter.py
│   └── lighteval_adapter/
└── pyproject.toml       # Project configuration
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/trustyai-explainability/evalhub-sdk.git
cd evalhub-sdk

# Install in development mode with all dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/evalhub_sdk --cov-report=html

# Run type checking
mypy src/evalhub_sdk

# Run linting
ruff check src/ tests/
ruff format src/ tests/
```

### Testing Your Adapter

```python
import pytest
from evalhub_sdk.client import AdapterClient

@pytest.mark.asyncio
async def test_adapter_health():
    async with AdapterClient("http://localhost:8080") as client:
        health = await client.health_check()
        assert health.status == "healthy"

@pytest.mark.asyncio
async def test_list_benchmarks():
    async with AdapterClient("http://localhost:8080") as client:
        benchmarks = await client.list_benchmarks()
        assert len(benchmarks) > 0
        assert all(b.benchmark_id for b in benchmarks)
```

### Development Server

```bash
# Run with auto-reload for development
evalhub-adapter run my_adapter:MyAdapter --reload --log-level DEBUG
```

### Quality Assurance

The project uses comprehensive QA tools:

- **Testing**: pytest with async support, coverage reporting
- **Type Checking**: mypy with strict configuration
- **Linting**: ruff for fast, modern Python linting
- **Formatting**: ruff format for consistent code style
- **Pre-commit**: Automated quality checks on commit

Run all quality checks:
```bash
# Format code
ruff format .

# Lint and fix issues
ruff check --fix .

# Type check
mypy src/evalhub_sdk

# Run full test suite
pytest -v --cov=src/evalhub_sdk
```

## Best Practices

### 1. Error Handling

```python
async def submit_evaluation(self, request: EvaluationRequest) -> EvaluationJob:
    try:
        # Validate request
        if not request.benchmark_id:
            raise ValueError("Benchmark ID is required")

        # Check if benchmark exists
        benchmark = await self.get_benchmark_info(request.benchmark_id)
        if not benchmark:
            raise ValueError(f"Benchmark '{request.benchmark_id}' not found")

        # Submit job
        job = await self._submit_to_framework(request)
        return job

    except Exception as e:
        # Log error and create failed job
        logger.exception(f"Failed to submit evaluation: {e}")
        job = self._create_failed_job(str(e))
        return job
```

### 2. Progress Tracking

```python
async def _run_evaluation(self, job_id: str):
    job = self._jobs[job_id]

    try:
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)

        # Step 1: Load model
        job.progress = 0.1
        job.current_step = "Loading model"
        await self._load_model(job.request.model)

        # Step 2: Load dataset
        job.progress = 0.2
        job.current_step = "Loading dataset"
        dataset = await self._load_dataset(job.request.benchmark_id)

        # Step 3: Run evaluation
        for i, batch in enumerate(dataset.batches):
            job.progress = 0.2 + 0.7 * (i / len(dataset.batches))
            job.current_step = f"Evaluating batch {i+1}/{len(dataset.batches)}"
            await self._evaluate_batch(batch)

        # Step 4: Compute metrics
        job.progress = 0.9
        job.current_step = "Computing metrics"
        results = await self._compute_metrics()

        job.status = JobStatus.COMPLETED
        job.progress = 1.0
        job.completed_at = datetime.now(timezone.utc)

    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
```

### 3. Resource Management

```python
async def initialize(self):
    # Check available resources
    if torch.cuda.is_available():
        self.device = "cuda"
        self.max_batch_size = 32
    else:
        self.device = "cpu"
        self.max_batch_size = 8

    # Initialize model cache
    self.model_cache = {}

    # Set up cleanup
    atexit.register(self._cleanup_resources)

async def _cleanup_resources(self):
    # Clear model cache
    for model in self.model_cache.values():
        del model

    # Free GPU memory
    if self.device == "cuda":
        torch.cuda.empty_cache()
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://trustyai.org/docs](https://trustyai.org/docs)
- **Issues**: [GitHub Issues](https://github.com/trustyai-explainability/trustyai-service/issues)
- **Discussions**: [GitHub Discussions](https://github.com/trustyai-explainability/trustyai-service/discussions)

## Related Projects

- **TrustyAI EvalHub**: The main evaluation orchestration platform
- **TrustyAI Service**: AI explainability and bias detection service
- **OpenShift AI**: Red Hat's AI/ML platform
