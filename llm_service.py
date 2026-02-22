"""LLM Enrichment Service (Mock for prototype)"""
from datetime import datetime
from typing import Dict, Any
from models import SchemaMetadata, StatisticalMetrics, SemanticDescription


class LLMEnrichmentService:
    """Generates business-friendly descriptions (Mock implementation)"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.model_version = "mock-v1.0"
    
    async def generate_description(
        self,
        schema_metadata: SchemaMetadata,
        statistical_metrics: StatisticalMetrics,
        table_context: Dict[str, Any]
    ) -> SemanticDescription:
        """Generate business-friendly description from technical metadata"""
        
        # Mock LLM generation - in production, this would call Gemini API
        business_name = self._humanize_column_name(schema_metadata.column_name)
        description = self._generate_mock_description(
            schema_metadata, statistical_metrics, table_context
        )
        business_domain = self._infer_domain(schema_metadata.column_name, schema_metadata.data_type)
        
        # Get example values from stats
        example_values = []
        if statistical_metrics.min_value is not None:
            example_values.append(str(statistical_metrics.min_value))
        if statistical_metrics.max_value is not None and statistical_metrics.max_value != statistical_metrics.min_value:
            example_values.append(str(statistical_metrics.max_value))
        
        if not example_values:
            example_values = ["N/A"]
        
        usage_guidelines = self._generate_usage_guidelines(schema_metadata, statistical_metrics)
        
        # Calculate confidence score based on data quality
        confidence_score = self._calculate_confidence(statistical_metrics)
        
        return SemanticDescription(
            column_id=f"{schema_metadata.table_name}.{schema_metadata.column_name}",
            business_name=business_name,
            description=description,
            business_domain=business_domain,
            example_values=example_values[:5],
            usage_guidelines=usage_guidelines,
            confidence_score=confidence_score,
            generated_at=datetime.utcnow()
        )
    
    def _humanize_column_name(self, column_name: str) -> str:
        """Convert technical column name to human-readable format"""
        # Remove common prefixes
        name = column_name.replace('tbl_', '').replace('col_', '').replace('fld_', '')
        
        # Replace underscores with spaces and title case
        name = name.replace('_', ' ').title()
        
        return name
    
    def _generate_mock_description(
        self,
        schema: SchemaMetadata,
        metrics: StatisticalMetrics,
        context: Dict[str, Any]
    ) -> str:
        """Generate a mock description based on metadata"""
        data_type = schema.data_type.upper()
        nullable = "optional" if schema.nullable else "required"
        
        description = f"This is a {nullable} {data_type} field in the {schema.table_name} table. "
        
        if metrics.distinct_count > 0:
            description += f"It contains {metrics.distinct_count} distinct values. "
        
        if metrics.null_percentage > 0:
            description += f"Approximately {metrics.null_percentage:.1f}% of values are null. "
        
        if metrics.mean is not None:
            description += f"The average value is {metrics.mean:.2f}. "
        
        description += f"Data distribution appears to be {metrics.distribution_type}."
        
        return description
    
    def _infer_domain(self, column_name: str, data_type: str) -> str:
        """Infer business domain from column name and type"""
        name_lower = column_name.lower()
        
        if any(x in name_lower for x in ['email', 'mail']):
            return "Contact Information"
        elif any(x in name_lower for x in ['phone', 'mobile', 'tel']):
            return "Contact Information"
        elif any(x in name_lower for x in ['price', 'cost', 'amount', 'revenue', 'salary']):
            return "Financial"
        elif any(x in name_lower for x in ['date', 'time', 'created', 'updated']):
            return "Temporal"
        elif any(x in name_lower for x in ['name', 'title', 'description']):
            return "Descriptive"
        elif any(x in name_lower for x in ['id', 'key', 'code']):
            return "Identifier"
        elif any(x in name_lower for x in ['status', 'state', 'flag']):
            return "Status"
        else:
            return "General"
    
    def _generate_usage_guidelines(
        self,
        schema: SchemaMetadata,
        metrics: StatisticalMetrics
    ) -> str:
        """Generate usage guidelines based on metadata"""
        guidelines = []
        
        if not schema.nullable:
            guidelines.append("This field is required and must not be null.")
        
        if metrics.null_percentage > 50:
            guidelines.append("Warning: High percentage of null values. Use with caution.")
        
        if metrics.distinct_count == 1:
            guidelines.append("This field has only one distinct value. Consider if it's still needed.")
        
        if metrics.entropy < 1.0 and metrics.distinct_count > 1:
            guidelines.append("Low entropy indicates limited variability in values.")
        
        if not guidelines:
            guidelines.append("Standard usage applies. Refer to data dictionary for details.")
        
        return " ".join(guidelines)
    
    def _calculate_confidence(self, metrics: StatisticalMetrics) -> float:
        """Calculate confidence score based on data quality"""
        score = 1.0
        
        # Reduce confidence for high null percentage
        if metrics.null_percentage > 50:
            score -= 0.3
        elif metrics.null_percentage > 25:
            score -= 0.1
        
        # Reduce confidence for very low entropy
        if metrics.entropy < 0.5:
            score -= 0.2
        
        # Reduce confidence for single value
        if metrics.distinct_count == 1:
            score -= 0.3
        
        return max(0.0, min(1.0, score))
