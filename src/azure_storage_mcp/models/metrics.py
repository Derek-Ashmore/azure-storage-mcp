"""Data models for Azure Storage metrics and monitoring."""

from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel, Field

from .storage_account import ResponseMetadata


class MetricDataPoint(BaseModel):
    """A single metric data point."""
    
    timestamp: datetime = Field(description="Data point timestamp")
    value: float = Field(description="Metric value")
    unit: str = Field(description="Unit of measurement")
    aggregation_type: str = Field(description="Aggregation type (Average, Total, Maximum, etc.)")


class MetricDefinition(BaseModel):
    """Metric definition information."""
    
    name: str = Field(description="Metric name")
    display_name: str = Field(description="Display name")
    description: str = Field(description="Metric description")
    unit: str = Field(description="Unit of measurement")
    primary_aggregation_type: str = Field(description="Primary aggregation type")
    supported_aggregation_types: List[str] = Field(description="Supported aggregation types")
    dimensions: List[str] = Field(description="Available dimensions")


class GetStorageMetricsRequest(BaseModel):
    """Request parameters for getting storage metrics."""
    
    subscription_id: str = Field(description="Azure subscription ID")
    resource_group: str = Field(description="Resource group name")
    account_name: str = Field(description="Storage account name")
    time_range: str = Field("1h", description="Time range (1h, 24h, 7d, 30d)")
    metrics: List[str] = Field(
        default_factory=lambda: ["UsedCapacity", "Transactions"],
        description="Metrics to retrieve"
    )
    aggregation_type: str = Field("Average", description="Aggregation type")
    interval: str = Field("PT1H", description="Time interval for data points")


class StorageMetrics(BaseModel):
    """Storage account metrics data."""
    
    account_name: str = Field(description="Storage account name")
    time_range: str = Field(description="Time range for metrics")
    start_time: datetime = Field(description="Start time for metrics")
    end_time: datetime = Field(description="End time for metrics")
    metrics_data: Dict[str, List[MetricDataPoint]] = Field(description="Metrics data by metric name")
    aggregated_summary: Dict[str, float] = Field(description="Aggregated summary values")
    available_metrics: List[MetricDefinition] = Field(description="Available metrics for this account")
    metadata: ResponseMetadata = Field(description="Response metadata")
    summary: str = Field(description="Human-readable summary")