# Use Python 3.11 as base image to match the workflows
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Azure CLI and uv
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Azure CLI (needed for authentication in container)
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install uv package manager (matching workflow setup)
RUN pip install uv

# Copy project files (including README.md required by pyproject.toml)
COPY pyproject.toml uv.lock* README.md LICENSE ./
COPY src/ ./src/
COPY scripts/ ./scripts/

# Install dependencies using uv sync (matching workflow)
RUN uv sync

# Set environment variables for the MCP server
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Create a non-root user for security
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Default command to run the MCP server
CMD ["uv", "run", "azure-storage-mcp"]

# Health check to ensure the server is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import azure_storage_mcp.server; print('Server module loaded')" || exit 1