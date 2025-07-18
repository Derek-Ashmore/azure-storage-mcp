"""Data models for Azure Storage MCP server."""

from .storage_account import (
    ResponseMetadata,
    StorageAccountSummary,
    ListStorageAccountsRequest,
    ListStorageAccountsResponse,
    StorageAccountDetails,
    GetStorageAccountDetailsRequest,
    SecuritySettings,
    NetworkConfiguration,
    BlobServiceProperties,
    AccessPolicy,
    DiagnosticSettings,
    StorageAccountBasicProperties,
    IpRule,
    VirtualNetworkRule,
    ResourceAccessRule,
)
from .network_rules import (
    GetNetworkRulesRequest,
    NetworkRules,
    NetworkInterfaceInfo,
    PrivateEndpointConnection,
    GetPrivateEndpointsRequest,
    GetPrivateEndpointsResponse,
)
from .metrics import (
    MetricDataPoint,
    MetricDefinition,
    GetStorageMetricsRequest,
    StorageMetrics,
)

__all__ = [
    # Common models
    "ResponseMetadata",
    "IpRule",
    "VirtualNetworkRule", 
    "ResourceAccessRule",
    
    # Storage account models
    "StorageAccountSummary",
    "ListStorageAccountsRequest",
    "ListStorageAccountsResponse",
    "StorageAccountDetails",
    "GetStorageAccountDetailsRequest",
    "SecuritySettings",
    "NetworkConfiguration",
    "BlobServiceProperties",
    "AccessPolicy",
    "DiagnosticSettings",
    "StorageAccountBasicProperties",
    
    # Network rules models
    "GetNetworkRulesRequest",
    "NetworkRules",
    "NetworkInterfaceInfo",
    "PrivateEndpointConnection",
    "GetPrivateEndpointsRequest",
    "GetPrivateEndpointsResponse",
    
    # Metrics models
    "MetricDataPoint",
    "MetricDefinition",
    "GetStorageMetricsRequest",
    "StorageMetrics",
]