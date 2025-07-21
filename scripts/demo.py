#!/usr/bin/env python3
"""
Demo script for Azure Storage MCP server.
Shows how to use the MCP tools programmatically.
"""

import asyncio
import json
import sys
import traceback
from typing import Dict, Any

from azure_storage_mcp.auth import AzureAuthManager
from azure_storage_mcp.tools import StorageAccountsTools, NetworkRulesTools, MetricsTools
from azure_storage_mcp.models import (
    ListStorageAccountsRequest,
    GetStorageAccountDetailsRequest,
    GetNetworkRulesRequest,
    GetPrivateEndpointsRequest,
    GetStorageMetricsRequest,
)


def pretty_print(title: str, data: Dict[str, Any]) -> None:
    """Pretty print JSON data with a title."""
    print(f"\n{'='*60}")
    print(f"[INFO] {title}")
    print(f"{'='*60}")
    print(json.dumps(data, indent=2, default=str))


def get_auth_method() -> str:
    """Determine the best auth method based on environment."""
    import os
    # If service principal env vars are set, use them
    if all([
        os.environ.get("AZURE_TENANT_ID"),
        os.environ.get("AZURE_CLIENT_ID"), 
        os.environ.get("AZURE_CLIENT_SECRET")
    ]):
        return "service_principal"
    # Otherwise use default (which includes CLI)
    return "default"


async def demo_list_storage_accounts(subscription_id: str) -> None:
    """Demo listing storage accounts."""
    auth_method = get_auth_method()
    auth_manager = AzureAuthManager(auth_method)
    tools = StorageAccountsTools(auth_manager)
    
    request = ListStorageAccountsRequest(subscription_id=subscription_id)
    result = await tools.list_storage_accounts(request)
    
    pretty_print("Storage Accounts List", result.dict())


async def demo_storage_account_details(subscription_id: str, resource_group: str, account_name: str) -> bool:
    """Demo getting storage account details."""
    auth_method = get_auth_method()
    auth_manager = AzureAuthManager(auth_method)
    tools = StorageAccountsTools(auth_manager)
    
    request = GetStorageAccountDetailsRequest(
        subscription_id=subscription_id,
        resource_group=resource_group,
        account_name=account_name
    )
    
    try:
        result = await tools.get_storage_account_details(request)
        pretty_print(f"Storage Account Details - {account_name}", result.dict())
        return True  # Indicate success
    except Exception as e:
        print(f"[ERROR] Error getting storage account details: {e}")
        print(f"[DEBUG] Stack trace:\n{traceback.format_exc()}")
        return False  # Indicate failure


async def demo_network_rules(subscription_id: str, resource_group: str, account_name: str) -> bool:
    """Demo getting network rules."""
    auth_method = get_auth_method()
    auth_manager = AzureAuthManager(auth_method)
    tools = NetworkRulesTools(auth_manager)
    
    request = GetNetworkRulesRequest(
        subscription_id=subscription_id,
        resource_group=resource_group,
        account_name=account_name
    )
    
    try:
        result = await tools.get_network_rules(request)
        pretty_print(f"Network Rules - {account_name}", result.dict())
        return True  # Indicate success
    except Exception as e:
        print(f"[ERROR] Error getting network rules: {e}")
        print(f"[DEBUG] Stack trace:\n{traceback.format_exc()}")
        return False  # Indicate failure


async def demo_private_endpoints(subscription_id: str, resource_group: str, account_name: str) -> bool:
    """Demo getting private endpoints."""
    auth_method = get_auth_method()
    auth_manager = AzureAuthManager(auth_method)
    tools = NetworkRulesTools(auth_manager)
    
    request = GetPrivateEndpointsRequest(
        subscription_id=subscription_id,
        resource_group=resource_group,
        account_name=account_name
    )
    
    try:
        result = await tools.get_private_endpoints(request)
        pretty_print(f"Private Endpoints - {account_name}", result.dict())
        return True  # Indicate success
    except Exception as e:
        print(f"[ERROR] Error getting private endpoints: {e}")
        print(f"[DEBUG] Stack trace:\n{traceback.format_exc()}")
        return False  # Indicate failure


async def demo_metrics(subscription_id: str, resource_group: str, account_name: str) -> bool:
    """Demo getting storage metrics."""
    auth_method = get_auth_method()
    auth_manager = AzureAuthManager(auth_method)
    tools = MetricsTools(auth_manager)
    
    request = GetStorageMetricsRequest(
        subscription_id=subscription_id,
        resource_group=resource_group,
        account_name=account_name,
        time_range="24h",
        metrics=["UsedCapacity", "Transactions"]
    )
    
    try:
        result = await tools.get_storage_metrics(request)
        pretty_print(f"Storage Metrics - {account_name}", result.dict())
        return True  # Indicate success
    except Exception as e:
        print(f"[ERROR] Error getting storage metrics: {e}")
        print(f"[DEBUG] Stack trace:\n{traceback.format_exc()}")
        return False  # Indicate failure


async def main() -> None:
    """Main demo function."""
    print("[DEMO] Azure Storage MCP Server Demo")
    print("=" * 60)
    
    # Test authentication
    print("[AUTH] Testing authentication...")
    auth_method = get_auth_method()
    print(f"[AUTH] Using authentication method: {auth_method}")
    auth_manager = AzureAuthManager(auth_method)
    
    try:
        is_authenticated = await auth_manager.test_authentication()
        if not is_authenticated:
            print("[ERROR] Authentication failed. Please run 'az login' first.")
            sys.exit(1)
        print("[SUCCESS] Authentication successful!")
    except Exception as e:
        print(f"[ERROR] Authentication error: {e}")
        print(f"[DEBUG] Stack trace:\n{traceback.format_exc()}")
        sys.exit(1)
    
    # Get subscription ID from command line or use default
    if len(sys.argv) > 1:
        subscription_id = sys.argv[1]
    else:
        # Try to get from Azure CLI
        try:
            import subprocess
            result = subprocess.run(['az', 'account', 'show', '--query', 'id', '-o', 'tsv'], 
                                  capture_output=True, text=True)
            subscription_id = result.stdout.strip()
            if not subscription_id:
                print("[ERROR] Could not get subscription ID. Please provide it as an argument.")
                print("Usage: python demo.py <subscription_id>")
                sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Error getting subscription ID: {e}")
            print("Usage: python demo.py <subscription_id>")
            sys.exit(1)
    
    print(f"[INFO] Using subscription: {subscription_id}")
    
    # Demo listing storage accounts
    await demo_list_storage_accounts(subscription_id)
    
    # Get first storage account for detailed demos
    auth_method = get_auth_method()
    auth_manager = AzureAuthManager(auth_method)
    tools = StorageAccountsTools(auth_manager)
    
    try:
        request = ListStorageAccountsRequest(subscription_id=subscription_id)
        result = await tools.list_storage_accounts(request)
        
        if result.storage_accounts:
            first_account = result.storage_accounts[0]
            print(f"\n[DEMO] Running detailed demos for: {first_account.name}")
            
            # Track errors
            errors = []
            
            # Demo detailed account information
            if not await demo_storage_account_details(
                subscription_id, 
                first_account.resource_group, 
                first_account.name
            ):
                errors.append("storage account details")
            
            # Demo network rules
            if not await demo_network_rules(
                subscription_id, 
                first_account.resource_group, 
                first_account.name
            ):
                errors.append("network rules")
            
            # Demo private endpoints
            if not await demo_private_endpoints(
                subscription_id, 
                first_account.resource_group, 
                first_account.name
            ):
                errors.append("private endpoints")
            
            # Demo metrics (may require additional permissions)
            if not await demo_metrics(
                subscription_id, 
                first_account.resource_group, 
                first_account.name
            ):
                errors.append("storage metrics")
            
            # Check for errors
            if errors:
                print(f"\n[ERROR] Demo failed for: {', '.join(errors)}")
                sys.exit(1)
        else:
            print("[INFO] No storage accounts found in subscription.")
            
    except Exception as e:
        print(f"[ERROR] Error during demo: {e}")
        print(f"[DEBUG] Stack trace:\n{traceback.format_exc()}")
        sys.exit(1)
    
    print("\n[SUCCESS] Demo completed!")
    print("[INFO] To run the MCP server: uv run azure-storage-mcp")


if __name__ == "__main__":
    asyncio.run(main())