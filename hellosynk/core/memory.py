"""
Memory Graph System - Structured memory for persistent context storage
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import networkx as nx
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Types of memory nodes"""
    ENTITY = "entity"  # Person, place, thing
    EVENT = "event"    # Something that happened
    CONCEPT = "concept"  # Abstract idea
    RELATIONSHIP = "relationship"  # Connection between entities
    TASK = "task"      # Action item
    CONTEXT = "context"  # Conversation context


class RelationshipType(str, Enum):
    """Types of relationships between nodes"""
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    CAUSED_BY = "caused_by"
    HAPPENED_BEFORE = "happened_before"
    INVOLVES = "involves"
    CREATED = "created"
    UPDATED = "updated"
    SIMILAR_TO = "similar_to"


@dataclass
class MemoryNode:
    """A node in the memory graph"""
    id: str
    type: NodeType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    importance: float = 0.5  # 0.0 to 1.0
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "importance": self.importance,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryNode":
        """Create node from dictionary"""
        node = cls(
            id=data["id"],
            type=NodeType(data["type"]),
            content=data["content"],
            metadata=data.get("metadata", {}),
            importance=data.get("importance", 0.5),
            access_count=data.get("access_count", 0),
        )
        node.created_at = datetime.fromisoformat(data["created_at"])
        node.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("last_accessed"):
            node.last_accessed = datetime.fromisoformat(data["last_accessed"])
        return node
    
    def access(self):
        """Mark node as accessed"""
        self.access_count += 1
        self.last_accessed = datetime.now()
    
    def update(self, content: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Update node content or metadata"""
        if content:
            self.content = content
        if metadata:
            self.metadata.update(metadata)
        self.updated_at = datetime.now()
    
    def __hash__(self) -> int:
        """Allow MemoryNode instances to be hashable based on their unique id"""
        return hash(self.id)


class MemoryGraph:
    """Graph-based memory system for storing and retrieving context"""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.nodes: Dict[str, MemoryNode] = {}
    
    def add_node(self, node: MemoryNode) -> None:
        """Add a node to the memory graph"""
        self.nodes[node.id] = node
        self.graph.add_node(
            node.id,
            type=node.type.value,
            content=node.content,
            metadata=node.metadata,
            importance=node.importance,
            access_count=node.access_count,
        )
    
    def get_node(self, node_id: str) -> Optional[MemoryNode]:
        """Get a node by ID"""
        node = self.nodes.get(node_id)
        if node:
            node.access()
        return node
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship: RelationshipType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a relationship between two nodes"""
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Both nodes must exist in the graph")
        
        self.graph.add_edge(
            source_id,
            target_id,
            relationship=relationship.value,
            metadata=metadata or {},
            created_at=datetime.now().isoformat(),
        )
    
    def find_nodes(
        self,
        query: Optional[str] = None,
        node_type: Optional[NodeType] = None,
        limit: int = 10
    ) -> List[MemoryNode]:
        """Find nodes by query or type"""
        results = []
        
        for node in self.nodes.values():
            # Filter by type if specified
            if node_type and node.type != node_type:
                continue
            
            # Filter by query if specified
            if query:
                if query.lower() not in node.content.lower():
                    continue
            
            results.append(node)
        
        # Sort by importance and access count
        results.sort(key=lambda n: (n.importance, n.access_count), reverse=True)
        return results[:limit]
    
    def get_related_nodes(self, node_id: str, depth: int = 1) -> List[MemoryNode]:
        """Get nodes related to a given node"""
        if node_id not in self.nodes:
            return []
        
        related_ids = set()
        if depth >= 1:
            # Direct neighbors
            related_ids.update(self.graph.successors(node_id))
            related_ids.update(self.graph.predecessors(node_id))
        
        if depth >= 2:
            # Two-hop neighbors
            for neighbor_id in list(related_ids):
                related_ids.update(self.graph.successors(neighbor_id))
                related_ids.update(self.graph.predecessors(neighbor_id))
        
        return [self.nodes[nid] for nid in related_ids if nid in self.nodes]
    
    def get_context(self, query: str, max_nodes: int = 20) -> List[MemoryNode]:
        """Get relevant context for a query"""
        # Find directly matching nodes
        matching_nodes = self.find_nodes(query=query, limit=max_nodes)
        
        # Get related nodes for each match
        context_nodes = set(matching_nodes)
        for node in matching_nodes:
            related = self.get_related_nodes(node.id, depth=1)
            context_nodes.update(related)
        
        # Sort by relevance (importance + recency)
        sorted_nodes = sorted(
            context_nodes,
            key=lambda n: (
                n.importance,
                n.access_count,
                (datetime.now() - n.updated_at).total_seconds()
            ),
            reverse=True
        )
        
        return list(sorted_nodes)[:max_nodes]
    
    def merge_nodes(self, source_id: str, target_id: str) -> None:
        """Merge two nodes, transferring relationships"""
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Both nodes must exist")
        
        source = self.nodes[source_id]
        target = self.nodes[target_id]
        
        # Merge content and metadata
        target.content = f"{target.content}\n\n{source.content}"
        target.metadata.update(source.metadata)
        target.importance = max(target.importance, source.importance)
        target.access_count += source.access_count
        
        # Transfer edges
        for pred_id in list(self.graph.predecessors(source_id)):
            for edge_data in self.graph[pred_id][source_id].values():
                self.add_edge(
                    pred_id,
                    target_id,
                    RelationshipType(edge_data["relationship"]),
                    edge_data.get("metadata", {})
                )
        
        for succ_id in list(self.graph.successors(source_id)):
            for edge_data in self.graph[source_id][succ_id].values():
                self.add_edge(
                    target_id,
                    succ_id,
                    RelationshipType(edge_data["relationship"]),
                    edge_data.get("metadata", {})
                )
        
        # Remove source node
        self.graph.remove_node(source_id)
        del self.nodes[source_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph to dictionary"""
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "relationship": data["relationship"],
                    "metadata": data.get("metadata", {}),
                }
                for source, target, data in self.graph.edges(data=True)
            ]
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Deserialize graph from dictionary"""
        self.graph.clear()
        self.nodes.clear()
        
        # Restore nodes
        for node_data in data.get("nodes", []):
            node = MemoryNode.from_dict(node_data)
            self.add_node(node)
        
        # Restore edges
        for edge_data in data.get("edges", []):
            self.add_edge(
                edge_data["source"],
                edge_data["target"],
                RelationshipType(edge_data["relationship"]),
                edge_data.get("metadata", {})
            )


