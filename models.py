"""Data models for The Living Ledger"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class CertificationStatus(str, Enum):
    UNCERTIFIED = "uncertified"
    PENDING_REVIEW = "pending_review"
    CERTIFIED = "certified"
    DENIED = "denied"
    OUTDATED = "outdated"


@dataclass
class DataSourceConfig:
    connection_string: str
    source_type: str
    sampling_rate: float = 0.1
    max_sample_size: int = 10000


@dataclass
class SchemaMetadata:
    table_name: str
    column_name: str
    data_type: str
    nullable: bool
    constraints: List[str] = field(default_factory=list)


@dataclass
class DataSample:
    table_name: str
    column_name: str
    sample_values: List[Any]
    sample_size: int


@dataclass
class StatisticalMetrics:
    column_id: str
    mean: Optional[float]
    std_dev: Optional[float]
    entropy: float
    distinct_count: int
    null_percentage: float
    distribution_type: str
    calculated_at: datetime
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None


@dataclass
class SemanticDescription:
    column_id: str
    business_name: str
    description: str
    business_domain: str
    example_values: List[str]
    usage_guidelines: str
    confidence_score: float
    generated_at: datetime


@dataclass
class MetadataEntity:
    entity_id: str
    schema_metadata: SchemaMetadata
    statistical_metrics: StatisticalMetrics
    semantic_description: SemanticDescription
    certification_status: CertificationStatus
    version: int
    created_at: datetime
    updated_at: datetime
    certified_by: Optional[str] = None
    certified_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class DriftAlert:
    alert_id: str
    column_id: str
    metric_name: str
    previous_value: float
    current_value: float
    drift_percentage: float
    severity: str
    detected_at: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
