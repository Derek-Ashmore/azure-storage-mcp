"""Tests for the main MCP server."""

import pytest
from unittest.mock import Mock, patch
import asyncio

from azure_storage_mcp.server import AzureStorageMCPServer
from azure_storage_mcp.models import ListStorageAccountsRequest


@pytest.mark.asyncio
async def test_server_initialization():
    """Test server initialization."""
    with patch.dict('os.environ', {'AZURE_AUTH_METHOD': 'default'}):
        server = AzureStorageMCPServer()
        assert server.server.name == "azure-storage-mcp"
        assert server.auth_manager is not None
        assert server.storage_tools is not None
        assert server.network_tools is not None
        assert server.metrics_tools is not None


@pytest.mark.asyncio
async def test_list_tools():
    """Test list_tools handler."""
    with patch.dict('os.environ', {'AZURE_AUTH_METHOD': 'default'}):
        server = AzureStorageMCPServer()
        
        # Get the list_tools handler
        handler = None
        for registered_handler in server.server._tools_handlers:
            if hasattr(registered_handler, '__name__') and registered_handler.__name__ == 'handle_list_tools':
                handler = registered_handler
                break
        
        assert handler is not None
        
        # Call the handler
        tools = await handler()
        
        # Check that all expected tools are present
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "list_storage_accounts",
            "get_storage_account_details", 
            "get_network_rules",
            "get_private_endpoints",
            "get_storage_metrics"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
        
        # Check that each tool has required properties
        for tool in tools:
            assert tool.name
            assert tool.description
            assert tool.inputSchema
            assert "properties" in tool.inputSchema
            assert "required" in tool.inputSchema


@pytest.mark.asyncio
async def test_call_tool_validation_error():
    """Test call_tool handler with validation error."""
    with patch.dict('os.environ', {'AZURE_AUTH_METHOD': 'default'}):
        server = AzureStorageMCPServer()
        
        # Get the call_tool handler
        handler = None
        for registered_handler in server.server._tools_handlers:
            if hasattr(registered_handler, '__name__') and registered_handler.__name__ == 'handle_call_tool':
                handler = registered_handler
                break
        
        assert handler is not None
        
        # Call with invalid arguments (missing required subscription_id)
        result = await handler("list_storage_accounts", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "ERROR: Validation error" in result[0].text


@pytest.mark.asyncio
async def test_call_tool_unknown_tool():
    """Test call_tool handler with unknown tool."""
    with patch.dict('os.environ', {'AZURE_AUTH_METHOD': 'default'}):
        server = AzureStorageMCPServer()
        
        # Get the call_tool handler
        handler = None
        for registered_handler in server.server._tools_handlers:
            if hasattr(registered_handler, '__name__') and registered_handler.__name__ == 'handle_call_tool':
                handler = registered_handler
                break
        
        assert handler is not None
        
        # Call with unknown tool
        result = await handler("unknown_tool", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "ERROR: Azure Storage MCP error: Unknown tool: unknown_tool" in result[0].text