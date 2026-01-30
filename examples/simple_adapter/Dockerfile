FROM registry.access.redhat.com/ubi9/python-312

# Set working directory
WORKDIR /app

# Install adapter SDK and dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy adapter implementation
COPY simple_adapter.py .

# The adapter reads job spec from /meta/job.json (mounted by K8s, configurable via EVALHUB_JOB_SPEC_PATH)
# and communicates with the sidecar at http://localhost:8080
CMD ["python", "simple_adapter.py"]
