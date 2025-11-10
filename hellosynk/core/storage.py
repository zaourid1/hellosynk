"""
Local Storage Engine - Persistent storage for memory graph and configuration
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import aiosqlite
from datetime import datetime

from hellosynk.core.memory import MemoryGraph, MemoryNode, NodeType, RelationshipType


class Storage:
    """Local storage engine for HelloSynk data"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path.home() / ".hellosynk"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "hellosynk.db"
        self.memory_path = self.data_dir / "memory.json"
    
    async def initialize(self):
        """Initialize the database"""
        async with aiosqlite.connect(self.db_path) as db:
            # Memory nodes table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memory_nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    importance REAL NOT NULL,
                    access_count INTEGER NOT NULL,
                    last_accessed TEXT
                )
            """)
            
            # Memory edges table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memory_edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relationship TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (source_id) REFERENCES memory_nodes(id),
                    FOREIGN KEY (target_id) REFERENCES memory_nodes(id)
                )
            """)
            
            # Skills table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    version TEXT NOT NULL,
                    author TEXT,
                    enabled INTEGER NOT NULL,
                    config TEXT,
                    installed_at TEXT NOT NULL
                )
            """)
            
            # Execution history table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id TEXT PRIMARY KEY,
                    skill_id TEXT NOT NULL,
                    input_data TEXT NOT NULL,
                    output_data TEXT,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (skill_id) REFERENCES skills(id)
                )
            """)
            
            await db.commit()
    
    async def save_memory_graph(self, memory_graph: MemoryGraph):
        """Save memory graph to storage"""
        data = memory_graph.to_dict()
        
        # Save to JSON (backup)
        with open(self.memory_path, "w") as f:
            json.dump(data, f, indent=2)
        
        # Save to database
        async with aiosqlite.connect(self.db_path) as db:
            # Clear existing data
            await db.execute("DELETE FROM memory_edges")
            await db.execute("DELETE FROM memory_nodes")
            
            # Insert nodes
            for node_data in data["nodes"]:
                await db.execute("""
                    INSERT INTO memory_nodes 
                    (id, type, content, metadata, created_at, updated_at, importance, access_count, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    node_data["id"],
                    node_data["type"],
                    node_data["content"],
                    json.dumps(node_data["metadata"]),
                    node_data["created_at"],
                    node_data["updated_at"],
                    node_data["importance"],
                    node_data["access_count"],
                    node_data.get("last_accessed"),
                ))
            
            # Insert edges
            for edge_data in data["edges"]:
                await db.execute("""
                    INSERT INTO memory_edges (source_id, target_id, relationship, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    edge_data["source"],
                    edge_data["target"],
                    edge_data["relationship"],
                    json.dumps(edge_data.get("metadata", {})),
                    datetime.now().isoformat(),
                ))
            
            await db.commit()
    
    async def load_memory_graph(self) -> MemoryGraph:
        """Load memory graph from storage"""
        memory_graph = MemoryGraph()
        
        # Try to load from database first
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Load nodes
            async with db.execute("SELECT * FROM memory_nodes") as cursor:
                nodes_data = []
                async for row in cursor:
                    node_data = {
                        "id": row["id"],
                        "type": row["type"],
                        "content": row["content"],
                        "metadata": json.loads(row["metadata"]),
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                        "importance": row["importance"],
                        "access_count": row["access_count"],
                        "last_accessed": row["last_accessed"],
                    }
                    nodes_data.append(node_data)
            
            # Load edges
            async with db.execute("SELECT * FROM memory_edges") as cursor:
                edges_data = []
                async for row in cursor:
                    edge_data = {
                        "source": row["source_id"],
                        "target": row["target_id"],
                        "relationship": row["relationship"],
                        "metadata": json.loads(row["metadata"]),
                    }
                    edges_data.append(edge_data)
            
            if nodes_data:
                graph_data = {"nodes": nodes_data, "edges": edges_data}
                memory_graph.from_dict(graph_data)
        
        # Fallback to JSON if database is empty
        if not memory_graph.nodes and self.memory_path.exists():
            with open(self.memory_path, "r") as f:
                data = json.load(f)
                memory_graph.from_dict(data)
        
        return memory_graph
    
    async def save_skill_config(self, skill_id: str, config: Dict[str, Any]):
        """Save skill configuration"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE skills SET config = ? WHERE id = ?
            """, (json.dumps(config), skill_id))
            await db.commit()
    
    async def get_skill_config(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Get skill configuration"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT config FROM skills WHERE id = ?", (skill_id,)) as cursor:
                row = await cursor.fetchone()
                if row and row["config"]:
                    return json.loads(row["config"])
                return None
    
    async def log_execution(
        self,
        execution_id: str,
        skill_id: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]],
        status: str,
        error_message: Optional[str] = None
    ):
        """Log skill execution"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO executions 
                (id, skill_id, input_data, output_data, status, error_message, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_id,
                skill_id,
                json.dumps(input_data),
                json.dumps(output_data) if output_data else None,
                status,
                error_message,
                datetime.now().isoformat(),
            ))
            await db.commit()
    
    def get_config_path(self) -> Path:
        """Get path to configuration file"""
        return self.data_dir / "config.json"
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        config_path = self.get_config_path()
        if config_path.exists():
            with open(config_path, "r") as f:
                return json.load(f)
        return {}
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration"""
        config_path = self.get_config_path()
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

