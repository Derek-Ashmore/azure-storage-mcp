"""MCP tools for Azure Storage network rules operations."""

import uuid
from datetime import datetime
from typing import Optional

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.mgmt.storage import StorageManagementClient

from ..auth import AzureAuthManager, SecurityValidator
from ..models import (
    GetNetworkRulesRequest,
    NetworkRules,
    GetPrivateEndpointsRequest,
    GetPrivateEndpointsResponse,
    PrivateEndpointConnection,
    NetworkInterfaceInfo,
    ResponseMetadata,
    IpRule,
    VirtualNetworkRule,
    ResourceAccessRule,
)
from ..utils import (
    AzureStorageMCPError,
    AuthenticationError,
    PermissionError,
    ValidationError,
    AzureAPIError,
    StructuredLogger,
)


class NetworkRulesTools:
    """Tools for Azure Storage network rules operations."""
    
    def __init__(self, auth_manager: AzureAuthManager) -> None:
        self.auth_manager = auth_manager
        self.logger = StructuredLogger(__name__)
        self._storage_client: Optional[StorageManagementClient] = None
    
    async def _get_storage_client(self, subscription_id: str) -> StorageManagementClient:
        """Get or create Azure Storage Management client."""
        if self._storage_client is None:
            credential = await self.auth_manager.get_credential()
            self._storage_client = StorageManagementClient(
                credential=credential,
                subscription_id=subscription_id
            )
        return self._storage_client
    
    async def get_network_rules(self, request: GetNetworkRulesRequest) -> NetworkRules:
        """Get network access rules for a storage account."""
        start_time = datetime.utcnow()
        correlation_id = str(uuid.uuid4())
        
        try:
            # Validate inputs
            SecurityValidator.validate_subscription_id(request.subscription_id)
            SecurityValidator.validate_resource_group(request.resource_group)
            SecurityValidator.validate_storage_account_name(request.account_name)
            
            # Get Azure client
            client = await self._get_storage_client(request.subscription_id)
            
            # Get storage account properties to access network rules
            account_props = client.storage_accounts.get_properties(
                request.resource_group,
                request.account_name
            )
            
            # Get network rules from account properties
            network_rules = account_props.network_rule_set
            
            # Create response
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            metadata = ResponseMetadata(
                correlation_id=correlation_id,
                execution_time_ms=execution_time
            )
            
            response = NetworkRules(
                default_action=network_rules.default_action.value if hasattr(network_rules.default_action, 'value') else str(network_rules.default_action),
                ip_rules=[
                    IpRule(
                        ip_address_or_range=rule.ip_address_or_range,
                        action=rule.action.value if hasattr(rule.action, 'value') else str(rule.action)
                    )
                    for rule in (network_rules.ip_rules or [])
                ],
                virtual_network_rules=[
                    VirtualNetworkRule(
                        subnet_id=rule.virtual_network_resource_id,
                        action=rule.action.value if hasattr(rule.action, 'value') else str(rule.action),
                        state=rule.state.value if hasattr(rule.state, 'value') else str(rule.state)
                    )
                    for rule in (network_rules.virtual_network_rules or [])
                ],
                resource_access_rules=[
                    ResourceAccessRule(
                        tenant_id=rule.tenant_id,
                        resource_id=rule.resource_id
                    )
                    for rule in (network_rules.resource_access_rules or [])
                ],
                bypass=network_rules.bypass.value if network_rules.bypass and hasattr(network_rules.bypass, 'value') else str(network_rules.bypass) if network_rules.bypass else "None",
                metadata=metadata,
                summary=self._create_network_rules_summary(network_rules, request.account_name)
            )
            
            self.logger.log_tool_execution(
                "get_network_rules",
                request.dict(),
                response,
                success=True
            )
            
            return response
            
        except ValidationError as e:
            self.logger.log_error(e, {"correlation_id": correlation_id})
            raise
        except ClientAuthenticationError as e:
            error = AuthenticationError(f"Authentication failed: {str(e)}", "azure_auth")
            self.logger.log_error(error, {"correlation_id": correlation_id})
            raise error
        except HttpResponseError as e:
            if e.status_code == 403:
                error = PermissionError(
                    f"Insufficient permissions to access network rules: {str(e)}",
                    "Microsoft.Storage/storageAccounts/read"
                )
            elif e.status_code == 404:
                error = AzureAPIError(f"Storage account not found: {request.account_name}", 404)
            else:
                error = AzureAPIError(f"Azure API error: {str(e)}", e.status_code)
            self.logger.log_error(error, {"correlation_id": correlation_id})
            raise error
        except Exception as e:
            error = AzureStorageMCPError(f"Unexpected error: {str(e)}")
            self.logger.log_error(error, {"correlation_id": correlation_id})
            raise error
    
    async def get_private_endpoints(
        self, 
        request: GetPrivateEndpointsRequest
    ) -> GetPrivateEndpointsResponse:
        """Get private endpoint connections for a storage account."""
        start_time = datetime.utcnow()
        correlation_id = str(uuid.uuid4())
        
        try:
            # Validate inputs
            SecurityValidator.validate_subscription_id(request.subscription_id)
            SecurityValidator.validate_resource_group(request.resource_group)
            SecurityValidator.validate_storage_account_name(request.account_name)
            
            # Get Azure client
            client = await self._get_storage_client(request.subscription_id)
            
            # Get private endpoint connections
            private_endpoints = []
            try:
                connections = client.private_endpoint_connections.list(
                    request.resource_group,
                    request.account_name
                )
                
                for connection in connections:
                    # Extract network interface info
                    network_interface_info = NetworkInterfaceInfo(
                        id=connection.private_endpoint.id if connection.private_endpoint else "",
                        name=connection.name,
                        private_ip_address="",  # Would need additional API call to get
                        subnet_id=connection.private_endpoint.subnet.id if connection.private_endpoint and connection.private_endpoint.subnet else "",
                        is_primary=True  # Would need additional logic to determine
                    )
                    
                    private_endpoint = PrivateEndpointConnection(
                        name=connection.name,
                        private_endpoint_id=connection.private_endpoint.id if connection.private_endpoint else "",
                        connection_state=connection.private_link_service_connection_state.status,
                        provisioning_state=connection.provisioning_state.value if hasattr(connection.provisioning_state, 'value') else str(connection.provisioning_state),
                        network_interface_info=network_interface_info,
                        dns_zones=[],  # Would need additional API call to populate
                        actions_required=connection.private_link_service_connection_state.actions_required.split(",") if connection.private_link_service_connection_state.actions_required else [],
                        description=connection.private_link_service_connection_state.description or ""
                    )
                    private_endpoints.append(private_endpoint)
                    
            except HttpResponseError as e:
                if e.status_code == 404:
                    # No private endpoints found
                    pass
                else:
                    raise
            
            # Create response
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            metadata = ResponseMetadata(
                correlation_id=correlation_id,
                execution_time_ms=execution_time
            )
            
            response = GetPrivateEndpointsResponse(
                private_endpoints=private_endpoints,
                total_count=len(private_endpoints),
                metadata=metadata,
                summary=self._create_private_endpoints_summary(private_endpoints, request.account_name)
            )
            
            self.logger.log_tool_execution(
                "get_private_endpoints",
                request.dict(),
                response,
                success=True
            )
            
            return response
            
        except ValidationError as e:
            self.logger.log_error(e, {"correlation_id": correlation_id})
            raise
        except ClientAuthenticationError as e:
            error = AuthenticationError(f"Authentication failed: {str(e)}", "azure_auth")
            self.logger.log_error(error, {"correlation_id": correlation_id})
            raise error
        except HttpResponseError as e:
            if e.status_code == 403:
                error = PermissionError(
                    f"Insufficient permissions to access private endpoints: {str(e)}",
                    "Microsoft.Storage/storageAccounts/privateEndpointConnections/read"
                )
            elif e.status_code == 404:
                error = AzureAPIError(f"Storage account not found: {request.account_name}", 404)
            else:
                error = AzureAPIError(f"Azure API error: {str(e)}", e.status_code)
            self.logger.log_error(error, {"correlation_id": correlation_id})
            raise error
        except Exception as e:
            error = AzureStorageMCPError(f"Unexpected error: {str(e)}")
            self.logger.log_error(error, {"correlation_id": correlation_id})
            raise error
    
    def _create_network_rules_summary(self, network_rules, account_name: str) -> str:
        """Create human-readable summary for network rules."""
        default_action = network_rules.default_action.value if hasattr(network_rules.default_action, 'value') else str(network_rules.default_action)
        
        ip_rule_count = len(network_rules.ip_rules or [])
        vnet_rule_count = len(network_rules.virtual_network_rules or [])
        resource_rule_count = len(network_rules.resource_access_rules or [])
        
        bypass_services = network_rules.bypass.value if network_rules.bypass and hasattr(network_rules.bypass, 'value') else str(network_rules.bypass) if network_rules.bypass else "None"
        
        rules_summary = []
        if ip_rule_count > 0:
            rules_summary.append(f"{ip_rule_count} IP rule{'s' if ip_rule_count != 1 else ''}")
        if vnet_rule_count > 0:
            rules_summary.append(f"{vnet_rule_count} VNet rule{'s' if vnet_rule_count != 1 else ''}")
        if resource_rule_count > 0:
            rules_summary.append(f"{resource_rule_count} resource rule{'s' if resource_rule_count != 1 else ''}")
        
        rules_text = ", ".join(rules_summary) if rules_summary else "no custom rules"
        
        return (
            f"Network access for '{account_name}': default action is {default_action}. "
            f"Rules: {rules_text}. "
            f"Bypass: {bypass_services}"
        )
    
    def _create_private_endpoints_summary(
        self, 
        private_endpoints: list, 
        account_name: str
    ) -> str:
        """Create human-readable summary for private endpoints."""
        if not private_endpoints:
            return f"No private endpoints configured for storage account '{account_name}'"
        
        count = len(private_endpoints)
        
        # Count by connection state
        states = {}
        for endpoint in private_endpoints:
            state = endpoint.connection_state
            states[state] = states.get(state, 0) + 1
        
        state_summary = ", ".join([f"{state}: {count}" for state, count in sorted(states.items())])
        
        return (
            f"Found {count} private endpoint{'s' if count != 1 else ''} for '{account_name}'. "
            f"Connection states: {state_summary}"
        )