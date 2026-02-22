"""Statistical Engine for metadata profiling"""
import math
import statistics
from datetime import datetime
from typing import Optional, List, Dict, Any

from models import DataSample, StatisticalMetrics, DriftAlert


class StatisticalEngine:
    """Performs statistical analysis on data samples"""
    
    def __init__(self):
        self.thresholds = {
            'low': 10.0,
            'medium': 25.0,
            'high': 50.0,
            'critical': 75.0
        }
    
    async def calculate_metrics(self, sample: DataSample) -> StatisticalMetrics:
        """Calculate statistical metrics for a data sample"""
        values = [v for v in sample.sample_values if v is not None]
        total_count = len(sample.sample_values)
        
        # Calculate null percentage
        null_count = total_count - len(values)
        null_percentage = (null_count / total_count * 100) if total_count > 0 else 0.0
        
        # Calculate distinct count
        distinct_count = len(set(values)) if values else 0
        
        # Calculate entropy
        entropy = self._calculate_shannon_entropy(values)
        
        # Try to calculate numeric statistics
        mean = None
        std_dev = None
        min_val = None
        max_val = None
        
        try:
            numeric_values = [float(v) for v in values]
            if numeric_values:
                mean = statistics.mean(numeric_values)
                std_dev = statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0.0
                min_val = min(numeric_values)
                max_val = max(numeric_values)
        except (ValueError, TypeError):
            # Not numeric data
            if values:
                min_val = min(values)
                max_val = max(values)
        
        # Determine distribution type
        distribution_type = self._analyze_distribution(values, mean, std_dev)
        
        return StatisticalMetrics(
            column_id=f"{sample.table_name}.{sample.column_name}",
            mean=mean,
            std_dev=std_dev,
            entropy=entropy,
            distinct_count=distinct_count,
            null_percentage=null_percentage,
            distribution_type=distribution_type,
            calculated_at=datetime.utcnow(),
            min_value=min_val,
            max_value=max_val
        )
    
    def _calculate_shannon_entropy(self, values: List[Any]) -> float:
        """Calculate Shannon entropy for categorical data"""
        if not values:
            return 0.0
        
        # Count value frequencies
        value_counts = {}
        for value in values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        # Calculate probabilities and entropy
        total_count = len(values)
        entropy = 0.0
        
        for count in value_counts.values():
            prob = count / total_count
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        return entropy
    
    def _analyze_distribution(self, values: List[Any], mean: Optional[float], 
                            std_dev: Optional[float]) -> str:
        """Analyze and classify data distribution type"""
        if not values:
            return 'unknown'
        
        distinct_count = len(set(values))
        total_count = len(values)
        
        # If mostly unique values, likely uniform
        if distinct_count / total_count > 0.9:
            return 'uniform'
        
        # If very few distinct values, likely categorical
        if distinct_count < 10:
            return 'categorical'
        
        # For numeric data, check if normal
        if mean is not None and std_dev is not None:
            try:
                numeric_values = [float(v) for v in values]
                # Simple skewness check
                median = statistics.median(numeric_values)
                if abs(mean - median) < std_dev * 0.1:
                    return 'normal'
                else:
                    return 'skewed'
            except (ValueError, TypeError):
                pass
        
        return 'unknown'
    
    async def detect_drift(
        self,
        column_id: str,
        current_metrics: StatisticalMetrics,
        historical_metrics: List[StatisticalMetrics]
    ) -> Optional[DriftAlert]:
        """Detect data drift by comparing current vs historical metrics"""
        if not historical_metrics:
            return None
        
        # Use median of recent historical values as baseline
        recent_history = historical_metrics[-10:]
        baseline_entropy = statistics.median([m.entropy for m in recent_history])
        baseline_null_pct = statistics.median([m.null_percentage for m in recent_history])
        
        # Calculate drift percentages
        drift_metrics = {}
        
        if baseline_entropy > 0:
            entropy_drift = abs((current_metrics.entropy - baseline_entropy) / baseline_entropy) * 100
            drift_metrics["entropy"] = (entropy_drift, baseline_entropy, current_metrics.entropy)
        
        if baseline_null_pct > 0:
            null_drift = abs((current_metrics.null_percentage - baseline_null_pct) / baseline_null_pct) * 100
            drift_metrics["null_percentage"] = (null_drift, baseline_null_pct, current_metrics.null_percentage)
        
        if not drift_metrics:
            return None
        
        # Find maximum drift
        max_metric = max(drift_metrics.items(), key=lambda x: x[1][0])
        metric_name = max_metric[0]
        drift_percentage, baseline_value, current_value = max_metric[1]
        
        # Determine severity
        severity = None
        if drift_percentage >= self.thresholds["critical"]:
            severity = "critical"
        elif drift_percentage >= self.thresholds["high"]:
            severity = "high"
        elif drift_percentage >= self.thresholds["medium"]:
            severity = "medium"
        elif drift_percentage >= self.thresholds["low"]:
            severity = "low"
        
        if severity:
            return DriftAlert(
                alert_id=f"{column_id}_{metric_name}_{datetime.utcnow().isoformat()}",
                column_id=column_id,
                metric_name=metric_name,
                previous_value=baseline_value,
                current_value=current_value,
                drift_percentage=drift_percentage,
                severity=severity,
                detected_at=datetime.utcnow()
            )
        
        return None
