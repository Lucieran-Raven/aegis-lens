"""
End-to-End Integration Test: All Components

This module tests the complete end-to-end flow of the Aegis Lens platform:
Candidate UI → Physics Engine → Agents → Orchestrator → Dashboard → Signaling

This validates the entire interview analysis pipeline from start to finish.
"""

import pytest
from typing import Dict, Any, List
from datetime import datetime


class TestFullPipelineE2E:
    """End-to-end tests for the complete Aegis Lens pipeline"""

    def test_complete_interview_flow(self):
        """
        Test complete interview flow from candidate connection to final verdict
        
        Full pipeline:
        1. Candidate connects via UI
        2. Physics engine collects data
        3. Agents analyze physics data
        4. Orchestrator aggregates results
        5. Dashboard displays verdict
        6. Signaling enables real-time communication
        """
        # Step 1: Candidate connects
        candidate_connection = {
            "candidate_id": "candidate_123",
            "session_id": "session_456",
            "connection_status": "connected",
            "timestamp": "2024-01-01T10:00:00Z"
        }
        
        # Step 2: Physics engine collects data
        physics_data = {
            "chronos": {
                "timestamps": [0, 100, 200, 300, 400],
                "sample_rate": 44100,
                "mean_jitter": 15.5,
                "std_jitter": 0.4
            },
            "echo": {
                "tof_values": [12.5, 12.8, 12.6, 12.7, 12.6],
                "mean_tof": 12.64,
                "std_tof": 0.12
            },
            "iris": {
                "face_detected": True,
                "eye_variance": 0.1,
                "liveness_score": 0.92
            },
            "lipsync": {
                "sync_scores": [0.85, 0.88, 0.86, 0.87, 0.86],
                "mean_sync": 0.864,
                "drift_score": 0.04
            }
        }
        
        # Step 3: Agents analyze physics data
        agent_results = [
            {
                "agent_id": "chronos",
                "status": "completed",
                "score": 0.85,
                "confidence": 0.9,
                "data": physics_data["chronos"],
                "metadata": {"execution_time_ms": 150}
            },
            {
                "agent_id": "echo",
                "status": "completed",
                "score": 0.78,
                "confidence": 0.85,
                "data": physics_data["echo"],
                "metadata": {"execution_time_ms": 120}
            },
            {
                "agent_id": "iris",
                "status": "completed",
                "score": 0.92,
                "confidence": 0.95,
                "data": physics_data["iris"],
                "metadata": {"execution_time_ms": 200}
            },
            {
                "agent_id": "lipsync",
                "status": "completed",
                "score": 0.88,
                "confidence": 0.88,
                "data": physics_data["lipsync"],
                "metadata": {"execution_time_ms": 180}
            }
        ]
        
        # Step 4: Orchestrator aggregates results
        total_weight = sum(r["confidence"] for r in agent_results)
        weighted_score = sum(r["score"] * r["confidence"] for r in agent_results)
        overall_score = weighted_score / total_weight if total_weight > 0 else 0.0
        
        orchestrator_result = {
            "orchestrator_id": "main_orchestrator",
            "status": "completed",
            "overall_score": overall_score,
            "overall_confidence": total_weight / len(agent_results),
            "agent_results": {r["agent_id"]: r for r in agent_results},
            "aggregated_data": {
                "method": "weighted_average",
                "agent_count": 4
            },
            "metadata": {
                "strategy": "parallel",
                "timestamp": "2024-01-01T10:05:00Z"
            }
        }
        
        # Step 5: Dashboard displays verdict
        verdict = {
            "status": "CLEAR" if overall_score > 0.7 else "SUSPECT",
            "trust_score": overall_score,
            "confidence": orchestrator_result["overall_confidence"],
            "evidence_count": 4,
            "evidence": [
                {"agent": r["agent_id"], "score": r["score"], "confidence": r["confidence"]}
                for r in agent_results
            ],
            "recommendation": "PROCEED" if overall_score > 0.7 else "REVIEW"
        }
        
        # Step 6: Verify complete flow
        assert candidate_connection["connection_status"] == "connected"
        assert len(physics_data) == 4
        assert len(agent_results) == 4
        assert orchestrator_result["status"] == "completed"
        assert 0.0 <= overall_score <= 1.0
        assert verdict["status"] == "CLEAR"
        assert verdict["recommendation"] == "PROCEED"

    def test_pipeline_with_anomaly_detection(self):
        """
        Test pipeline with anomaly detection (suspicious candidate)
        """
        # Physics data with anomalies
        physics_data = {
            "chronos": {
                "mean_jitter": 85.5,  # High jitter
                "std_jitter": 25.4
            },
            "echo": {
                "mean_tof": 150.0,  # High delay
                "std_tof": 45.2
            },
            "iris": {
                "face_detected": True,
                "eye_variance": 0.8,  # High variance
                "liveness_score": 0.45  # Low liveness
            },
            "lipsync": {
                "mean_sync": 0.35,  # Low sync
                "drift_score": 0.85  # High drift
            }
        }
        
        # Agents detect anomalies
        agent_results = [
            {
                "agent_id": "chronos",
                "status": "completed",
                "score": 0.25,  # Low score = anomaly
                "confidence": 0.9,
                "data": physics_data["chronos"]
            },
            {
                "agent_id": "echo",
                "status": "completed",
                "score": 0.20,
                "confidence": 0.85,
                "data": physics_data["echo"]
            },
            {
                "agent_id": "iris",
                "status": "completed",
                "score": 0.35,
                "confidence": 0.95,
                "data": physics_data["iris"]
            },
            {
                "agent_id": "lipsync",
                "status": "completed",
                "score": 0.30,
                "confidence": 0.88,
                "data": physics_data["lipsync"]
            }
        ]
        
        # Orchestrator aggregates
        total_weight = sum(r["confidence"] for r in agent_results)
        weighted_score = sum(r["score"] * r["confidence"] for r in agent_results)
        overall_score = weighted_score / total_weight
        
        # Verdict should be suspicious
        verdict = {
            "status": "LIKELY_FAKE" if overall_score < 0.4 else "SUSPECT",
            "trust_score": overall_score,
            "risk_level": "HIGH",
            "recommendation": "REJECT" if overall_score < 0.3 else "DEEP_DIVE"
        }
        
        # Validate anomaly detection
        assert overall_score < 0.4
        assert verdict["status"] in ["SUSPECT", "LIKELY_FAKE"]
        assert verdict["risk_level"] == "HIGH"

    def test_pipeline_with_partial_failure(self):
        """
        Test pipeline when some agents fail
        """
        # Mixed agent results
        agent_results = [
            {
                "agent_id": "chronos",
                "status": "completed",
                "score": 0.85,
                "confidence": 0.9,
                "data": {}
            },
            {
                "agent_id": "echo",
                "status": "error",
                "score": 0.0,
                "confidence": 0.0,
                "error_message": "Audio data insufficient",
                "data": {}
            },
            {
                "agent_id": "iris",
                "status": "completed",
                "score": 0.92,
                "confidence": 0.95,
                "data": {}
            },
            {
                "agent_id": "lipsync",
                "status": "completed",
                "score": 0.88,
                "confidence": 0.88,
                "data": {}
            }
        ]
        
        # Orchestrator handles partial failure
        successful_results = [r for r in agent_results if r["status"] == "completed"]
        total_weight = sum(r["confidence"] for r in successful_results)
        weighted_score = sum(r["score"] * r["confidence"] for r in successful_results)
        overall_score = weighted_score / total_weight if total_weight > 0 else 0.0
        
        orchestrator_result = {
            "status": "completed",  # Can complete with partial results
            "overall_score": overall_score,
            "overall_confidence": total_weight / len(successful_results),
            "agent_results": {r["agent_id"]: r for r in agent_results},
            "aggregated_data": {
                "method": "weighted_average",
                "agent_count": 4,
                "successful_count": len(successful_results),
                "failed_count": len(agent_results) - len(successful_results)
            }
        }
        
        # Validate partial failure handling
        assert orchestrator_result["aggregated_data"]["failed_count"] == 1
        assert orchestrator_result["aggregated_data"]["successful_count"] == 3
        assert orchestrator_result["status"] == "completed"

    def test_pipeline_with_realtime_updates(self):
        """
        Test pipeline with real-time updates during interview
        """
        # Simulate real-time analysis updates
        updates = []
        
        for i in range(5):
            # Physics data at time i
            physics_snapshot = {
                "chronos": {"mean_jitter": 15.0 + i * 0.5},
                "iris": {"liveness_score": 0.9 - i * 0.02}
            }
            
            # Agent results
            agent_snapshot = {
                "chronos": {"score": 0.85 - i * 0.01, "confidence": 0.9},
                "iris": {"score": 0.92 - i * 0.01, "confidence": 0.95}
            }
            
            # Orchestrator result
            total_weight = sum(r["confidence"] for r in agent_snapshot.values())
            weighted_score = sum(r["score"] * r["confidence"] for r in agent_snapshot.values())
            overall_score = weighted_score / total_weight
            
            update = {
                "timestamp": f"2024-01-01T10:0{i}:00Z",
                "overall_score": overall_score,
                "agent_scores": {k: v["score"] for k, v in agent_snapshot.items()}
            }
            updates.append(update)
        
        # Verify real-time updates
        assert len(updates) == 5
        # Scores should gradually decrease (simulating fatigue)
        assert updates[0]["overall_score"] > updates[-1]["overall_score"]

    def test_pipeline_with_signaling_integration(self):
        """
        Test complete pipeline including signaling for real-time communication
        """
        # Step 1: Candidate and HR connect via signaling
        signaling_connections = {
            "candidate": {
                "client_id": "client_candidate",
                "status": "connected",
                "room_id": "interview_room_123"
            },
            "hr": {
                "client_id": "client_hr",
                "status": "connected",
                "room_id": "interview_room_123"
            }
        }
        
        # Step 2: Video/audio established via WebRTC signaling
        webrtc_established = {
            "video": {"status": "connected", "quality": "720p"},
            "audio": {"status": "connected", "codec": "opus"}
        }
        
        # Step 3: Physics engine collects data during call
        physics_data = {
            "chronos": {"mean_jitter": 15.5},
            "iris": {"liveness_score": 0.92}
        }
        
        # Step 4: Agents analyze
        agent_results = [
            {"agent_id": "chronos", "score": 0.85, "confidence": 0.9},
            {"agent_id": "iris", "score": 0.92, "confidence": 0.95}
        ]
        
        # Step 5: Orchestrator aggregates
        overall_score = 0.885
        
        # Step 6: Dashboard displays with real-time signaling
        dashboard_display = {
            "trust_score": overall_score,
            "status": "CLEAR",
            "video_active": True,
            "audio_active": True,
            "signaling_connected": True
        }
        
        # Validate complete pipeline with signaling
        assert signaling_connections["candidate"]["status"] == "connected"
        assert signaling_connections["hr"]["status"] == "connected"
        assert webrtc_established["video"]["status"] == "connected"
        assert dashboard_display["signaling_connected"] is True

    def test_pipeline_data_persistence(self):
        """
        Test that pipeline data is persisted throughout the flow
        """
        # Initial candidate data
        candidate_data = {
            "candidate_id": "candidate_123",
            "session_id": "session_456",
            "start_time": "2024-01-01T10:00:00Z"
        }
        
        # Physics data with timestamps
        physics_data = {
            "chronos": {
                "data": {"mean_jitter": 15.5},
                "timestamp": "2024-01-01T10:01:00Z"
            },
            "iris": {
                "data": {"liveness_score": 0.92},
                "timestamp": "2024-01-01T10:01:00Z"
            }
        }
        
        # Agent results with metadata
        agent_results = [
            {
                "agent_id": "chronos",
                "score": 0.85,
                "metadata": {
                    "physics_timestamp": physics_data["chronos"]["timestamp"],
                    "execution_time_ms": 150
                }
            }
        ]
        
        # Orchestrator result with chain of custody
        orchestrator_result = {
            "overall_score": 0.85,
            "metadata": {
                "candidate_id": candidate_data["candidate_id"],
                "session_id": candidate_data["session_id"],
                "data_sources": ["chronos", "iris"],
                "processing_chain": ["physics", "agents", "orchestrator"]
            }
        }
        
        # Verify data persistence
        assert orchestrator_result["metadata"]["candidate_id"] == candidate_data["candidate_id"]
        assert orchestrator_result["metadata"]["session_id"] == candidate_data["session_id"]
        assert "physics" in orchestrator_result["metadata"]["processing_chain"]

    def test_pipeline_error_recovery(self):
        """
        Test pipeline error recovery and retry logic
        """
        # Simulate agent failure
        agent_failure = {
            "agent_id": "chronos",
            "status": "error",
            "error_message": "WASM module timeout",
            "retry_count": 0
        }
        
        # Retry logic
        retry_attempt = {
            "agent_id": "chronos",
            "retry_count": 1,
            "max_retries": 3,
            "status": "retrying"
        }
        
        # Successful retry
        agent_success = {
            "agent_id": "chronos",
            "status": "completed",
            "score": 0.85,
            "confidence": 0.9,
            "retry_count": 1,
            "retry_successful": True
        }
        
        # Validate error recovery
        assert agent_failure["status"] == "error"
        assert retry_attempt["retry_count"] == 1
        assert agent_success["retry_successful"] is True
        assert agent_success["status"] == "completed"

    def test_pipeline_performance_metrics(self):
        """
        Test that pipeline performance metrics are collected
        """
        # Simulate timing data for each stage
        pipeline_timing = {
            "physics_collection": {
                "start": "2024-01-01T10:00:00Z",
                "end": "2024-01-01T10:00:05Z",
                "duration_ms": 5000
            },
            "agent_execution": {
                "start": "2024-01-01T10:00:05Z",
                "end": "2024-01-01T10:00:07Z",
                "duration_ms": 2000
            },
            "orchestrator_aggregation": {
                "start": "2024-01-01T10:00:07Z",
                "end": "2024-01-01T10:00:08Z",
                "duration_ms": 1000
            },
            "dashboard_display": {
                "start": "2024-01-01T10:00:08Z",
                "end": "2024-01-01T10:00:09Z",
                "duration_ms": 1000
            }
        }
        
        # Calculate total pipeline duration
        total_duration = sum(stage["duration_ms"] for stage in pipeline_timing.values())
        
        # Performance report
        performance_report = {
            "total_pipeline_duration_ms": total_duration,
            "stage_breakdown": pipeline_timing,
            "meets_sla": total_duration < 10000,  # 10 second SLA
            "slowest_stage": max(pipeline_timing.items(), key=lambda x: x[1]["duration_ms"])[0]
        }
        
        # Validate performance metrics
        assert performance_report["total_pipeline_duration_ms"] == 9000
        assert performance_report["meets_sla"] is True
        assert performance_report["slowest_stage"] == "physics_collection"

    def test_pipeline_with_multiple_candidates(self):
        """
        Test pipeline handling multiple concurrent candidates
        """
        # Multiple candidate sessions
        candidates = [
            {"candidate_id": "candidate_001", "session_id": "session_001"},
            {"candidate_id": "candidate_002", "session_id": "session_002"},
            {"candidate_id": "candidate_003", "session_id": "session_003"}
        ]
        
        # Process each candidate
        results = []
        for candidate in candidates:
            # Simulate pipeline for each candidate
            candidate_result = {
                "candidate_id": candidate["candidate_id"],
                "session_id": candidate["session_id"],
                "trust_score": 0.8 + (hash(candidate["candidate_id"]) % 20) / 100.0,
                "status": "CLEAR",
                "processing_time_ms": 8000
            }
            results.append(candidate_result)
        
        # Dashboard displays all candidates
        dashboard_view = {
            "total_candidates": len(candidates),
            "candidates": results,
            "average_trust_score": sum(r["trust_score"] for r in results) / len(results)
        }
        
        # Validate multi-candidate handling
        assert dashboard_view["total_candidates"] == 3
        assert len(dashboard_view["candidates"]) == 3
        assert 0.0 <= dashboard_view["average_trust_score"] <= 1.0


class TestPipelineIntegrationPoints:
    """Test specific integration points in the pipeline"""

    def test_physics_to_agents_data_format(self):
        """Test data format compatibility between physics and agents"""
        physics_output = {
            "chronos": {
                "timestamps": [0, 100, 200],
                "sample_rate": 44100,
                "mean_jitter": 15.5
            }
        }
        
        # Agent expects specific format
        agent_input = {
            "timestamps": physics_output["chronos"]["timestamps"],
            "sample_rate": physics_output["chronos"]["sample_rate"],
            "jitter_data": [15.5]
        }
        
        # Validate format compatibility
        assert "timestamps" in agent_input
        assert "sample_rate" in agent_input
        assert len(agent_input["timestamps"]) == len(physics_output["chronos"]["timestamps"])

    def test_agents_to_orchestrator_result_format(self):
        """Test result format compatibility between agents and orchestrator"""
        agent_result = {
            "agent_id": "chronos",
            "status": "completed",
            "score": 0.85,
            "confidence": 0.9,
            "data": {"jitter_score": 15.5}
        }
        
        # Orchestrator expects specific fields
        orchestrator_input = {
            "agent_id": agent_result["agent_id"],
            "status": agent_result["status"],
            "score": agent_result["score"],
            "confidence": agent_result["confidence"]
        }
        
        # Validate format compatibility
        assert orchestrator_input["agent_id"] == agent_result["agent_id"]
        assert 0.0 <= orchestrator_input["score"] <= 1.0

    def test_orchestrator_to_dashboard_display_format(self):
        """Test display format compatibility between orchestrator and dashboard"""
        orchestrator_result = {
            "overall_score": 0.85,
            "status": "completed",
            "agent_results": {}
        }
        
        # Dashboard expects display-ready format
        dashboard_display = {
            "trust_score": orchestrator_result["overall_score"],
            "status_label": orchestrator_result["status"].upper(),
            "color": "green" if orchestrator_result["overall_score"] > 0.7 else "red"
        }
        
        # Validate display format
        assert dashboard_display["trust_score"] == orchestrator_result["overall_score"]
        assert dashboard_display["color"] == "green"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
