"""Main MCP server for Azure Storage Account access."""

import asyncio
import os
import sys
from typing import Any, Dict, List, Optional, Sequence

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from pydantic import ValidationError

from .auth import AzureAuthManager
from .models import (
    ListStorageAccountsRequest,
    GetStorageAccountDetailsRequest,
    GetNetworkRulesRequest,
    GetPrivateEndpointsRequest,
    GetStorageMetricsRequest,
)
from .tools import StorageAccountsTools, NetworkRulesTools, MetricsTools
from .utils import StructuredLogger, AzureStorageMCPError


class AzureStorageMCPServer:
    """Azure Storage MCP Server implementation."""
    
    def __init__(self) -> None:
        self.server = Server("azure-storage-mcp")
        self.logger = StructuredLogger(__name__)
        
        # Initialize authentication
        auth_method = os.environ.get("AZURE_AUTH_METHOD", "default")
        self.auth_manager = AzureAuthManager(auth_method)
        
        # Initialize tools
        self.storage_tools = StorageAccountsTools(self.auth_manager)
        self.network_tools = NetworkRulesTools(self.auth_manager)
        self.metrics_tools = MetricsTools(self.auth_manager)
        
        # Setup handlers
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Setup MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="list_storage_accounts",
                    description="List all storage accounts in a subscription or resource group",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "subscription_id": {
                                "type": "string",
                                "description": "Azure subscription ID"
                            },
                            "resource_group": {
                                "type": "string",
                                "description": "Resource group name (optional)"
                            },
                            "include_deleted": {
                                "type": "boolean",
                                "description": "Include deleted storage accounts",
                                "default": False
                            }
                        },
                        "required": ["subscription_id"]
                    }
                ),
                types.Tool(
                    name="get_storage_account_details",
                    description="Get detailed information for a specific storage account",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "subscription_id": {
                                "type": "string",
                                "description": "Azure subscription ID"
                            },
                            "resource_group": {
                                "type": "string",
                                "description": "Resource group name"
                            },
                            "account_name": {
                                "type": "string",
                                "description": "Storage account name"
                            },
                            "include_keys": {
                                "type": "boolean",
                                "description": "Include access keys (requires permissions)",
                                "default": False
                            }
                        },
                        "required": ["subscription_id", "resource_group", "account_name"]
                    }
                ),
                types.Tool(
                    name="get_network_rules",
                    description="Retrieve network access rules and firewall settings",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "subscription_id": {
                                "type": "string",
                                "description": "Azure subscription ID"
                            },
                            "resource_group": {
                                "type": "string",
                                "description": "Resource group name"
                            },
                            "account_name": {
                                "type": "string",
                                "description": "Storage account name"
                            }
                        },
                        "required": ["subscription_id", "resource_group", "account_name"]
                    }
                ),
                types.Tool(
                    name="get_private_endpoints",
                    description="List private endpoint connections and their status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "subscription_id": {
                                "type": "string",
                                "description": "Azure subscription ID"
                            },
                            "resource_group": {
                                "type": "string",
                                "description": "Resource group name"
                            },
                            "account_name": {
                                "type": "string",
                                "description": "Storage account name"
                            }
                        },
                        "required": ["subscription_id", "resource_group", "account_name"]
                    }
                ),
                types.Tool(
                    name="get_storage_metrics",
                    description="Fetch basic usage and performance metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "subscription_id": {
                                "type": "string",
                                "description": "Azure subscription ID"
                            },
                            "resource_group": {
                                "type": "string",
                                "description": "Resource group name"
                            },
                            "account_name": {
                                "type": "string",
                                "description": "Storage account name"
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Time range (1h, 24h, 7d, 30d)",
                                "default": "1h"
                            },
                            "metrics": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Metrics to retrieve",
                                "default": ["UsedCapacity", "Transactions"]
                            },
                            "aggregation_type": {
                                "type": "string",
                                "description": "Aggregation type",
                                "default": "Average"
                            },
                            "interval": {
                                "type": "string",
                                "description": "Time interval for data points",
                                "default": "PT1H"
                            }
                        },
                        "required": ["subscription_id", "resource_group", "account_name"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, 
            arguments: Dict[str, Any] | None
        ) -> List[types.TextContent]:
            """Handle tool calls."""
            if arguments is None:
                arguments = {}
            
            try:
                if name == "list_storage_accounts":
                    request = ListStorageAccountsRequest(**arguments)
                    result = await self.storage_tools.list_storage_accounts(request)
                    return [
                        types.TextContent(
                            type="text",
                            text=result.json(indent=2)
                        )
                    ]
                
                elif name == "get_storage_account_details":
                    request = GetStorageAccountDetailsRequest(**arguments)
                    result = await self.storage_tools.get_storage_account_details(request)
                    return [
                        types.TextContent(
                            type="text",
                            text=result.json(indent=2)
                        )
                    ]
                
                elif name == "get_network_rules":
                    request = GetNetworkRulesRequest(**arguments)
                    result = await self.network_tools.get_network_rules(request)
                    return [
                        types.TextContent(
                            type="text",
                            text=result.json(indent=2)
                        )
                    ]
                
                elif name == "get_private_endpoints":
                    request = GetPrivateEndpointsRequest(**arguments)
                    result = await self.network_tools.get_private_endpoints(request)
                    return [
                        types.TextContent(
                            type="text",
                            text=result.json(indent=2)
                        )
                    ]
                
                elif name == "get_storage_metrics":
                    request = GetStorageMetricsRequest(**arguments)
                    result = await self.metrics_tools.get_storage_metrics(request)
                    return [
                        types.TextContent(
                            type="text",
                            text=result.json(indent=2)
                        )
                    ]
                
                else:
                    raise AzureStorageMCPError(f"Unknown tool: {name}")
                    
            except ValidationError as e:
                error_message = f"Validation error: {str(e)}"
                self.logger.log_error(e, {"tool": name, "arguments": arguments})
                return [
                    types.TextContent(
                        type="text",
                        text=f"ERROR: {error_message}"
                    )
                ]
            
            except AzureStorageMCPError as e:
                error_message = f"Azure Storage MCP error: {str(e)}"
                self.logger.log_error(e, {"tool": name, "arguments": arguments})
                return [
                    types.TextContent(
                        type="text",
                        text=f"ERROR: {error_message}"
                    )
                ]
            
            except Exception as e:
                error_message = f"Unexpected error: {str(e)}"
                self.logger.log_error(e, {"tool": name, "arguments": arguments})
                return [
                    types.TextContent(
                        type="text",
                        text=f"ERROR: {error_message}"
                    )
                ]
    
    async def run(self) -> None:
        """Run the MCP server."""
        # Test authentication on startup
        if not await self.auth_manager.test_authentication():
            self.logger.logger.error("Authentication test failed. Please check your Azure credentials.")
            sys.exit(1)
        
        self.logger.logger.info("Azure Storage MCP server starting...")
        
        # Setup stdio transport
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream,
                InitializationOptions(
                    server_name="azure-storage-mcp",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )


async def main() -> None:
    """Main entry point."""
    server = AzureStorageMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())