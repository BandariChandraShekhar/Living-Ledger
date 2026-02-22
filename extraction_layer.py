"""Extraction Layer for connecting to data sources"""
import sqlite3
import random
from typing import List, Dict, Any
from models import DataSourceConfig, SchemaMetadata, DataSample


class ExtractionLayer:
    """Connects to data sources and extracts metadata"""
    
    def __init__(self):
        self.connection = None
        self.config = None
    
    async def connect(self, config: DataSourceConfig) -> bool:
        """Establish connection to data source"""
        try:
            self.config = config
            # For prototype, support SQLite
            if config.source_type == "sqlite":
                self.connection = sqlite3.connect(config.connection_string)
                return True
            else:
                raise ValueError(f"Unsupported source type: {config.source_type}")
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    async def list_tables(self) -> List[str]:
        """List all tables in the data source"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        return tables
    
    async def extract_ddl(self, table_names: List[str]) -> List[SchemaMetadata]:
        """Extract DDL schema information"""
        if not self.connection:
            return []
        
        schema_list = []
        cursor = self.connection.cursor()
        
        for table_name in table_names:
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                
                schema = SchemaMetadata(
                    table_name=table_name,
                    column_name=col_name,
                    data_type=col_type,
                    nullable=not not_null,
                    constraints=["PRIMARY KEY"] if pk else []
                )
                schema_list.append(schema)
        
        return schema_list
    
    async def sample_data(self, table_name: str, column_name: str) -> DataSample:
        """Sample data for statistical analysis (no PII storage)"""
        if not self.connection:
            return DataSample(table_name, column_name, [], 0)
        
        cursor = self.connection.cursor()
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]
        
        # Calculate sample size
        sample_size = min(
            int(total_count * self.config.sampling_rate),
            self.config.max_sample_size
        )
        
        # Sample data using random sampling
        cursor.execute(f"SELECT {column_name} FROM {table_name} ORDER BY RANDOM() LIMIT {sample_size}")
        sample_values = [row[0] for row in cursor.fetchall()]
        
        return DataSample(
            table_name=table_name,
            column_name=column_name,
            sample_values=sample_values,
            sample_size=len(sample_values)
        )
    
    async def get_table_context(self, table_name: str) -> Dict[str, Any]:
        """Get additional context about a table"""
        if not self.connection:
            return {}
        
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        return {
            "row_count": row_count,
            "table_name": table_name
        }
    
    async def disconnect(self) -> None:
        """Close connection to data source"""
        if self.connection:
            self.connection.close()
            self.connection = None
