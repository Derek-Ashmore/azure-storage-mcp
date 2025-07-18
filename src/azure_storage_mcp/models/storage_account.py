"""Data models for Azure Storage Account information."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResponseMetadata(BaseModel):
    """Common metadata for all responses."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: str = Field(description="Correlation ID for request tracking")
    request_id: Optional[str] = Field(None, description="Azure request ID")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")


class StorageAccountSummary(BaseModel):
    """Summary information for a storage account."""
    
    name: str = Field(description="Storage account name")
    resource_group: str = Field(description="Resource group name")
    location: str = Field(description="Azure region")
    sku: str = Field(description="SKU name (e.g., Standard_LRS)")
    kind: str = Field(description="Storage account kind (e.g., StorageV2)")
    access_tier: Optional[str] = Field(None, description="Default access tier")
    creation_time: datetime = Field(description="Account creation timestamp")
    last_modified_time: datetime = Field(description="Last modification timestamp")
    provisioning_state: str = Field(description="Provisioning state")
    status_of_primary: str = Field(description="Status of primary endpoint")
    status_of_secondary: Optional[str] = Field(None, description="Status of secondary endpoint")


class ListStorageAccountsRequest(BaseModel):
    """Request parameters for listing storage accounts."""
    
    subscription_id: str = Field(description="Azure subscription ID")
    resource_group: Optional[str] = Field(None, description="Resource group name (optional)")
    include_deleted: bool = Field(False, description="Include deleted storage accounts")


class ListStorageAccountsResponse(BaseModel):
    """Response for listing storage accounts."""
    
    storage_accounts: List[StorageAccountSummary] = Field(description="List of storage accounts")
    total_count: int = Field(description="Total number of storage accounts")
    metadata: ResponseMetadata = Field(description="Response metadata")
    summary: str = Field(description="Human-readable summary")


class SecuritySettings(BaseModel):
    """Security settings for a storage account."""
    
    require_secure_transfer: bool = Field(description="Require HTTPS for transfers")
    allow_blob_public_access: bool = Field(description="Allow public access to blobs")
    allow_shared_key_access: bool = Field(description="Allow shared key access")
    allow_cross_tenant_replication: bool = Field(description="Allow cross-tenant replication")
    public_network_access: str = Field(description="Public network access setting")
    minimum_tls_version: str = Field(description="Minimum TLS version")
    encryption_at_rest: Dict[str, Any] = Field(description="Encryption at rest settings")
    encryption_in_transit: Dict[str, Any] = Field(description="Encryption in transit settings")


class IpRule(BaseModel):
    """IP rule for network access."""
    
    ip_address_or_range: str = Field(description="IP address or CIDR range")
    action: str = Field(description="Allow or Deny")


class VirtualNetworkRule(BaseModel):
    """Virtual network rule for network access."""
    
    subnet_id: str = Field(description="Subnet resource ID")
    action: str = Field(description="Allow or Deny")
    state: str = Field(description="Rule state")


class ResourceAccessRule(BaseModel):
    """Resource access rule for network access."""
    
    tenant_id: str = Field(description="Tenant ID")
    resource_id: str = Field(description="Resource ID")


class NetworkConfiguration(BaseModel):
    """Network configuration for a storage account."""
    
    default_action: str = Field(description="Default network access action")
    ip_rules: List[IpRule] = Field(description="IP access rules")
    virtual_network_rules: List[VirtualNetworkRule] = Field(description="VNet access rules")
    resource_access_rules: List[ResourceAccessRule] = Field(description="Resource access rules")
    bypass: str = Field(description="Services that can bypass network rules")


class BlobServiceProperties(BaseModel):
    """Blob service properties."""
    
    versioning_enabled: bool = Field(description="Is versioning enabled")
    change_feed_enabled: bool = Field(description="Is change feed enabled")
    soft_delete_enabled: bool = Field(description="Is soft delete enabled")
    soft_delete_retention_days: Optional[int] = Field(None, description="Soft delete retention days")
    container_soft_delete_enabled: bool = Field(description="Is container soft delete enabled")
    container_soft_delete_retention_days: Optional[int] = Field(None, description="Container soft delete retention days")
    restore_policy_enabled: bool = Field(description="Is restore policy enabled")
    restore_policy_days: Optional[int] = Field(None, description="Restore policy days")
    last_access_time_tracking_enabled: bool = Field(description="Is last access time tracking enabled")


class AccessPolicy(BaseModel):
    """Access policy information."""
    
    id: str = Field(description="Policy ID")
    start_time: Optional[datetime] = Field(None, description="Policy start time")
    expiry_time: Optional[datetime] = Field(None, description="Policy expiry time")
    permissions: str = Field(description="Permissions string")


class DiagnosticSettings(BaseModel):
    """Diagnostic settings for storage account."""
    
    enabled: bool = Field(description="Are diagnostic settings enabled")
    workspace_id: Optional[str] = Field(None, description="Log Analytics workspace ID")
    storage_account_id: Optional[str] = Field(None, description="Storage account ID for logs")
    retention_policy: Optional[Dict[str, Any]] = Field(None, description="Retention policy")
    categories: List[str] = Field(description="Enabled log categories")
    metrics: List[str] = Field(description="Enabled metrics")


class StorageAccountBasicProperties(BaseModel):
    """Basic properties of a storage account."""
    
    name: str = Field(description="Storage account name")
    resource_group: str = Field(description="Resource group name")
    subscription_id: str = Field(description="Subscription ID")
    location: str = Field(description="Azure region")
    sku: str = Field(description="SKU name")
    kind: str = Field(description="Storage account kind")
    access_tier: Optional[str] = Field(None, description="Default access tier")
    creation_time: datetime = Field(description="Creation timestamp")
    last_modified_time: datetime = Field(description="Last modification timestamp")
    provisioning_state: str = Field(description="Provisioning state")
    primary_location: str = Field(description="Primary location")
    secondary_location: Optional[str] = Field(None, description="Secondary location")
    status_of_primary: str = Field(description="Primary endpoint status")
    status_of_secondary: Optional[str] = Field(None, description="Secondary endpoint status")
    primary_endpoints: Dict[str, str] = Field(description="Primary service endpoints")
    secondary_endpoints: Optional[Dict[str, str]] = Field(None, description="Secondary service endpoints")


class StorageAccountDetails(BaseModel):
    """Complete details for a storage account."""
    
    basic_properties: StorageAccountBasicProperties = Field(description="Basic account properties")
    security_settings: SecuritySettings = Field(description="Security configuration")
    network_configuration: NetworkConfiguration = Field(description="Network settings")
    blob_service_properties: BlobServiceProperties = Field(description="Blob service settings")
    access_policies: List[AccessPolicy] = Field(description="Access policies")
    diagnostic_settings: DiagnosticSettings = Field(description="Diagnostic configuration")
    metadata: ResponseMetadata = Field(description="Response metadata")
    summary: str = Field(description="Human-readable summary")


class GetStorageAccountDetailsRequest(BaseModel):
    """Request parameters for getting storage account details."""
    
    subscription_id: str = Field(description="Azure subscription ID")
    resource_group: str = Field(description="Resource group name")
    account_name: str = Field(description="Storage account name")
    include_keys: bool = Field(False, description="Include access keys (requires permissions)")