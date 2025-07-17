Create a Python MCP (Model Context Protocol) server that provides read-only access to Azure Storage Account information. The server should:

## Core Functionality
- Connect to Azure using the Azure SDK for Python (azure-storage-blob, azure-mgmt-storage, azure-identity)
- Provide tools to list and inspect storage accounts across subscriptions
- Return comprehensive storage account details including configuration, security settings, and network topology

## Required Tools
1. **list_storage_accounts** - List all storage accounts in a subscription or resource group
2. **get_storage_account_details** - Get detailed information for a specific storage account
3. **get_network_rules** - Retrieve network access rules and firewall settings
4. **get_private_endpoints** - List private endpoint connections and their status
5. **get_storage_metrics** - Fetch basic usage and performance metrics

## Data to Include
- Basic properties (name, location, resource group, SKU, kind, access tier)
- Security settings (encryption, secure transfer, public access, shared key access)
- Network configuration (virtual network rules, IP rules, default action)
- Private endpoint details (connection state, network interface info, DNS zones)
- Blob service properties (versioning, soft delete, change feed)
- Access policies and RBAC assignments
- Diagnostic and monitoring settings

## Authentication
- Support Azure CLI authentication, managed identity, and service principal
- Handle multi-tenant scenarios
- Implement proper error handling for authentication failures

## Output Format
- Return structured JSON data for easy parsing
- Include metadata like last updated timestamps
- Provide human-readable summaries alongside raw data

The server should be production-ready with proper logging, error handling, and follow MCP protocol specifications for tool definitions and responses.