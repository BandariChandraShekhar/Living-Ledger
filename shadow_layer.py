"""Semantic Shadow Layer - Digital Twin of Metadata"""
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import sqlite3
from models import MetadataEntity, CertificationStatus, StatisticalMetrics, DriftAlert


class SemanticShadowLayer:
    """Maintains the real-time digital twin of metadata"""
    
    def __init__(self, db_path: str = "living_ledger.db"):
        self.db_path = db_path
        self.drift_alerts: List[DriftAlert] = []  # Keep alerts in memory for now
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables for entities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metadata_entities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata_entities (
                entity_id TEXT PRIMARY KEY,
                entity_data TEXT NOT NULL,
                certification_status TEXT DEFAULT 'uncertified',
                certified_by TEXT,
                certified_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                version INTEGER DEFAULT 1
            )
        ''')
        
        # Create historical_metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                column_id TEXT NOT NULL,
                metrics_data TEXT NOT NULL,
                calculated_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    async def upsert_entity(self, entity: MetadataEntity) -> str:
        """Create or update metadata entity"""
        entity_id = entity.entity_id
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if entity exists
        cursor.execute("SELECT version FROM metadata_entities WHERE entity_id = ?", (entity_id,))
        existing = cursor.fetchone()
        
        if existing:
            entity.version = existing['version'] + 1
            entity.updated_at = datetime.utcnow()
        else:
            entity.created_at = datetime.utcnow()
            entity.updated_at = datetime.utcnow()
        
        # Serialize entity to JSON
        entity_data = {
            "entity_id": entity.entity_id,
            "schema_metadata": {
                "table_name": entity.schema_metadata.table_name,
                "column_name": entity.schema_metadata.column_name,
                "data_type": entity.schema_metadata.data_type,
                "nullable": entity.schema_metadata.nullable,
                "constraints": entity.schema_metadata.constraints
            },
            "statistical_metrics": {
                "column_id": entity.statistical_metrics.column_id,
                "mean": entity.statistical_metrics.mean,
                "std_dev": entity.statistical_metrics.std_dev,
                "entropy": entity.statistical_metrics.entropy,
                "distinct_count": entity.statistical_metrics.distinct_count,
                "null_percentage": entity.statistical_metrics.null_percentage,
                "distribution_type": entity.statistical_metrics.distribution_type,
                "min_value": entity.statistical_metrics.min_value,
                "max_value": entity.statistical_metrics.max_value,
                "calculated_at": entity.statistical_metrics.calculated_at.isoformat()
            },
            "semantic_description": {
                "column_id": entity.semantic_description.column_id,
                "business_name": entity.semantic_description.business_name,
                "description": entity.semantic_description.description,
                "business_domain": entity.semantic_description.business_domain,
                "example_values": entity.semantic_description.example_values,
                "usage_guidelines": entity.semantic_description.usage_guidelines,
                "confidence_score": entity.semantic_description.confidence_score,
                "generated_at": entity.semantic_description.generated_at.isoformat()
            }
        }
        
        # Store entity
        cursor.execute('''
            INSERT OR REPLACE INTO metadata_entities 
            (entity_id, entity_data, certification_status, certified_by, certified_at, created_at, updated_at, version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entity_id,
            json.dumps(entity_data),
            entity.certification_status.value,
            entity.certified_by,
            entity.certified_at.isoformat() if entity.certified_at else None,
            entity.created_at.isoformat(),
            entity.updated_at.isoformat(),
            entity.version
        ))
        
        # Store historical metrics
        metrics_data = {
            "mean": entity.statistical_metrics.mean,
            "std_dev": entity.statistical_metrics.std_dev,
            "entropy": entity.statistical_metrics.entropy,
            "distinct_count": entity.statistical_metrics.distinct_count,
            "null_percentage": entity.statistical_metrics.null_percentage,
            "distribution_type": entity.statistical_metrics.distribution_type,
            "min_value": entity.statistical_metrics.min_value,
            "max_value": entity.statistical_metrics.max_value
        }
        
        cursor.execute('''
            INSERT INTO historical_metrics (column_id, metrics_data, calculated_at)
            VALUES (?, ?, ?)
        ''', (
            entity_id,
            json.dumps(metrics_data),
            entity.statistical_metrics.calculated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return entity_id
    
    async def get_entity(self, entity_id: str) -> Optional[MetadataEntity]:
        """Retrieve metadata entity by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM metadata_entities WHERE entity_id = ?", (entity_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_entity(row)
    
    def _row_to_entity(self, row) -> MetadataEntity:
        """Convert database row to MetadataEntity"""
        from models import SchemaMetadata, SemanticDescription
        
        entity_data = json.loads(row['entity_data'])
        
        # Reconstruct schema metadata
        schema_meta = SchemaMetadata(
            table_name=entity_data['schema_metadata']['table_name'],
            column_name=entity_data['schema_metadata']['column_name'],
            data_type=entity_data['schema_metadata']['data_type'],
            nullable=entity_data['schema_metadata']['nullable'],
            constraints=entity_data['schema_metadata']['constraints']
        )
        
        # Reconstruct statistical metrics
        stats_data = entity_data['statistical_metrics']
        stats = StatisticalMetrics(
            column_id=stats_data['column_id'],
            mean=stats_data['mean'],
            std_dev=stats_data['std_dev'],
            entropy=stats_data['entropy'],
            distinct_count=stats_data['distinct_count'],
            null_percentage=stats_data['null_percentage'],
            distribution_type=stats_data['distribution_type'],
            min_value=stats_data['min_value'],
            max_value=stats_data['max_value'],
            calculated_at=datetime.fromisoformat(stats_data['calculated_at'])
        )
        
        # Reconstruct semantic description
        sem_data = entity_data['semantic_description']
        semantic_desc = SemanticDescription(
            column_id=sem_data['column_id'],
            business_name=sem_data['business_name'],
            description=sem_data['description'],
            business_domain=sem_data['business_domain'],
            example_values=sem_data['example_values'],
            usage_guidelines=sem_data['usage_guidelines'],
            confidence_score=sem_data['confidence_score'],
            generated_at=datetime.fromisoformat(sem_data['generated_at'])
        )
        
        # Reconstruct entity
        entity = MetadataEntity(
            entity_id=row['entity_id'],
            schema_metadata=schema_meta,
            statistical_metrics=stats,
            semantic_description=semantic_desc,
            certification_status=CertificationStatus(row['certification_status']),
            version=row['version'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            certified_by=row['certified_by'],
            certified_at=datetime.fromisoformat(row['certified_at']) if row['certified_at'] else None
        )
        
        return entity
    
    async def get_all_entities(self) -> List[MetadataEntity]:
        """Get all metadata entities"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM metadata_entities ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_entity(row) for row in rows]
    
    async def search_entities(self, query: str, limit: int = 10) -> List[MetadataEntity]:
        """Simple keyword search across metadata entities"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query_lower = query.lower()
        cursor.execute("SELECT * FROM metadata_entities")
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            entity = self._row_to_entity(row)
            # Search in business name and description
            if (query_lower in entity.semantic_description.business_name.lower() or
                query_lower in entity.semantic_description.description.lower() or
                query_lower in entity.schema_metadata.table_name.lower() or
                query_lower in entity.schema_metadata.column_name.lower()):
                results.append(entity)
            
            if len(results) >= limit:
                break
        
        return results
    
    async def certify_entity(
        self,
        entity_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """Mark entity as certified by user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE metadata_entities 
            SET certification_status = ?, certified_by = ?, certified_at = ?, updated_at = ?
            WHERE entity_id = ?
        ''', (
            CertificationStatus.CERTIFIED.value,
            user_id,
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat(),
            entity_id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    async def uncertify_entity(
        self,
        entity_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """Mark entity as uncertified"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE metadata_entities 
            SET certification_status = ?, certified_by = NULL, certified_at = NULL, updated_at = ?
            WHERE entity_id = ?
        ''', (
            CertificationStatus.UNCERTIFIED.value,
            datetime.utcnow().isoformat(),
            entity_id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    async def deny_entity(
        self,
        entity_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """Mark entity as denied"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE metadata_entities 
            SET certification_status = ?, certified_by = ?, certified_at = ?, updated_at = ?
            WHERE entity_id = ?
        ''', (
            CertificationStatus.DENIED.value,
            user_id,
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat(),
            entity_id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    async def get_historical_metrics(self, column_id: str) -> List[StatisticalMetrics]:
        """Get historical metrics for a column"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT metrics_data, calculated_at 
            FROM historical_metrics 
            WHERE column_id = ?
            ORDER BY calculated_at DESC
        ''', (column_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        metrics_list = []
        for row in rows:
            metrics_data = json.loads(row['metrics_data'])
            metrics = StatisticalMetrics(
                column_id=column_id,
                mean=metrics_data['mean'],
                std_dev=metrics_data['std_dev'],
                entropy=metrics_data['entropy'],
                distinct_count=metrics_data['distinct_count'],
                null_percentage=metrics_data['null_percentage'],
                distribution_type=metrics_data['distribution_type'],
                min_value=metrics_data['min_value'],
                max_value=metrics_data['max_value'],
                calculated_at=datetime.fromisoformat(row['calculated_at'])
            )
            metrics_list.append(metrics)
        
        return metrics_list
    
    async def add_drift_alert(self, alert: DriftAlert) -> None:
        """Add a drift alert"""
        self.drift_alerts.append(alert)
    
    async def get_drift_alerts(self, severity: Optional[str] = None) -> List[DriftAlert]:
        """Retrieve active drift alerts"""
        if severity:
            return [a for a in self.drift_alerts if a.severity == severity and not a.acknowledged]
        return [a for a in self.drift_alerts if not a.acknowledged]
    
    async def acknowledge_alert(
        self,
        alert_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """Acknowledge a drift alert"""
        for alert in self.drift_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = user_id
                alert.acknowledged_at = datetime.utcnow()
                alert.resolution_notes = notes
                return True
        return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the shadow layer"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total entities
        cursor.execute("SELECT COUNT(*) as count FROM metadata_entities")
        total_entities = cursor.fetchone()['count']
        
        # Certified
        cursor.execute("SELECT COUNT(*) as count FROM metadata_entities WHERE certification_status = ?", 
                      (CertificationStatus.CERTIFIED.value,))
        certified = cursor.fetchone()['count']
        
        # Uncertified
        cursor.execute("SELECT COUNT(*) as count FROM metadata_entities WHERE certification_status = ?", 
                      (CertificationStatus.UNCERTIFIED.value,))
        uncertified = cursor.fetchone()['count']
        
        conn.close()
        
        active_alerts = len([a for a in self.drift_alerts if not a.acknowledged])
        
        return {
            "total_entities": total_entities,
            "certified": certified,
            "uncertified": uncertified,
            "pending_review": total_entities - certified - uncertified,
            "active_drift_alerts": active_alerts,
            "total_alerts": len(self.drift_alerts)
        }
