# Azure Storage MCP Server

A [Model Context Protocol (MCP)](https://github.com/anthropics/mcp-specification) server that provides read-only access to Azure Storage Account information. This server allows you to inspect storage accounts, network configurations, security settings, and metrics through a standardized protocol.

## Features

- **🔐 Multiple Authentication Methods**: Support for Azure CLI, Managed Identity, Service Principal, and Default Azure Credential
- **📊 Comprehensive Storage Account Information**: Basic properties, security settings, network configuration, blob service properties
- **🌐 Network Rules and Private Endpoints**: Detailed network access rules and private endpoint configurations
- **📈 Metrics and Monitoring**: Storage usage and performance metrics
- **🔒 Security-First Design**: Read-only operations with proper input validation and error handling
- **🏗️ Production-Ready**: Structured logging, comprehensive error handling, and monitoring capabilities

## Tools Available

1. **`list_storage_accounts`** - List all storage accounts in a subscription or resource group
2. **`get_storage_account_details`** - Get detailed information for a specific storage account
3. **`get_network_rules`** - Retrieve network access rules and firewall settings
4. **`get_private_endpoints`** - List private endpoint connections and their status
5. **`get_storage_metrics`** - Fetch basic usage and performance metrics

## Installation

### Prerequisites

- Python 3.10 or higher
- Azure CLI installed and configured (`az login`)
- Appropriate Azure permissions for storage account access

### Using UV (Recommended)

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd azure-storage-mcp

# Install dependencies
uv sync --all-extras

# Run development setup
./scripts/dev.sh
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd azure-storage-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .
```

## Quick Start

### 1. Authentication Setup

The server supports multiple authentication methods:

```bash
# Azure CLI (recommended for development)
az login

# Or set environment variables for service principal
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_AUTH_METHOD="service_principal"
```

### 2. Run the Demo

```bash
# Run the interactive demo
uv run python scripts/demo.py

# Or with a specific subscription
uv run python scripts/demo.py "your-subscription-id"
```

### 3. Start the MCP Server

```bash
# Start the MCP server
uv run azure-storage-mcp

# Or run directly
uv run python -m azure_storage_mcp.server
```

## Using with Claude Desktop on Windows

This section provides step-by-step instructions for configuring the Azure Storage MCP server to work with Claude Desktop on Windows using your personal Azure credentials.

### Prerequisites

- **Claude Desktop for Windows** installed from [Claude.ai](https://claude.ai/download)
- **Azure CLI** installed from [Microsoft Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows)
- **Windows PowerShell** or **Command Prompt**
- **Azure subscription** with storage accounts to inspect
- **Docker Desktop** (optional, for container-based setup)

### Option 1: Native Installation (Recommended)

#### Step 1: Install Prerequisites

```powershell
# Install Azure CLI (if not already installed)
# Download from: https://aka.ms/installazurecliwindows

# Install UV package manager
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install Git (if not already installed)
# Download from: https://git-scm.com/download/win
```

#### Step 2: Clone and Setup the MCP Server

```powershell
# Clone the repository
git clone https://github.com/your-username/azure-storage-mcp.git
cd azure-storage-mcp

# Install dependencies
uv sync --all-extras

# Test installation
uv run python scripts/demo.py --help
```

#### Step 3: Authenticate with Azure

```powershell
# Login to Azure with your personal account
az login

# Verify your login and note your subscription ID
az account show

# Optional: Set a specific subscription as default
az account set --subscription "your-subscription-id"

# Test authentication with the MCP server
uv run python scripts/demo.py
```

#### Step 4: Configure Claude Desktop

Create or edit the Claude Desktop configuration file:

**Location**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "azure-storage": {
      "command": "uv",
      "args": ["run", "azure-storage-mcp"],
      "cwd": "C:\\path\\to\\your\\azure-storage-mcp",
      "env": {
        "AZURE_AUTH_METHOD": "default"
      }
    }
  }
}
```

**Replace** `C:\\path\\to\\your\\azure-storage-mcp` with the actual path where you cloned the repository.

#### Step 5: Restart Claude Desktop

1. Close Claude Desktop completely
2. Restart Claude Desktop
3. Open a new conversation
4. The Azure Storage MCP tools should now be available

### Option 2: Docker/OCI Container Setup

#### Step 1: Install Docker Desktop

1. Download and install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows/)
2. Start Docker Desktop and ensure it's running

#### Step 2: Pull the Pre-built Image

```powershell
# Pull the latest Azure Storage MCP image
docker pull ghcr.io/derek-ashmore/azure-storage-mcp:latest

# Verify the image
docker images | findstr azure-storage-mcp
```

#### Step 3: Authenticate with Azure

```powershell
# Login to Azure with your personal account
az login

# Get your Azure credentials for container use
az account show

# Get service principal details (if you have one)
# Or use the interactive login approach below
```

#### Step 4: Run the Container with Azure Credentials

**Option A: Using Azure CLI Authentication (Recommended)**

```powershell
# Create a wrapper script for container authentication
@'
#!/bin/bash
# Login with device code if needed
if ! az account show > /dev/null 2>&1; then
    echo "Please run 'az login' on your host machine first"
    exit 1
fi

# Run the MCP server
exec azure-storage-mcp "$@"
'@ | Out-File -FilePath azure-mcp-wrapper.sh -Encoding UTF8

# Run container with Azure CLI configuration mounted
docker run -it --rm `
  -v "$env:USERPROFILE\.azure:/root/.azure:ro" `
  -v "$PWD/azure-mcp-wrapper.sh:/usr/local/bin/azure-mcp-wrapper.sh:ro" `
  --entrypoint="/usr/local/bin/azure-mcp-wrapper.sh" `
  ghcr.io/derek-ashmore/azure-storage-mcp:latest
```

**Option B: Using Environment Variables (Service Principal)**

```powershell
# Set your Azure service principal credentials
$env:AZURE_TENANT_ID = "your-tenant-id"
$env:AZURE_CLIENT_ID = "your-client-id"
$env:AZURE_CLIENT_SECRET = "your-client-secret"
$env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"

# Test the container
docker run --rm `
  -e AZURE_TENANT_ID="$env:AZURE_TENANT_ID" `
  -e AZURE_CLIENT_ID="$env:AZURE_CLIENT_ID" `
  -e AZURE_CLIENT_SECRET="$env:AZURE_CLIENT_SECRET" `
  -e AZURE_SUBSCRIPTION_ID="$env:AZURE_SUBSCRIPTION_ID" `
  ghcr.io/derek-ashmore/azure-storage-mcp:latest `
  uv run python scripts/demo.py "$env:AZURE_SUBSCRIPTION_ID"
```

#### Step 5: Configure Claude Desktop for Container

Create the configuration file at `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "azure-storage": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "%USERPROFILE%\\.azure:/root/.azure:ro",
        "-e", "AZURE_AUTH_METHOD=default",
        "ghcr.io/derek-ashmore/azure-storage-mcp:latest"
      ],
      "env": {}
    }
  }
}
```

For service principal authentication, use:

```json
{
  "mcpServers": {
    "azure-storage": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "AZURE_TENANT_ID",
        "-e", "AZURE_CLIENT_ID", 
        "-e", "AZURE_CLIENT_SECRET",
        "-e", "AZURE_SUBSCRIPTION_ID",
        "-e", "AZURE_AUTH_METHOD=service_principal",
        "ghcr.io/derek-ashmore/azure-storage-mcp:latest"
      ],
      "env": {
        "AZURE_TENANT_ID": "your-tenant-id",
        "AZURE_CLIENT_ID": "your-client-id",
        "AZURE_CLIENT_SECRET": "your-client-secret",
        "AZURE_SUBSCRIPTION_ID": "your-subscription-id"
      }
    }
  }
}
```

### Testing the Integration

1. **Restart Claude Desktop** after configuration changes
2. **Open a new conversation** in Claude
3. **Test the integration** with sample queries:

```
Can you list my Azure storage accounts?

Show me the network rules for my storage account named "mystorageaccount" in resource group "my-rg"

What are the current storage metrics for my storage account?
```

### Troubleshooting Windows Setup

#### Common Issues

1. **"uv: command not found"**
   ```powershell
   # Restart PowerShell after installing UV
   # Or install manually:
   Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -OutFile install.ps1
   powershell -ExecutionPolicy ByPass -File install.ps1
   ```

2. **"Azure CLI not found"**
   ```powershell
   # Install Azure CLI
   Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile AzureCLI.msi
   Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
   ```

3. **"Claude can't find the MCP server"**
   - Verify the path in `claude_desktop_config.json` uses double backslashes (`\\`)
   - Ensure the path exists and contains the MCP server files
   - Check that UV and Python are in your PATH

4. **"Authentication failed in container"**
   ```powershell
   # Verify Azure login
   az account show
   
   # Ensure Azure config directory is mounted correctly
   # Path should be: %USERPROFILE%\.azure:/root/.azure:ro
   ```

5. **"Permission denied" in Docker**
   ```powershell
   # Ensure Docker Desktop is running
   # Check Docker daemon is accessible
   docker version
   ```

### Security Recommendations

1. **Use Azure CLI authentication** for personal use (most secure)
2. **Limit service principal permissions** to only required storage accounts
3. **Store credentials securely** - avoid hardcoding in configuration files
4. **Regular credential rotation** for service principals
5. **Monitor access logs** in Azure for unusual activity

### Performance Tips

1. **Native installation** is faster than container for regular use
2. **Container approach** is better for isolated/testing environments
3. **Cache Docker images** locally to avoid repeated downloads
4. **Use specific subscription IDs** in queries to reduce API calls

## Usage Examples

### List Storage Accounts

```json
{
  "name": "list_storage_accounts",
  "arguments": {
    "subscription_id": "12345678-1234-1234-1234-123456789012",
    "resource_group": "my-resource-group",
    "include_deleted": false
  }
}
```

### Get Storage Account Details

```json
{
  "name": "get_storage_account_details",
  "arguments": {
    "subscription_id": "12345678-1234-1234-1234-123456789012",
    "resource_group": "my-resource-group",
    "account_name": "mystorageaccount",
    "include_keys": false
  }
}
```

### Get Network Rules

```json
{
  "name": "get_network_rules",
  "arguments": {
    "subscription_id": "12345678-1234-1234-1234-123456789012",
    "resource_group": "my-resource-group",
    "account_name": "mystorageaccount"
  }
}
```

### Get Storage Metrics

```json
{
  "name": "get_storage_metrics",
  "arguments": {
    "subscription_id": "12345678-1234-1234-1234-123456789012",
    "resource_group": "my-resource-group",
    "account_name": "mystorageaccount",
    "time_range": "24h",
    "metrics": ["UsedCapacity", "Transactions"],
    "aggregation_type": "Average"
  }
}
```

## Configuration

### Authentication Methods

Set the `AZURE_AUTH_METHOD` environment variable to choose authentication:

- `default` - DefaultAzureCredential (tries multiple methods)
- `cli` - Azure CLI authentication
- `managed_identity` - Managed Identity
- `service_principal` - Service Principal with environment variables

### Environment Variables

- `AZURE_AUTH_METHOD` - Authentication method (default: "default")
- `AZURE_TENANT_ID` - Tenant ID for service principal auth
- `AZURE_CLIENT_ID` - Client ID for service principal auth
- `AZURE_CLIENT_SECRET` - Client secret for service principal auth

## Development

### Project Structure

```
azure-storage-mcp/
├── src/azure_storage_mcp/
│   ├── __init__.py
│   ├── server.py              # Main MCP server
│   ├── auth/                  # Authentication handling
│   ├── models/                # Pydantic data models
│   ├── tools/                 # MCP tool implementations
│   └── utils/                 # Utilities and exceptions
├── tests/                     # Test suite
├── scripts/                   # Development scripts
└── pyproject.toml             # Project configuration
```

### Development Setup

```bash
# Clone and setup development environment
git clone <repository-url>
cd azure-storage-mcp
./scripts/dev.sh
```

### Running Tests

```bash
# Run all tests with coverage
./scripts/test.sh

# Or run specific tests
uv run pytest tests/test_server.py -v

# Run with coverage report
uv run pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
uv run black src tests

# Lint code
uv run ruff check src tests

# Type checking
uv run mypy src
```

## Required Azure Permissions

The service principal or user needs the following permissions:

- `Microsoft.Storage/storageAccounts/read`
- `Microsoft.Storage/storageAccounts/listKeys/action` (optional, for `include_keys`)
- `Microsoft.Storage/storageAccounts/blobServices/read`
- `Microsoft.Storage/storageAccounts/privateEndpointConnections/read`
- `Microsoft.Insights/metrics/read` (for metrics)
- `Microsoft.Insights/metricDefinitions/read` (for metrics)

## Response Format

All tools return structured JSON responses with:

- **Data**: The requested information in a structured format
- **Metadata**: Request correlation ID, execution time, timestamps
- **Summary**: Human-readable summary of the results

Example response structure:

```json
{
  "storage_accounts": [...],
  "total_count": 3,
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "correlation_id": "12345678-1234-1234-1234-123456789012",
    "execution_time_ms": 1250
  },
  "summary": "Found 3 storage accounts in subscription. Distribution by region: eastus: 2, westus: 1"
}
```

## Error Handling

The server provides comprehensive error handling with specific error types:

- **AuthenticationError**: Issues with Azure authentication
- **PermissionError**: Insufficient permissions for the requested operation
- **ValidationError**: Invalid input parameters
- **AzureAPIError**: Azure API-related errors
- **AzureStorageMCPError**: General server errors

## Logging

The server uses structured logging with JSON format for easy parsing:

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "tool_name": "list_storage_accounts",
  "parameters": {...},
  "success": true,
  "execution_time_ms": 1250
}
```

## Security Considerations

- **Read-Only Operations**: All operations are read-only and non-destructive
- **Input Validation**: All inputs are validated using Pydantic models
- **Credential Security**: Credentials are never logged or exposed
- **Least Privilege**: Only request necessary permissions

## CI/CD Workflows

This project includes automated testing workflows that validate the MCP server functionality across multiple environments and deployment methods.

### Available Workflows

1. **Test MCP Server - Linux** (`.github/workflows/test-linux.yml`)
   - Runs on Ubuntu latest
   - Tests the demo.py script with Azure authentication
   - Triggers on push, pull request, and manual dispatch

2. **Test MCP Server - Windows** (`.github/workflows/test-windows.yml`)
   - Runs on Windows latest  
   - Tests the demo.py script with Azure authentication
   - Triggers on push, pull request, and manual dispatch

3. **Build and Publish OCI Image** (`.github/workflows/build-container.yml`)
   - Builds OCI container image using Podman
   - Tests containerized MCP server with Azure authentication
   - Publishes to GitHub Container Registry (ghcr.io)
   - Only publishes on main branch (skips PRs)
   - Triggers on push, pull request, and manual dispatch

### Required Secrets

Both workflows require the following GitHub secrets to be configured:

- `AZURE_TENANT_ID` - Your Azure tenant ID
- `AZURE_CLIENT_ID` - Service principal client ID
- `AZURE_CLIENT_SECRET` - Service principal client secret
- `AZURE_SUBSCRIPTION_ID` - Target Azure subscription ID

### Workflow Features

- **Cross-platform testing**: Ensures compatibility on both Linux and Windows
- **Service principal authentication**: Uses Azure service principal for CI/CD
- **Error capture**: Automatically uploads failure logs as artifacts
- **Demo validation**: Runs the complete demo.py script to validate all MCP tools

### Manual Trigger

You can manually trigger the workflows from the GitHub Actions tab using workflow_dispatch.

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Check Azure CLI login
   az account show
   
   # Re-login if needed
   az login
   ```

2. **Permission Errors**
   ```bash
   # Check your permissions
   az role assignment list --assignee $(az account show --query user.name -o tsv)
   ```

3. **Subscription Not Found**
   ```bash
   # List available subscriptions
   az account list --query "[].{Name:name, Id:id}" --output table
   ```

### Debug Mode

Enable debug logging by setting:

```bash
export AZURE_STORAGE_MCP_DEBUG=true
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the [troubleshooting section](#troubleshooting)
2. Review the [Azure Storage documentation](https://docs.microsoft.com/en-us/azure/storage/)
3. Open an issue in the repository

## Acknowledgments

- Built using the [Model Context Protocol (MCP)](https://github.com/anthropics/mcp-specification)
- Powered by [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)
- Package management with [UV](https://astral.sh/uv)