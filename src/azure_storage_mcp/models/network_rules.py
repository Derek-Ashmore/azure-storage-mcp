"""Data models for Azure Storage network rules and configurations."""

from typing import List
from pydantic import BaseModel, Field

from .storage_account import ResponseMetadata, IpRule, VirtualNetworkRule, ResourceAccessRule


class GetNetworkRulesRequest(BaseModel):
    """Request parameters for getting network rules."""
    
    subscription_id: str = Field(description="Azure subscription ID")
    resource_group: str = Field(description="Resource group name")
    account_name: str = Field(description="Storage account name")


class NetworkRules(BaseModel):
    """Network access rules for a storage account."""
    
    default_action: str = Field(description="Default network access action (Allow/Deny)")
    ip_rules: List[IpRule] = Field(description="IP access rules")
    virtual_network_rules: List[VirtualNetworkRule] = Field(description="Virtual network access rules")
    resource_access_rules: List[ResourceAccessRule] = Field(description="Resource access rules")
    bypass: str = Field(description="Services that can bypass network rules")
    metadata: ResponseMetadata = Field(description="Response metadata")
    summary: str = Field(description="Human-readable summary")


class NetworkInterfaceInfo(BaseModel):
    """Network interface information for private endpoints."""
    
    id: str = Field(description="Network interface ID")
    name: str = Field(description="Network interface name")
    private_ip_address: str = Field(description="Private IP address")
    subnet_id: str = Field(description="Subnet ID")
    is_primary: bool = Field(description="Is this the primary interface")


class PrivateEndpointConnection(BaseModel):
    """Private endpoint connection information."""
    
    name: str = Field(description="Connection name")
    private_endpoint_id: str = Field(description="Private endpoint resource ID")
    connection_state: str = Field(description="Connection state (Approved/Rejected/Pending)")
    provisioning_state: str = Field(description="Provisioning state")
    network_interface_info: NetworkInterfaceInfo = Field(description="Network interface details")
    dns_zones: List[str] = Field(description="Associated DNS zones")
    actions_required: List[str] = Field(description="Actions required to complete connection")
    description: str = Field(description="Connection description")


class GetPrivateEndpointsRequest(BaseModel):
    """Request parameters for getting private endpoints."""
    
    subscription_id: str = Field(description="Azure subscription ID")
    resource_group: str = Field(description="Resource group name")
    account_name: str = Field(description="Storage account name")


class GetPrivateEndpointsResponse(BaseModel):
    """Response for getting private endpoints."""
    
    private_endpoints: List[PrivateEndpointConnection] = Field(description="Private endpoint connections")
    total_count: int = Field(description="Total number of private endpoints")
    metadata: ResponseMetadata = Field(description="Response metadata")
    summary: str = Field(description="Human-readable summary")