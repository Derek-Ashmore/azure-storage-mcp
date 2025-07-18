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