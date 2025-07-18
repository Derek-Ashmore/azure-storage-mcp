"""Test configuration and fixtures for Azure Storage MCP tests."""

import pytest
from unittest.mock import Mock, MagicMock
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.identity import DefaultAzureCredential

from azure_storage_mcp.auth import AzureAuthManager
from azure_storage_mcp.tools import StorageAccountsTools, NetworkRulesTools, MetricsTools


@pytest.fixture
def mock_credential():
    """Mock Azure credential."""
    credential = Mock(spec=DefaultAzureCredential)
    credential.get_token.return_value = Mock(token="mock_token")
    return credential


@pytest.fixture
def mock_auth_manager(mock_credential):
    """Mock authentication manager."""
    auth_manager = Mock(spec=AzureAuthManager)
    auth_manager.get_credential.return_value = mock_credential
    auth_manager.test_authentication.return_value = True
    return auth_manager


@pytest.fixture
def mock_storage_client():
    """Mock Azure Storage Management client."""
    client = Mock(spec=StorageManagementClient)
    
    # Mock storage accounts list
    mock_account = Mock()
    mock_account.name = "teststorage"
    mock_account.id = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/test-rg/providers/Microsoft.Storage/storageAccounts/teststorage"
    mock_account.location = "eastus"
    mock_account.sku.name = "Standard_LRS"
    mock_account.kind.value = "StorageV2"
    mock_account.access_tier = None
    mock_account.creation_time = "2024-01-01T00:00:00Z"
    mock_account.last_modified_time = "2024-01-01T00:00:00Z"
    mock_account.provisioning_state.value = "Succeeded"
    mock_account.status_of_primary.value = "available"
    mock_account.status_of_secondary = None
    
    client.storage_accounts.list.return_value = [mock_account]
    client.storage_accounts.list_by_resource_group.return_value = [mock_account]
    client.storage_accounts.get_properties.return_value = mock_account
    
    # Mock network rules
    mock_network_rules = Mock()
    mock_network_rules.default_action.value = "Allow"
    mock_network_rules.ip_rules = []
    mock_network_rules.virtual_network_rules = []
    mock_network_rules.resource_access_rules = []
    mock_network_rules.bypass.value = "AzureServices"
    
    client.storage_accounts.get_network_rule_set.return_value = mock_network_rules
    
    # Mock blob service properties
    mock_blob_props = Mock()
    mock_blob_props.is_versioning_enabled = False
    mock_blob_props.change_feed = None
    mock_blob_props.delete_retention_policy = None
    mock_blob_props.container_delete_retention_policy = None
    mock_blob_props.restore_policy = None
    mock_blob_props.last_access_time_tracking_policy = None
    
    client.blob_services.get_service_properties.return_value = mock_blob_props
    
    # Mock private endpoints
    client.private_endpoint_connections.list.return_value = []
    
    return client


@pytest.fixture
def mock_monitor_client():
    """Mock Azure Monitor client."""
    client = Mock(spec=MonitorManagementClient)
    
    # Mock metric definitions
    mock_metric_def = Mock()
    mock_metric_def.name.value = "UsedCapacity"
    mock_metric_def.display_name = "Used Capacity"
    mock_metric_def.display_description = "Used capacity in bytes"
    mock_metric_def.unit.value = "Bytes"
    mock_metric_def.primary_aggregation_type.value = "Average"
    mock_metric_def.supported_aggregation_types = [Mock(value="Average")]
    mock_metric_def.dimensions = []
    
    mock_definitions = Mock()
    mock_definitions.value = [mock_metric_def]
    client.metric_definitions.list.return_value = mock_definitions
    
    # Mock metrics data
    mock_data_point = Mock()
    mock_data_point.time_stamp = "2024-01-01T00:00:00Z"
    mock_data_point.average = 1024.0
    mock_data_point.total = None
    mock_data_point.maximum = None
    mock_data_point.minimum = None
    mock_data_point.count = None
    
    mock_time_series = Mock()
    mock_time_series.data = [mock_data_point]
    
    mock_metric = Mock()
    mock_metric.unit.value = "Bytes"
    mock_metric.timeseries = [mock_time_series]
    
    mock_metrics_result = Mock()
    mock_metrics_result.value = [mock_metric]
    client.metrics.list.return_value = mock_metrics_result
    
    return client


@pytest.fixture
def storage_tools(mock_auth_manager):
    """Storage accounts tools instance."""
    return StorageAccountsTools(mock_auth_manager)


@pytest.fixture
def network_tools(mock_auth_manager):
    """Network rules tools instance."""
    return NetworkRulesTools(mock_auth_manager)


@pytest.fixture
def metrics_tools(mock_auth_manager):
    """Metrics tools instance."""
    return MetricsTools(mock_auth_manager)