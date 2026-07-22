"""Knowledge graph module"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Node:
    """Represents a node in the knowledge graph"""

    id: str
    label: str
    properties: Dict[str, any]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "label": self.label,
            "properties": self.properties,
        }


@dataclass
class Edge:
    """Represents an edge in the knowledge graph"""

    id: str
    source: str
    target: str
    relationship: str
    properties: Dict[str, any]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "relationship": self.relationship,
            "properties": self.properties,
        }


@dataclass
class KnowledgeGraph:
    """Represents a knowledge graph"""

    nodes: List[Node]
    edges: List[Edge]

    def add_node(self, node: Node) -> None:
        """Add a node to the graph"""
        self.nodes.append(node)

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph"""
        self.edges.append(edge)

    def find_node(self, node_id: str) -> Optional[Node]:
        """Find a node by ID"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
