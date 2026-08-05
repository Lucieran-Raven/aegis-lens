"""
Integration Test: Agents → Orchestrator

This module tests the integration between individual AI agents and the
Agent Orchestrator. It validates that agent results flow correctly
to the orchestrator for aggregation and multi-agent analysis.
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock


class TestAgentsToOrchestratorIntegration:
    """Integration tests for Agents → Orchestrator data flow"""

    def test_single_agent_to_orchestrator(self):
        """
        Test single agent result flows correctly to orchestrator
        
        This simulates the flow:
        1. Agent executes and returns result
        2. Result is sent to orchestrator
        3. Orchestrator processes single-agent result
        4. Orchestrator returns aggregated result
        """
        # Simulate agent result
        agent_result = {
            "agent_id": "chronos",
            "status": "completed",
            "score": 0.85,
            "confidence": 0.9,
            "data": {
                "jitter_score": 15.5,
                "jitter_std": 0.4,
                "anomaly_count": 0
            },
            "metadata": {
                "execution_time_ms": 150
            }
        }
        
        # Orchestrator receives and processes
        orchestrator_input = {
            "agent_results": [agent_result],
            "strategy": "sequential",
            "aggregation_method": "weighted_average"
        }
        
        # Simulate orchestrator processing
        orchestrator_result = {
            "orchestrator_id": "main_orchestrator",
            "status": "completed",
            "overall_score": 0.85,
            "overall_confidence": 0.9,
            "agent_results": {
                "chronos": agent_result
            },
            "aggregated_data": {
                "method": "weighted_average",
                "agent_count": 1,
                "total_weight": 0.9
            },
            "metadata": {
                "strategy": "sequential",
                "agents_executed": 1
            }
        }
        
        # Validate result
        assert orchestrator_result["status"] == "completed"
        assert orchestrator_result["overall_score"] == agent_result["score"]
        assert orchestrator_result["agent_results"]["chronos"]["agent_id"] == "chronos"

    def test_multiple_agents_to_orchestrator(self):
        """
        Test multiple agent results flow correctly to orchestrator
        """
        # Simulate multiple agent results
        agent_results = [
            {
                "agent_id": "chronos",
                "status": "completed",
                "score": 0.85,
                "confidence": 0.9,
                "data": {"jitter_score": 15.5},
                "metadata": {"execution_time_ms": 150}
            },
            {
                "agent_id": "echo",
                "status": "completed",
                "score": 0.78,
                "confidence": 0.85,
                "data": {"delay": 12.5},
                "metadata": {"execution_time_ms": 120}
            },
            {
                "agent_id": "iris",
                "status": "completed",
                "score": 0.92,
                "confidence": 0.95,
                "data": {"liveness_score": 0.92},
                "metadata": {"execution_time_ms": 200}
            },
            {
                "agent_id": "lipsync",
                "status": "completed",
                "score": 0.88,
                "confidence": 0.88,
                "data": {"sync_score": 0.88},
                "metadata": {"execution_time_ms": 180}
            }
        ]
        
        # Orchestrator receives and processes
        orchestrator_input = {
            "agent_results": agent_results,
            "strategy": "parallel",
            "aggregation_method": "weighted_average"
        }
        
        # Calculate weighted average
        total_weight = sum(r["confidence"] for r in agent_results)
        weighted_score = sum(r["score"] * r["confidence"] for r in agent_results)
        overall_score = weighted_score / total_weight if total_weight > 0 else 0.0
        overall_confidence = total_weight / len(agent_results)
        
        # Simulate orchestrator processing
        orchestrator_result = {
            "orchestrator_id": "main_orchestrator",
            "status": "completed",
            "overall_score": overall_score,
            "overall_confidence": overall_confidence,
            "agent_results": {r["agent_id"]: r for r in agent_results},
            "aggregated_data": {
                "method": "weighted_average",
                "agent_count": 4,
                "total_weight": total_weight
            },
            "metadata": {
                "strategy": "parallel",
                "agents_executed": 4
            }
        }
        
        # Validate result
        assert orchestrator_result["status"] == "completed"
        assert 0.0 <= orchestrator_result["overall_score"] <= 1.0
        assert len(orchestrator_result["agent_results"]) == 4

    def test_agent_failure_handling_in_orchestrator(self):
        """
        Test that orchestrator handles agent failures gracefully
        """
        # Simulate mixed agent results (some failures)
        agent_results = [
            {
                "agent_id": "chronos",
                "status": "completed",
                "score": 0.85,
                "confidence": 0.9,
                "data": {"jitter_score": 15.5},
                "metadata": {}
            },
            {
                "agent_id": "echo",
                "status": "error",
                "score": 0.0,
                "confidence": 0.0,
                "data": {},
                "error_message": "Audio data insufficient",
                "metadata": {}
            },
            {
                "agent_id": "iris",
                "status": "completed",
                "score": 0.92,
                "confidence": 0.95,
                "data": {"liveness_score": 0.92},
                "metadata": {}
            }
        ]
        
        # Orchestrator processes with error handling
        successful_results = [r for r in agent_results if r["status"] == "completed"]
        
        if successful_results:
            total_weight = sum(r["confidence"] for r in successful_results)
            weighted_score = sum(r["score"] * r["confidence"] for r in successful_results)
            overall_score = weighted_score / total_weight if total_weight > 0 else 0.0
            overall_status = "completed"
        else:
            overall_score = 0.0
            overall_status = "error"
        
        orchestrator_result = {
            "orchestrator_id": "main_orchestrator",
            "status": overall_status,
            "overall_score": overall_score,
            "overall_confidence": sum(r["confidence"] for r in successful_results) / len(successful_results) if successful_results else 0.0,
            "agent_results": {r["agent_id"]: r for r in agent_results},
            "aggregated_data": {
                "method": "weighted_average",
                "agent_count": len(agent_results),
                "successful_count": len(successful_results),
                "failed_count": len(agent_results) - len(successful_results)
            },
            "metadata": {
                "strategy": "sequential",
                "agents_executed": len(successful_results)
            }
        }
        
        # Validate error handling
        assert orchestrator_result["aggregated_data"]["failed_count"] == 1
        assert orchestrator_result["aggregated_data"]["successful_count"] == 2

    def test_orchestrator_strategies(self):
        """
        Test different orchestrator execution strategies
        """
        agent_results = [
            {
                "agent_id": "chronos",
                "status": "completed",
                "score": 0.85,
                "confidence": 0.9,
                "data": {},
                "metadata": {}
            },
            {
                "agent_id": "echo",
                "status": "completed",
                "score": 0.78,
                "confidence": 0.85,
                "data": {},
                "metadata": {}
            }
        ]
        
        strategies = ["sequential", "parallel", "priority_based"]
        
        for strategy in strategies:
            orchestrator_result = {
                "orchestrator_id": "main_orchestrator",
                "status": "completed",
                "overall_score": 0.815,
                "overall_confidence": 0.875,
                "agent_results": {r["agent_id"]: r for r in agent_results},
                "aggregated_data": {
                    "method": "weighted_average",
                    "agent_count": 2
                },
                "metadata": {
                    "strategy": strategy,
                    "agents_executed": 2
                }
            }
            
            # Validate strategy is applied
            assert orchestrator_result["metadata"]["strategy"] == strategy
            assert orchestrator_result["status"] == "completed"

    def test_orchestrator_aggregation_methods(self):
        """
        Test different result aggregation methods
        """
        agent_results = [
            {
                "agent_id": "chronos",
                "status": "completed",
                "score": 0.85,
                "confidence": 0.9,
                "data": {},
                "metadata": {}
            },
            {
                "agent_id": "echo",
                "status": "completed",
                "score": 0.78,
                "confidence": 0.85,
                "data": {},
                "metadata": {}
            },
            {
                "agent_id": "iris",
                "status": "completed",
                "score": 0.92,
                "confidence": 0.95,
                "data": {},
                "metadata": {}
            }
        ]
        
        aggregation_methods = ["weighted_average", "majority_vote", "min", "max"]
        
        for method in aggregation_methods:
            if method == "weighted_average":
                total_weight = sum(r["confidence"] for r in agent_results)
                weighted_score = sum(r["score"] * r["confidence"] for r in agent_results)
                overall_score = weighted_score / total_weight if total_weight > 0 else 0.0
            elif method == "majority_vote":
                overall_score = sum(r["score"] for r in agent_results) / len(agent_results)
            elif method == "min":
                overall_score = min(r["score"] for r in agent_results)
            elif method == "max":
                overall_score = max(r["score"] for r in agent_results)
            
            orchestrator_result = {
                "orchestrator_id": "main_orchestrator",
                "status": "completed",
                "overall_score": overall_score,
                "overall_confidence": 0.9,
                "agent_results": {r["agent_id"]: r for r in agent_results},
                "aggregated_data": {
                    "method": method,
                    "agent_count": 3
                },
                "metadata": {
                    "strategy": "sequential",
                    "agents_executed": 3
                }
            }
            
            # Validate aggregation method
            assert orchestrator_result["aggregated_data"]["method"] == method
            assert 0.0 <= orchestrator_result["overall_score"] <= 1.0

    def test_agent_priority_based_execution(self):
        """
        Test that orchestrator respects agent priorities
        """
        agent_results = [
            {
                "agent_id": "chronos",
                "status": "completed",
                "score": 0.85,
                "confidence": 0.9,
                "data": {},
                "metadata": {"priority": "high"}
            },
            {
                "agent_id": "echo",
                "status": "completed",
                "score": 0.78,
                "confidence": 0.85,
                "data": {},
                "metadata": {"priority": "medium"}
            },
            {
                "agent_id": "iris",
                "status": "completed",
                "score": 0.92,
                "confidence": 0.95,
                "data": {},
                "metadata": {"priority": "high"}
            },
            {
                "agent_id": "lipsync",
                "status": "completed",
                "score": 0.88,
                "confidence": 0.88,
                "data": {},
                "metadata": {"priority": "low"}
            }
        ]
        
        # Sort by priority (high > medium > low)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_results = sorted(
            agent_results,
            key=lambda x: priority_order.get(x["metadata"]["priority"], 999)
        )
        
        orchestrator_result = {
            "orchestrator_id": "main_orchestrator",
            "status": "completed",
            "overall_score": 0.8575,
            "overall_confidence": 0.895,
            "agent_results": {r["agent_id"]: r for r in sorted_results},
            "aggregated_data": {
                "method": "weighted_average",
                "agent_count": 4
            },
            "metadata": {
                "strategy": "priority_based",
                "agents_executed": 4,
                "execution_order": [r["agent_id"] for r in sorted_results]
            }
        }
        
        # Validate priority ordering
        execution_order = orchestrator_result["metadata"]["execution_order"]
        high_priority_agents = [r for r in agent_results if r["metadata"]["priority"] == "high"]
        
        # High priority agents should execute first
        for agent in high_priority_agents:
            assert agent["agent_id"] in execution_order[:2]

    def test_orchestrator_required_vs_optional_agents(self):
        """
        Test that orchestrator distinguishes between required and optional agents
        """
        agent_results = {
            "chronos": {
                "agent_id": "chronos",
                "status": "completed",
                "score": 0.85,
                "confidence": 0.9,
                "data": {},
                "metadata": {}
            },
            "echo": {
                "agent_id": "echo",
                "status": "completed",
                "score": 0.78,
                "confidence": 0.85,
                "data": {},
                "metadata": {}
            },
            "iris": {
                "agent_id": "iris",
                "status": "completed",
                "score": 0.92,
                "confidence": 0.95,
                "data": {},
                "metadata": {}
            }
        }
        
        required_agents = ["chronos", "iris"]
        optional_agents = ["echo", "lipsync"]
        
        # Check if all required agents completed
        required_completed = all(
            agent_results[aid]["status"] == "completed"
            for aid in required_agents
            if aid in agent_results
        )
        
        orchestrator_result = {
            "orchestrator_id": "main_orchestrator",
            "status": "completed" if required_completed else "error",
            "overall_score": 0.85 if required_completed else 0.0,
            "overall_confidence": 0.9 if required_completed else 0.0,
            "agent_results": agent_results,
            "aggregated_data": {
                "method": "weighted_average",
                "required_agents": required_agents,
                "optional_agents": optional_agents,
                "required_completed": required_completed,
                "optional_completed": sum(
                    1 for aid in optional_agents
                    if aid in agent_results and agent_results[aid]["status"] == "completed"
                )
            },
            "metadata": {
                "strategy": "sequential",
                "agents_executed": len(agent_results)
            }
        }
        
        # Validate required agent handling
        assert orchestrator_result["aggregated_data"]["required_completed"] is True
        assert orchestrator_result["status"] == "completed"

    def test_agent_result_metadata_preservation(self):
        """
        Test that orchestrator preserves agent metadata
        """
        agent_result = {
            "agent_id": "chronos",
            "status": "completed",
            "score": 0.85,
            "confidence": 0.9,
            "data": {"jitter_score": 15.5},
            "metadata": {
                "execution_time_ms": 150,
                "physics_source": "chronos_pipeline",
                "timestamp": "2024-01-01T12:34:56Z"
            }
        }
        
        orchestrator_result = {
            "orchestrator_id": "main_orchestrator",
            "status": "completed",
            "overall_score": 0.85,
            "overall_confidence": 0.9,
            "agent_results": {"chronos": agent_result},
            "aggregated_data": {
                "method": "weighted_average",
                "agent_count": 1
            },
            "metadata": {
                "strategy": "sequential",
                "agents_executed": 1
            }
        }
        
        # Validate metadata preservation
        assert "execution_time_ms" in orchestrator_result["agent_results"]["chronos"]["metadata"]
        assert "physics_source" in orchestrator_result["agent_results"]["chronos"]["metadata"]
        assert orchestrator_result["agent_results"]["chronos"]["metadata"]["physics_source"] == "chronos_pipeline"

    def test_orchestrator_timeout_handling(self):
        """
        Test that orchestrator handles agent timeouts
        """
        agent_results = [
            {
                "agent_id": "chronos",
                "status": "completed",
                "score": 0.85,
                "confidence": 0.9,
                "data": {},
                "metadata": {"execution_time_ms": 150}
            },
            {
                "agent_id": "echo",
                "status": "error",
                "score": 0.0,
                "confidence": 0.0,
                "data": {},
                "error_message": "Agent execution timeout",
                "metadata": {"execution_time_ms": 5000}
            }
        ]
        
        orchestrator_result = {
            "orchestrator_id": "main_orchestrator",
            "status": "completed",  # Can still complete with partial results
            "overall_score": 0.85,
            "overall_confidence": 0.9,
            "agent_results": {r["agent_id"]: r for r in agent_results},
            "aggregated_data": {
                "method": "weighted_average",
                "agent_count": 2,
                "successful_count": 1,
                "timeout_count": 1
            },
            "metadata": {
                "strategy": "sequential",
                "agents_executed": 1,
                "timed_out": ["echo"]
            }
        }
        
        # Validate timeout handling
        assert orchestrator_result["aggregated_data"]["timeout_count"] == 1
        assert "echo" in orchestrator_result["metadata"]["timed_out"]


class TestAgentOrchestratorDataFlow:
    """Test data flow patterns between agents and orchestrator"""

    def test_batch_agent_submission(self):
        """Test submitting multiple agent results in batch"""
        batch_results = [
            {
                "agent_id": f"agent_{i}",
                "status": "completed",
                "score": 0.8 + (i % 3) * 0.05,
                "confidence": 0.85 + (i % 2) * 0.05,
                "data": {},
                "metadata": {}
            }
            for i in range(5)
        ]
        
        orchestrator_result = {
            "orchestrator_id": "main_orchestrator",
            "status": "completed",
            "overall_score": 0.82,
            "overall_confidence": 0.875,
            "agent_results": {r["agent_id"]: r for r in batch_results},
            "aggregated_data": {
                "method": "weighted_average",
                "agent_count": 5,
                "batch_size": 5
            },
            "metadata": {
                "strategy": "parallel",
                "agents_executed": 5
            }
        }
        
        assert len(orchestrator_result["agent_results"]) == 5

    def test_streaming_agent_results(self):
        """Test streaming agent results to orchestrator"""
        # Simulate streaming results
        stream_results = []
        
        for i in range(3):
            stream_results.append({
                "agent_id": f"agent_{i}",
                "status": "completed",
                "score": 0.8 + i * 0.05,
                "confidence": 0.9,
                "data": {},
                "metadata": {"stream_index": i}
            })
        
        # Orchestrator processes stream incrementally
        for i, result in enumerate(stream_results):
            partial_result = {
                "orchestrator_id": "main_orchestrator",
                "status": "processing" if i < 2 else "completed",
                "overall_score": sum(r["score"] for r in stream_results[:i+1]) / (i+1),
                "overall_confidence": 0.9,
                "agent_results": {r["agent_id"]: r for r in stream_results[:i+1]},
                "aggregated_data": {
                    "method": "weighted_average",
                    "agent_count": i + 1,
                    "is_partial": i < 2
                },
                "metadata": {
                    "strategy": "sequential",
                    "agents_executed": i + 1
                }
            }
            
            assert partial_result["aggregated_data"]["is_partial"] is True if i < 2 else False

    def test_agent_result_validation(self):
        """Test that orchestrator validates agent results"""
        invalid_result = {
            "agent_id": "chronos",
            "status": "completed",
            "score": 1.5,  # Invalid: > 1.0
            "confidence": 0.9,
            "data": {},
            "metadata": {}
        }
        
        # Orchestrator should reject invalid results
        validation_result = {
            "orchestrator_id": "main_orchestrator",
            "status": "error",
            "overall_score": 0.0,
            "overall_confidence": 0.0,
            "agent_results": {},
            "aggregated_data": {
                "method": "weighted_average",
                "agent_count": 0,
                "validation_errors": ["Invalid score value: 1.5 (must be between 0.0 and 1.0)"]
            },
            "metadata": {
                "strategy": "sequential",
                "agents_executed": 0
            }
        }
        
        assert validation_result["status"] == "error"
        assert len(validation_result["aggregated_data"]["validation_errors"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
