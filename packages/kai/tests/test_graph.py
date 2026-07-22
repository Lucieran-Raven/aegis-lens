"""Tests for graph module"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from graph import Node, Edge, KnowledgeGraph


def test_node_creation():
    """Test node creation"""
    node = Node(id="1", label="Person", properties={"name": "John"})
    assert node.id == "1"
    assert node.label == "Person"


def test_node_to_dict():
    """Test node to dictionary"""
    node = Node(id="1", label="Person", properties={"name": "John"})
    data = node.to_dict()
    assert data["id"] == "1"
    assert data["label"] == "Person"


def test_edge_creation():
    """Test edge creation"""
    edge = Edge(id="1", source="1", target="2", relationship="KNOWS", properties={})
    assert edge.source == "1"
    assert edge.target == "2"


def test_knowledge_graph():
    """Test knowledge graph operations"""
    graph = KnowledgeGraph(nodes=[], edges=[])
    node = Node(id="1", label="Person", properties={"name": "John"})
    graph.add_node(node)
    assert len(graph.nodes) == 1
    assert graph.find_node("1") == node
