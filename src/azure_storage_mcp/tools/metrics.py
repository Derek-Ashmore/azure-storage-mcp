"""MCP tools for Azure Storage metrics operations."""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.mgmt.monitor import MonitorManagementClient

from ..auth import AzureAuthManager, SecurityValidator
from ..models import (
    GetStorageMetricsRequest,
    StorageMetrics,
    MetricDataPoint,
    MetricDefinition,
    ResponseMetadata,
)
from ..utils import (
    AzureStorageMCPError,
    AuthenticationError,
    PermissionError,
    ValidationError,
    AzureAPIError,
    StructuredLogger,
)


class MetricsTools:
    """Tools for Azure Storage metrics operations."""
    
    def __init__(self, auth_manager: AzureAuthManager) -> None:
        self.auth_manager = auth_manager
        self.logger = StructuredLogger(__name__)
        self._monitor_client: Optional[MonitorManagementClient] = None
    
    async def _get_monitor_client(self, subscription_id: str) -> MonitorManagementClient:
        """Get or create Azure Monitor client."""
        if self._monitor_client is None:
            credential = await self.auth_manager.get_credential()
            self._monitor_client = MonitorManagementClient(
                credential=credential,
                subscription_id=subscription_id
            )
        return self._monitor_client
    
    async def get_storage_metrics(self, request: GetStorageMetricsRequest) -> StorageMetrics:
        """Get storage metrics for a storage account."""
        start_time = datetime.utcnow()
        correlation_id = str(uuid.uuid4())
        
        try:
            # Validate inputs
            SecurityValidator.validate_subscription_id(request.subscription_id)
            SecurityValidator.validate_resource_group(request.resource_group)
            SecurityValidator.validate_storage_account_name(request.account_name)
            
            # Get Azure client
            client = await self._get_monitor_client(request.subscription_id)
            
            # Build resource ID
            resource_id = (
                f"/subscriptions/{request.subscription_id}"
                f"/resourceGroups/{request.resource_group}"
                f"/providers/Microsoft.Storage/storageAccounts/{request.account_name}"
            )
            
            # Parse time range
            end_time = datetime.utcnow()
            start_time_metrics = self._parse_time_range(request.time_range, end_time)
            
            # Get available metrics first
            available_metrics = self._get_available_metrics(client, resource_id)
            
            # Get metrics data
            metrics_data = {}
            aggregated_summary = {}
            
            for metric_name in request.metrics:
                try:
                    metric_result = client.metrics.list(
                        resource_uri=resource_id,
                        timespan=f"{start_time_metrics.isoformat()}/{end_time.isoformat()}",
                        interval=request.interval,
                        metricnames=metric_name,
                        aggregation=request.aggregation_type
                    )
                    
                    data_points = []
                    total_value = 0
                    count = 0
                    
                    for metric in metric_result.value:
                        for time_series in metric.timeseries:
                            for data_point in time_series.data:
                                if data_point.time_stamp and self._has_metric_value(data_point, request.aggregation_type):
                                    value = self._get_metric_value(data_point, request.aggregation_type)
                                    
                                    point = MetricDataPoint(
                                        timestamp=data_point.time_stamp,
                                        value=value,
                                        unit=metric.unit.value if hasattr(metric.unit, 'value') else str(metric.unit),
                                        aggregation_type=request.aggregation_type
                                    )
                                    data_points.append(point)
                                    total_value += value
                                    count += 1
                    
                    metrics_data[metric_name] = data_points
                    aggregated_summary[metric_name] = total_value / count if count > 0 else 0
                    
                except HttpResponseError as e:
                    self.logger.log_error(e, {"metric_name": metric_name, "correlation_id": correlation_id})
                    # Continue with other metrics if one fails
                    metrics_data[metric_name] = []
                    aggregated_summary[metric_name] = 0
            
            # Create response
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            metadata = ResponseMetadata(
                correlation_id=correlation_id,
                execution_time_ms=execution_time
            )
            
            response = StorageMetrics(
                account_name=request.account_name,
                time_range=request.time_range,
                start_time=start_time_metrics,
                end_time=end_time,
                metrics_data=metrics_data,
                aggregated_summary=aggregated_summary,
                available_metrics=available_metrics,
                metadata=metadata,
                summary=self._create_metrics_summary(request, aggregated_summary)
            )
            
            self.logger.log_tool_execution(
                "get_storage_metrics",
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
                    f"Insufficient permissions to access metrics: {str(e)}",
                    "Microsoft.Insights/metrics/read"
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
    
    def _get_available_metrics(
        self, 
        client: MonitorManagementClient, 
        resource_id: str
    ) -> List[MetricDefinition]:
        """Get available metrics for the storage account."""
        try:
            definitions = client.metric_definitions.list(resource_uri=resource_id)
            
            return [
                MetricDefinition(
                    name=definition.name.value if hasattr(definition.name, 'value') else str(definition.name),
                    display_name=definition.display_name,
                    description=definition.display_description or "",
                    unit=definition.unit.value if hasattr(definition.unit, 'value') else str(definition.unit),
                    primary_aggregation_type=definition.primary_aggregation_type.value if hasattr(definition.primary_aggregation_type, 'value') else str(definition.primary_aggregation_type),
                    supported_aggregation_types=[agg.value if hasattr(agg, 'value') else str(agg) for agg in definition.supported_aggregation_types],
                    dimensions=[dim.value if hasattr(dim, 'value') else str(dim) for dim in definition.dimensions] if definition.dimensions else []
                )
                for definition in definitions.value
            ]
        except Exception as e:
            self.logger.log_error(e, {"context": "get_available_metrics"})
            return []
    
    def _parse_time_range(self, time_range: str, end_time: datetime) -> datetime:
        """Parse time range string to start time."""
        if time_range == "1h":
            return end_time - timedelta(hours=1)
        elif time_range == "24h":
            return end_time - timedelta(hours=24)
        elif time_range == "7d":
            return end_time - timedelta(days=7)
        elif time_range == "30d":
            return end_time - timedelta(days=30)
        else:
            # Default to 1 hour
            return end_time - timedelta(hours=1)
    
    def _has_metric_value(self, data_point, aggregation_type: str) -> bool:
        """Check if data point has a value for the aggregation type."""
        if aggregation_type.lower() == "average":
            return data_point.average is not None
        elif aggregation_type.lower() == "total":
            return data_point.total is not None
        elif aggregation_type.lower() == "maximum":
            return data_point.maximum is not None
        elif aggregation_type.lower() == "minimum":
            return data_point.minimum is not None
        elif aggregation_type.lower() == "count":
            return data_point.count is not None
        else:
            return data_point.average is not None
    
    def _get_metric_value(self, data_point, aggregation_type: str) -> float:
        """Get metric value from data point based on aggregation type."""
        if aggregation_type.lower() == "average":
            return data_point.average or 0
        elif aggregation_type.lower() == "total":
            return data_point.total or 0
        elif aggregation_type.lower() == "maximum":
            return data_point.maximum or 0
        elif aggregation_type.lower() == "minimum":
            return data_point.minimum or 0
        elif aggregation_type.lower() == "count":
            return data_point.count or 0
        else:
            return data_point.average or 0
    
    def _create_metrics_summary(
        self, 
        request: GetStorageMetricsRequest, 
        aggregated_summary: Dict[str, float]
    ) -> str:
        """Create human-readable summary for metrics."""
        if not aggregated_summary:
            return f"No metrics data available for '{request.account_name}' in the last {request.time_range}"
        
        metrics_text = []
        for metric_name, value in aggregated_summary.items():
            if metric_name == "UsedCapacity":
                # Convert bytes to GB for readability
                value_gb = value / (1024 * 1024 * 1024)
                metrics_text.append(f"{metric_name}: {value_gb:.2f} GB")
            elif metric_name == "Transactions":
                metrics_text.append(f"{metric_name}: {value:.0f}")
            else:
                metrics_text.append(f"{metric_name}: {value:.2f}")
        
        metrics_summary = ", ".join(metrics_text)
        
        return (
            f"Metrics for '{request.account_name}' over the last {request.time_range} "
            f"({request.aggregation_type}): {metrics_summary}"
        )