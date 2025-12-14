"""Unit tests for client components."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from evalhub_sdk.client.adapter_client import AdapterClient, ClientError
from evalhub_sdk.models.api import (
    BenchmarkInfo,
    EvaluationJob,
    EvaluationRequest,
    EvaluationResponse,
    FrameworkInfo,
    HealthResponse,
    JobStatus,
    ModelConfig,
)


class TestAdapterClient:
    """Test cases for AdapterClient."""

    @pytest.fixture
    def mock_response_data(self) -> dict[str, Any]:
        """Mock response data for tests."""
        return {
            "framework_info": {
                "framework_id": "test_framework",
                "name": "Test Framework",
                "version": "1.0.0",
                "description": "Test framework",
                "supported_benchmarks": [
                    {
                        "benchmark_id": "test_bench",
                        "name": "Test Benchmark",
                        "description": "Test description",
                        "category": "testing",
                        "metrics": ["accuracy"],
                    }
                ],
                "supported_model_types": ["gpt"],
                "capabilities": ["text-classification"],
            },
            "health_response": {
                "status": "healthy",
                "framework_id": "test_framework",
                "version": "1.0.0",
                "uptime_seconds": 3600.0,
            },
            "benchmarks": [
                {
                    "benchmark_id": "test_bench",
                    "name": "Test Benchmark",
                    "description": "Test description",
                    "category": "testing",
                    "metrics": ["accuracy"],
                }
            ],
            "evaluation_job": {
                "job_id": "job_123",
                "status": "pending",
                "request": {
                    "benchmark_id": "test_bench",
                    "model": {"name": "test-model"},
                },
                "submitted_at": "2024-01-01T12:00:00Z",
            },
            "evaluation_results": {
                "job_id": "job_123",
                "benchmark_id": "test_bench",
                "model_name": "test-model",
                "results": [
                    {
                        "metric_name": "accuracy",
                        "metric_value": 0.85,
                        "metric_type": "float",
                    }
                ],
                "overall_score": 0.85,
                "num_examples_evaluated": 100,
                "completed_at": "2024-01-01T12:10:00Z",
                "duration_seconds": 600.0,
            },
        }

    @pytest.mark.asyncio
    async def test_client_context_manager(self) -> None:
        """Test AdapterClient as async context manager."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                assert client.base_url == "http://test"
                assert client._client == mock_instance

            # Ensure client was closed
            mock_instance.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_framework_info_success(
        self, mock_response_data: dict[str, Any]
    ) -> None:
        """Test successful get_framework_info call."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data["framework_info"]
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                info = await client.get_framework_info()

                assert isinstance(info, FrameworkInfo)
                assert info.framework_id == "test_framework"
                assert info.name == "Test Framework"
                assert len(info.supported_benchmarks) == 1

            mock_instance.get.assert_called_with("/api/v1/info")

    @pytest.mark.asyncio
    async def test_get_framework_info_http_error(self) -> None:
        """Test get_framework_info with HTTP error."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                with pytest.raises(ClientError, match="HTTP 500"):
                    await client.get_framework_info()

    @pytest.mark.asyncio
    async def test_health_check_success(
        self, mock_response_data: dict[str, Any]
    ) -> None:
        """Test successful health_check call."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data["health_response"]
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                health = await client.health_check()

                assert isinstance(health, HealthResponse)
                assert health.status == "healthy"
                assert health.framework_id == "test_framework"
                assert health.uptime_seconds == 3600.0

            mock_instance.get.assert_called_with("/api/v1/health")

    @pytest.mark.asyncio
    async def test_list_benchmarks_success(
        self, mock_response_data: dict[str, Any]
    ) -> None:
        """Test successful list_benchmarks call."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data["benchmarks"]
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                benchmarks = await client.list_benchmarks()

                assert len(benchmarks) == 1
                assert isinstance(benchmarks[0], BenchmarkInfo)
                assert benchmarks[0].benchmark_id == "test_bench"
                assert benchmarks[0].name == "Test Benchmark"

            mock_instance.get.assert_called_with("/api/v1/benchmarks")

    @pytest.mark.asyncio
    async def test_get_benchmark_info_success(
        self, mock_response_data: dict[str, Any]
    ) -> None:
        """Test successful get_benchmark_info call."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data["benchmarks"][0]
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                benchmark = await client.get_benchmark_info("test_bench")

                assert benchmark is not None
                assert isinstance(benchmark, BenchmarkInfo)
                assert benchmark.benchmark_id == "test_bench"

            mock_instance.get.assert_called_with("/api/v1/benchmarks/test_bench")

    @pytest.mark.asyncio
    async def test_get_benchmark_info_not_found(self) -> None:
        """Test get_benchmark_info with 404 response."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                benchmark = await client.get_benchmark_info("non_existent")
                assert benchmark is None

    @pytest.mark.asyncio
    async def test_submit_evaluation_success(
        self, mock_response_data: dict[str, Any]
    ) -> None:
        """Test successful submit_evaluation call."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = mock_response_data["evaluation_job"]
            mock_instance.post.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                model = ModelConfig(name="test-model")
                request = EvaluationRequest(benchmark_id="test_bench", model=model)

                job = await client.submit_evaluation(request)

                assert isinstance(job, EvaluationJob)
                assert job.job_id == "job_123"
                assert job.status == JobStatus.PENDING

            # Verify the POST was called with correct data
            call_args = mock_instance.post.call_args
            assert call_args[0][0] == "/api/v1/evaluations"

            # Check that json parameter was passed
            assert "json" in call_args[1]
            request_data = call_args[1]["json"]
            assert request_data["benchmark_id"] == "test_bench"
            assert request_data["model"]["name"] == "test-model"

    @pytest.mark.asyncio
    async def test_get_job_status_success(
        self, mock_response_data: dict[str, Any]
    ) -> None:
        """Test successful get_job_status call."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data["evaluation_job"]
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                job = await client.get_job_status("job_123")

                assert job is not None
                assert isinstance(job, EvaluationJob)
                assert job.job_id == "job_123"
                assert job.status == JobStatus.PENDING

            mock_instance.get.assert_called_with("/api/v1/evaluations/job_123")

    @pytest.mark.asyncio
    async def test_get_job_status_not_found(self) -> None:
        """Test get_job_status with 404 response."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                job = await client.get_job_status("non_existent")
                assert job is None

    @pytest.mark.asyncio
    async def test_get_evaluation_results_success(
        self, mock_response_data: dict[str, Any]
    ) -> None:
        """Test successful get_evaluation_results call."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data["evaluation_results"]
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                results = await client.get_evaluation_results("job_123")

                assert results is not None
                assert isinstance(results, EvaluationResponse)
                assert results.job_id == "job_123"
                assert results.benchmark_id == "test_bench"
                assert len(results.results) == 1
                assert results.overall_score == 0.85

            mock_instance.get.assert_called_with("/api/v1/evaluations/job_123/results")

    @pytest.mark.asyncio
    async def test_cancel_job_success(self) -> None:
        """Test successful cancel_job call."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_instance.delete.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                result = await client.cancel_job("job_123")
                assert result is True

            mock_instance.delete.assert_called_with("/api/v1/evaluations/job_123")

    @pytest.mark.asyncio
    async def test_cancel_job_not_found(self) -> None:
        """Test cancel_job with 404 response."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_instance.delete.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                result = await client.cancel_job("non_existent")
                assert result is False

    @pytest.mark.asyncio
    async def test_wait_for_completion_completed(self) -> None:
        """Test wait_for_completion with completed job."""
        completed_job_data = {
            "job_id": "job_123",
            "status": "completed",
            "request": {
                "benchmark_id": "test_bench",
                "model": {"name": "test-model"},
            },
            "submitted_at": "2024-01-01T12:00:00Z",
            "completed_at": "2024-01-01T12:10:00Z",
            "progress": 1.0,
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = completed_job_data
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                job = await client.wait_for_completion("job_123", poll_interval=0.1)

                assert job is not None
                assert job.status == JobStatus.COMPLETED
                assert job.progress == 1.0

    @pytest.mark.asyncio
    async def test_wait_for_completion_timeout(self) -> None:
        """Test wait_for_completion with timeout."""
        running_job_data = {
            "job_id": "job_123",
            "status": "running",
            "request": {
                "benchmark_id": "test_bench",
                "model": {"name": "test-model"},
            },
            "submitted_at": "2024-01-01T12:00:00Z",
            "progress": 0.5,
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = running_job_data
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                job = await client.wait_for_completion(
                    "job_123", timeout=0.2, poll_interval=0.1
                )

                # Should return the last known status (still running)
                assert job is not None
                assert job.status == JobStatus.RUNNING

    @pytest.mark.asyncio
    async def test_connection_error(self) -> None:
        """Test handling of connection errors."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.side_effect = httpx.ConnectError("Connection failed")
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                with pytest.raises(ClientError, match="Connection failed"):
                    await client.health_check()

    @pytest.mark.asyncio
    async def test_timeout_error(self) -> None:
        """Test handling of timeout errors."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.side_effect = httpx.TimeoutException("Request timeout")
            mock_client.return_value = mock_instance

            async with AdapterClient("http://test") as client:
                with pytest.raises(ClientError, match="Request timeout"):
                    await client.health_check()

    def test_client_error_creation(self) -> None:
        """Test ClientError exception creation."""
        error = ClientError("Test error")
        assert str(error) == "Test error"

        error_with_cause = ClientError("Test error", cause=ValueError("Original error"))
        assert str(error_with_cause) == "Test error"
        assert error_with_cause.cause is not None
        assert isinstance(error_with_cause.cause, ValueError)
