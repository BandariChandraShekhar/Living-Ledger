"""Main orchestration for The Living Ledger"""
from datetime import datetime
from typing import Dict, Any, List
from models import (
    DataSourceConfig, MetadataEntity, CertificationStatus
)
from extraction_layer import ExtractionLayer
from statistical_engine import StatisticalEngine
from llm_service import LLMEnrichmentService
from shadow_layer import SemanticShadowLayer


class LivingLedger:
    """Main orchestrator for The Living Ledger platform"""
    
    def __init__(self, gemini_api_key: str = None):
        self.extraction_layer = ExtractionLayer()
        self.statistical_engine = StatisticalEngine()
        self.llm_service = LLMEnrichmentService(gemini_api_key)
        self.shadow_layer = SemanticShadowLayer()
    
    async def process_data_source(self, config: DataSourceConfig) -> Dict[str, Any]:
        """Process a data source through the entire TLL pipeline"""
        results = {
            "entities_created": 0,
            "entities_updated": 0,
            "drift_alerts": [],
            "errors": []
        }
        
        try:
            # Step 1: Connect to data source
            connected = await self.extraction_layer.connect(config)
            if not connected:
                results["errors"].append("Failed to connect to data source")
                return results
            
            # Step 2: Extract DDL for all tables
            all_tables = await self.extraction_layer.list_tables()
            print(f"Found {len(all_tables)} tables: {all_tables}")
            
            schema_metadata_list = await self.extraction_layer.extract_ddl(all_tables)
            print(f"Extracted {len(schema_metadata_list)} columns")
            
            # Step 3: Process each column
            for schema_meta in schema_metadata_list:
                try:
                    # Sample data for this column
                    sample = await self.extraction_layer.sample_data(
                        schema_meta.table_name,
                        schema_meta.column_name
                    )
                    
                    # Calculate statistical metrics
                    stats = await self.statistical_engine.calculate_metrics(sample)
                    
                    # Check for drift against historical data
                    historical = await self.shadow_layer.get_historical_metrics(
                        f"{schema_meta.table_name}.{schema_meta.column_name}"
                    )
                    
                    if historical:
                        drift_alert = await self.statistical_engine.detect_drift(
                            column_id=f"{schema_meta.table_name}.{schema_meta.column_name}",
                            current_metrics=stats,
                            historical_metrics=historical
                        )
                        if drift_alert:
                            await self.shadow_layer.add_drift_alert(drift_alert)
                            results["drift_alerts"].append(drift_alert)
                    
                    # Generate semantic description via LLM
                    table_context = await self.extraction_layer.get_table_context(
                        schema_meta.table_name
                    )
                    
                    semantic_desc = await self.llm_service.generate_description(
                        schema_meta, stats, table_context
                    )
                    
                    # Create or update metadata entity
                    entity = MetadataEntity(
                        entity_id=f"{schema_meta.table_name}.{schema_meta.column_name}",
                        schema_metadata=schema_meta,
                        statistical_metrics=stats,
                        semantic_description=semantic_desc,
                        certification_status=CertificationStatus.UNCERTIFIED,
                        version=1,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    existing = await self.shadow_layer.get_entity(entity.entity_id)
                    if existing:
                        results["entities_updated"] += 1
                    else:
                        results["entities_created"] += 1
                    
                    await self.shadow_layer.upsert_entity(entity)
                    
                    # Discard sample data (privacy-first)
                    del sample
                    
                except Exception as e:
                    results["errors"].append(f"Error processing {schema_meta.table_name}.{schema_meta.column_name}: {str(e)}")
            
            # Step 4: Cleanup
            await self.extraction_layer.disconnect()
            
            return results
            
        except Exception as e:
            results["errors"].append(f"Pipeline error: {str(e)}")
            await self.extraction_layer.disconnect()
            return results
    
    async def search(self, query: str, limit: int = 10) -> List[MetadataEntity]:
        """Search for metadata entities"""
        return await self.shadow_layer.search_entities(query, limit)
    
    async def certify(self, entity_id: str, user_id: str, notes: str = None) -> bool:
        """Certify a metadata entity"""
        return await self.shadow_layer.certify_entity(entity_id, user_id, notes)
    
    async def uncertify(self, entity_id: str, user_id: str, notes: str = None) -> bool:
        """Uncertify a metadata entity"""
        return await self.shadow_layer.uncertify_entity(entity_id, user_id, notes)
    
    async def deny(self, entity_id: str, user_id: str, notes: str = None) -> bool:
        """Deny a metadata entity"""
        return await self.shadow_layer.deny_entity(entity_id, user_id, notes)
    
    async def create_entity(
        self,
        table_name: str,
        column_name: str,
        data_type: str,
        business_name: str,
        description: str,
        business_domain: str,
        nullable: bool = True
    ) -> str:
        """Manually create a new metadata entity"""
        from models import SchemaMetadata, SemanticDescription, StatisticalMetrics
        
        # Create schema metadata
        schema_meta = SchemaMetadata(
            table_name=table_name,
            column_name=column_name,
            data_type=data_type,
            nullable=nullable,
            constraints=[]
        )
        
        # Create semantic description
        semantic_desc = SemanticDescription(
            column_id=f"{table_name}.{column_name}",
            business_name=business_name,
            description=description,
            business_domain=business_domain,
            example_values=[],
            usage_guidelines="Manually created entity",
            confidence_score=1.0,
            generated_at=datetime.utcnow()
        )
        
        # Create default statistics
        stats = StatisticalMetrics(
            column_id=f"{table_name}.{column_name}",
            mean=None,
            std_dev=None,
            entropy=0.0,
            distinct_count=0,
            null_percentage=0.0,
            distribution_type="unknown",
            calculated_at=datetime.utcnow(),
            min_value=None,
            max_value=None
        )
        
        # Create entity
        entity = MetadataEntity(
            entity_id=f"{table_name}.{column_name}",
            schema_metadata=schema_meta,
            statistical_metrics=stats,
            semantic_description=semantic_desc,
            certification_status=CertificationStatus.UNCERTIFIED,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await self.shadow_layer.upsert_entity(entity)
        return entity.entity_id
    
    async def get_entity(self, entity_id: str) -> MetadataEntity:
        """Get a specific metadata entity"""
        return await self.shadow_layer.get_entity(entity_id)
    
    async def get_all_entities(self) -> List[MetadataEntity]:
        """Get all metadata entities"""
        return await self.shadow_layer.get_all_entities()
    
    async def get_drift_alerts(self, severity: str = None) -> List:
        """Get drift alerts"""
        return await self.shadow_layer.get_drift_alerts(severity)
    
    async def acknowledge_alert(self, alert_id: str, user_id: str, notes: str = None) -> bool:
        """Acknowledge a drift alert"""
        return await self.shadow_layer.acknowledge_alert(alert_id, user_id, notes)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get platform statistics"""
        return await self.shadow_layer.get_stats()
