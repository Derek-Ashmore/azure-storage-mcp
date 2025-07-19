"""MCP tools for Azure Storage Account operations."""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlobServiceClient

from ..auth import AzureAuthManager, SecurityValidator
from ..models import (
    ListStorageAccountsRequest,
    ListStorageAccountsResponse,
    StorageAccountSummary,
    GetStorageAccountDetailsRequest,
    StorageAccountDetails,
    StorageAccountBasicProperties,
    SecuritySettings,
    NetworkConfiguration,
    BlobServiceProperties,
    AccessPolicy,
    DiagnosticSettings,
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


class StorageAccountsTools:
    """Tools for Azure Storage Account operations."""
    
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
    
    async def list_storage_accounts(
        self, 
        request: ListStorageAccountsRequest
    ) -> ListStorageAccountsResponse:
        """List storage accounts in subscription or resource group."""
        start_time = datetime.utcnow()
        correlation_id = str(uuid.uuid4())
        
        try:
            # Validate inputs
            SecurityValidator.validate_subscription_id(request.subscription_id)
            if request.resource_group:
                SecurityValidator.validate_resource_group(request.resource_group)
            
            # Get Azure client
            client = await self._get_storage_client(request.subscription_id)
            
            # List storage accounts
            if request.resource_group:
                accounts_iterator = client.storage_accounts.list_by_resource_group(
                    request.resource_group
                )
            else:
                accounts_iterator = client.storage_accounts.list()
            
            # Convert to our model
            storage_accounts = []
            for account in accounts_iterator:
                summary = StorageAccountSummary(
                    name=account.name,
                    resource_group=account.id.split('/')[4],  # Extract from resource ID
                    location=account.location,
                    sku=account.sku.name,
                    kind=account.kind.value if hasattr(account.kind, 'value') else str(account.kind),
                    access_tier=account.access_tier.value if account.access_tier and hasattr(account.access_tier, 'value') else str(account.access_tier) if account.access_tier else None,
                    creation_time=account.creation_time,
                    last_modified_time=getattr(account, 'last_modified_time', account.creation_time),
                    provisioning_state=account.provisioning_state.value if hasattr(account.provisioning_state, 'value') else str(account.provisioning_state),
                    status_of_primary=account.status_of_primary.value if hasattr(account.status_of_primary, 'value') else str(account.status_of_primary),
                    status_of_secondary=account.status_of_secondary.value if account.status_of_secondary and hasattr(account.status_of_secondary, 'value') else str(account.status_of_secondary) if account.status_of_secondary else None,
                )
                storage_accounts.append(summary)
            
            # Create response
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            metadata = ResponseMetadata(
                correlation_id=correlation_id,
                execution_time_ms=execution_time
            )
            
            summary_text = self._create_list_summary(storage_accounts, request)
            
            response = ListStorageAccountsResponse(
                storage_accounts=storage_accounts,
                total_count=len(storage_accounts),
                metadata=metadata,
                summary=summary_text
            )
            
            self.logger.log_tool_execution(
                "list_storage_accounts",
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
                    f"Insufficient permissions to list storage accounts: {str(e)}",
                    "Microsoft.Storage/storageAccounts/read"
                )
            else:
                error = AzureAPIError(f"Azure API error: {str(e)}", e.status_code)
            self.logger.log_error(error, {"correlation_id": correlation_id})
            raise error
        except Exception as e:
            error = AzureStorageMCPError(f"Unexpected error: {str(e)}")
            self.logger.log_error(error, {"correlation_id": correlation_id})
            raise error
    
    async def get_storage_account_details(
        self, 
        request: GetStorageAccountDetailsRequest
    ) -> StorageAccountDetails:
        """Get detailed information for a specific storage account."""
        start_time = datetime.utcnow()
        correlation_id = str(uuid.uuid4())
        
        try:
            # Validate inputs
            SecurityValidator.validate_subscription_id(request.subscription_id)
            SecurityValidator.validate_resource_group(request.resource_group)
            SecurityValidator.validate_storage_account_name(request.account_name)
            
            # Get Azure client
            client = await self._get_storage_client(request.subscription_id)
            
            # Get storage account details
            try:
                account_props = client.storage_accounts.get_properties(
                    request.resource_group, 
                    request.account_name
                )
            except Exception as e:
                raise e
            
            # Get network rules (optional)
            try:
                network_rules = account_props.network_rule_set
            except Exception as e:
                self.logger.log_error(e, {"context": "get_network_rules"})
                network_rules = None
            
            # Get blob service properties (optional)
            try:
                blob_props = client.blob_services.get_service_properties(
                    request.resource_group, 
                    request.account_name
                )
            except Exception as e:
                self.logger.log_error(e, {"context": "get_blob_properties"})
                blob_props = None
            
            # Build response
            basic_properties = await self._build_basic_properties(account_props, request)
            security_settings = await self._build_security_settings(account_props)
            network_configuration = await self._build_network_configuration(network_rules)
            blob_service_properties = await self._build_blob_service_properties(blob_props)
            
            # Create response
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            metadata = ResponseMetadata(
                correlation_id=correlation_id,
                execution_time_ms=execution_time
            )
            
            summary_text = self._create_details_summary(basic_properties, security_settings)
            
            response = StorageAccountDetails(
                basic_properties=basic_properties,
                security_settings=security_settings,
                network_configuration=network_configuration,
                blob_service_properties=blob_service_properties,
                access_policies=[],  # Would need additional API calls to populate
                diagnostic_settings=DiagnosticSettings(
                    enabled=False,
                    categories=[],
                    metrics=[]
                ),
                metadata=metadata,
                summary=summary_text
            )
            
            self.logger.log_tool_execution(
                "get_storage_account_details",
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
                    f"Insufficient permissions to access storage account: {str(e)}",
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
    
    async def _build_basic_properties(
        self, 
        account_props, 
        request: GetStorageAccountDetailsRequest
    ) -> StorageAccountBasicProperties:
        """Build basic properties from Azure account properties."""
        return StorageAccountBasicProperties(
            name=account_props.name,
            resource_group=request.resource_group,
            subscription_id=request.subscription_id,
            location=account_props.location,
            sku=account_props.sku.name,
            kind=account_props.kind.value if hasattr(account_props.kind, 'value') else str(account_props.kind),
            access_tier=account_props.access_tier.value if account_props.access_tier and hasattr(account_props.access_tier, 'value') else str(account_props.access_tier) if account_props.access_tier else None,
            creation_time=account_props.creation_time,
            last_modified_time=getattr(account_props, 'last_modified_time', account_props.creation_time),
            provisioning_state=account_props.provisioning_state.value if hasattr(account_props.provisioning_state, 'value') else str(account_props.provisioning_state),
            primary_location=account_props.primary_location,
            secondary_location=account_props.secondary_location,
            status_of_primary=account_props.status_of_primary.value if hasattr(account_props.status_of_primary, 'value') else str(account_props.status_of_primary),
            status_of_secondary=account_props.status_of_secondary.value if account_props.status_of_secondary and hasattr(account_props.status_of_secondary, 'value') else str(account_props.status_of_secondary) if account_props.status_of_secondary else None,
            primary_endpoints={
                "blob": account_props.primary_endpoints.blob,
                "queue": account_props.primary_endpoints.queue,
                "table": account_props.primary_endpoints.table,
                "file": account_props.primary_endpoints.file,
            },
            secondary_endpoints={
                "blob": account_props.secondary_endpoints.blob,
                "queue": account_props.secondary_endpoints.queue,
                "table": account_props.secondary_endpoints.table,
                "file": account_props.secondary_endpoints.file,
            } if account_props.secondary_endpoints else None,
        )
    
    async def _build_security_settings(self, account_props) -> SecuritySettings:
        """Build security settings from Azure account properties."""
        return SecuritySettings(
            require_secure_transfer=account_props.enable_https_traffic_only,
            allow_blob_public_access=account_props.allow_blob_public_access,
            allow_shared_key_access=account_props.allow_shared_key_access,
            allow_cross_tenant_replication=account_props.allow_cross_tenant_replication,
            public_network_access=account_props.public_network_access.value if account_props.public_network_access and hasattr(account_props.public_network_access, 'value') else str(account_props.public_network_access) if account_props.public_network_access else "Enabled",
            minimum_tls_version=account_props.minimum_tls_version.value if account_props.minimum_tls_version and hasattr(account_props.minimum_tls_version, 'value') else str(account_props.minimum_tls_version) if account_props.minimum_tls_version else "TLS1_0",
            encryption_at_rest={
                "enabled": account_props.encryption.services.blob.enabled if account_props.encryption else False,
                "key_source": account_props.encryption.key_source.value if account_props.encryption and hasattr(account_props.encryption.key_source, 'value') else str(account_props.encryption.key_source) if account_props.encryption else "Microsoft.Storage"
            },
            encryption_in_transit={
                "enabled": account_props.enable_https_traffic_only,
                "minimum_tls_version": account_props.minimum_tls_version.value if account_props.minimum_tls_version and hasattr(account_props.minimum_tls_version, 'value') else str(account_props.minimum_tls_version) if account_props.minimum_tls_version else "TLS1_0"
            }
        )
    
    async def _build_network_configuration(self, network_rules) -> NetworkConfiguration:
        """Build network configuration from Azure network rules."""
        if not network_rules:
            return NetworkConfiguration(
                default_action="Allow",
                ip_rules=[],
                virtual_network_rules=[],
                resource_access_rules=[],
                bypass="AzureServices"
            )
        
        return NetworkConfiguration(
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
            bypass=network_rules.bypass.value if network_rules.bypass and hasattr(network_rules.bypass, 'value') else str(network_rules.bypass) if network_rules.bypass else "None"
        )
    
    async def _build_blob_service_properties(self, blob_props) -> BlobServiceProperties:
        """Build blob service properties from Azure blob properties."""
        if not blob_props:
            return BlobServiceProperties(
                versioning_enabled=False,
                change_feed_enabled=False,
                soft_delete_enabled=False,
                soft_delete_retention_days=None,
                container_soft_delete_enabled=False,
                container_soft_delete_retention_days=None,
                restore_policy_enabled=False,
                restore_policy_days=None,
                last_access_time_tracking_enabled=False
            )
        
        return BlobServiceProperties(
            versioning_enabled=blob_props.is_versioning_enabled if hasattr(blob_props, 'is_versioning_enabled') else False,
            change_feed_enabled=blob_props.change_feed.enabled if hasattr(blob_props, 'change_feed') and blob_props.change_feed else False,
            soft_delete_enabled=blob_props.delete_retention_policy.enabled if hasattr(blob_props, 'delete_retention_policy') and blob_props.delete_retention_policy else False,
            soft_delete_retention_days=blob_props.delete_retention_policy.days if hasattr(blob_props, 'delete_retention_policy') and blob_props.delete_retention_policy and blob_props.delete_retention_policy.enabled else None,
            container_soft_delete_enabled=blob_props.container_delete_retention_policy.enabled if hasattr(blob_props, 'container_delete_retention_policy') and blob_props.container_delete_retention_policy else False,
            container_soft_delete_retention_days=blob_props.container_delete_retention_policy.days if hasattr(blob_props, 'container_delete_retention_policy') and blob_props.container_delete_retention_policy and blob_props.container_delete_retention_policy.enabled else None,
            restore_policy_enabled=blob_props.restore_policy.enabled if hasattr(blob_props, 'restore_policy') and blob_props.restore_policy else False,
            restore_policy_days=blob_props.restore_policy.days if hasattr(blob_props, 'restore_policy') and blob_props.restore_policy and blob_props.restore_policy.enabled else None,
            last_access_time_tracking_enabled=blob_props.last_access_time_tracking_policy.enabled if hasattr(blob_props, 'last_access_time_tracking_policy') and blob_props.last_access_time_tracking_policy else False
        )
    
    def _create_list_summary(
        self, 
        accounts: List[StorageAccountSummary], 
        request: ListStorageAccountsRequest
    ) -> str:
        """Create human-readable summary for list operation."""
        if not accounts:
            scope = f"resource group '{request.resource_group}'" if request.resource_group else "subscription"
            return f"No storage accounts found in {scope}"
        
        scope = f"resource group '{request.resource_group}'" if request.resource_group else "subscription"
        count = len(accounts)
        
        # Count by region
        locations = {}
        for account in accounts:
            locations[account.location] = locations.get(account.location, 0) + 1
        
        location_summary = ", ".join([f"{loc}: {count}" for loc, count in sorted(locations.items())])
        
        return f"Found {count} storage account{'s' if count != 1 else ''} in {scope}. Distribution by region: {location_summary}"
    
    def _create_details_summary(
        self, 
        basic_props: StorageAccountBasicProperties, 
        security_settings: SecuritySettings
    ) -> str:
        """Create human-readable summary for details operation."""
        security_items = []
        
        if security_settings.require_secure_transfer:
            security_items.append("secure transfer required")
        
        if not security_settings.allow_blob_public_access:
            security_items.append("public access disabled")
        
        if not security_settings.allow_shared_key_access:
            security_items.append("shared key access disabled")
        
        security_summary = ", ".join(security_items) if security_items else "standard security settings"
        
        return (
            f"Storage account '{basic_props.name}' in {basic_props.location} "
            f"({basic_props.sku}, {basic_props.kind}). "
            f"Security: {security_summary}. "
            f"Status: {basic_props.provisioning_state}"
        )