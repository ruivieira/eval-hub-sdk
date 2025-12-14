# LightEval Framework Adapter Container
FROM registry.access.redhat.com/ubi9-minimal:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install Python 3.11 and system dependencies
RUN microdnf install -y \
    python3.11 \
    python3.11-pip \
    git \
    gcc \
    gcc-c++ \
    make \
    && microdnf clean all

# Create Python symlinks
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/pip3.11 /usr/bin/pip

# Create app user with home directory and set up directories
RUN useradd -r -g root -u 1001 -m appuser
RUN mkdir -p /app /tmp/lighteval_cache /tmp/lighteval_output
RUN chown -R appuser:root /app /tmp/lighteval_cache /tmp/lighteval_output /home/appuser && \
    chmod -R g=u /app /tmp/lighteval_cache /tmp/lighteval_output /home/appuser

# Set working directory
WORKDIR /app

# Copy EvalHub SDK source
COPY --chown=appuser:root ../../src ./src/
COPY --chown=appuser:root ../../pyproject.toml ./

# Copy lighteval adapter files
COPY --chown=appuser:root examples/lighteval_adapter/lighteval_adapter.py ./
COPY --chown=appuser:root examples/lighteval_adapter/requirements.txt ./requirements.txt
COPY --chown=appuser:root examples/lighteval_adapter/config.yaml ./config.yaml

# Switch to app user
USER appuser

# Install EvalHub SDK from local source
RUN pip install --user -e .

RUN pip install --user torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies with faster resolver
RUN pip install --user --no-deps -r requirements.txt || \
    pip install --user -r requirements.txt

# Add user's local bin to PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Set Python path to include src
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the LightEval adapter
CMD ["python", "lighteval_adapter.py", "8000"]
