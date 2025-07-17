# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python MCP (Model Context Protocol) server that provides read-only access to Azure Storage Account information. The project is in initial planning phase with specifications defined in INITIAL.md.

## Key Project Requirements

Based on INITIAL.md, this MCP server should:

### Core Tools to Implement
1. **list_storage_accounts** - List all storage accounts in a subscription or resource group
2. **get_storage_account_details** - Get detailed information for a specific storage account  
3. **get_network_rules** - Retrieve network access rules and firewall settings
4. **get_private_endpoints** - List private endpoint connections and their status
5. **get_storage_metrics** - Fetch basic usage and performance metrics

### Required Dependencies
- azure-storage-blob
- azure-mgmt-storage  
- azure-identity
- MCP protocol libraries

### Authentication Support
- Azure CLI authentication
- Managed identity
- Service principal
- Multi-tenant scenarios

### Data Structure Requirements
- Return structured JSON data
- Include metadata like timestamps
- Provide human-readable summaries alongside raw data
- Cover: basic properties, security settings, network configuration, private endpoints, blob service properties, access policies, diagnostic settings

## Development Setup

Since this is a new project, typical Python MCP development setup would include:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (once requirements.txt is created)
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Architecture Notes

The server should follow MCP protocol specifications for:
- Tool definitions and responses
- Proper error handling for authentication failures
- Production-ready logging
- Structured JSON responses with metadata

## Security Considerations

This is a read-only server focused on Azure Storage inspection. All operations should be non-destructive and follow Azure SDK authentication patterns.