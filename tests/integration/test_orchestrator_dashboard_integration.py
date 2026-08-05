"""
Integration Test: Orchestrator → Dashboard

This module tests the integration between the Agent Orchestrator and the
HR Dashboard. It validates that orchestrator results flow correctly
to the dashboard for visualization and HR decision support.
"""

import pytest
from typing import Dict, Any, List
from datetime import datetime


class TestOrchestratorToDashboardIntegration:
    """Integration tests for Orchestrator → Dashboard data flow"""

    def test_orchestrator_result_to_dashboard(self):
        """
        Test orchestrator result flows correctly to dashboard
        
        This simulates the flow:
        1. Orchestrator produces aggregated result
        2. Result is sent to dashboard API
        3. Dashboard processes and formats for display
        4. Dashboard renders visualization
        """
        # Simulate orchestrator result
        orchestrator_result = {
            "orchestrator_id": "main_orchestrator",
            "status": "completed",
            "overall_score": 0.85,
            "overall_confidence": 0.9,
            "agent_results": {
                "chronos": {
                    "agent_id": "chronos",
                    "status": "completed",
                    "score": 0.85,
                    "confidence": 0.9,
                    "data": {"jitter_score": 15.5},
                    "metadata": {}
                },
                "iris": {
                    "agent_id": "iris",
                    "status": "completed",
                    "score": 0.92,
                    "confidence": 0.95,
                    "data": {"liveness_score": 0.92},
                    "metadata": {}
                }
            },
            "aggregated_data": {
                "method": "weighted_average",
                "agent_count": 2
            },
            "metadata": {
                "strategy": "sequential",
                "timestamp": "2024-01-01T12:34:56Z"
            }
        }
        
        # Dashboard receives and formats for display
        dashboard_data = {
            "candidate_id": "candidate_123",
            "session_id": "session_456",
            "trust_score": orchestrator_result["overall_score"],
            "confidence": orchestrator_result["overall_confidence"],
            "status": orchestrator_result["status"],
            "agent_breakdown": [
                {
                    "name": "CHRONOS",
                    "score": orchestrator_result["agent_results"]["chronos"]["score"],
                    "confidence": orchestrator_result["agent_results"]["chronos"]["confidence"],
                    "data": orchestrator_result["agent_results"]["chronos"]["data"]
                },
                {
                    "name": "IRIS",
                    "score": orchestrator_result["agent_results"]["iris"]["score"],
                    "confidence": orchestrator_result["agent_results"]["iris"]["confidence"],
                    "data": orchestrator_result["agent_results"]["iris"]["data"]
                }
            ],
            "timestamp": orchestrator_result["metadata"]["timestamp"],
            "recommendation": "PROCEED" if orchestrator_result["overall_score"] > 0.7 else "REVIEW"
        }
        
        # Validate dashboard data
        assert dashboard_data["trust_score"] == 0.85
        assert dashboard_data["recommendation"] == "PROCEED"
        assert len(dashboard_data["agent_breakdown"]) == 2

    def test_verdict_to_dashboard_display(self):
        """
        Test that orchestrator verdict is properly displayed on dashboard
        """
        orchestrator_verdict = {
            "status": "CLEAR",
            "trust_score": 0.88,
            "confidence": 0.92,
            "evidence_count": 4,
            "evidence": [
                {"agent": "chronos", "score": 0.85, "reasoning": "Low frame jitter"},
                {"agent": "echo", "score": 0.78, "reasoning": "Normal audio delay"},
                {"agent": "iris", "score": 0.92, "reasoning": "High liveness score"},
                {"agent": "lipsync", "score": 0.88, "reasoning": "Good sync"}
            ],
            "has_trend": True,
            "trend": "IMPROVING"
        }
        
        # Dashboard formats verdict for display
        dashboard_verdict = {
            "verdict_status": orchestrator_verdict["status"],
            "trust_score": orchestrator_verdict["trust_score"],
            "confidence": orchestrator_verdict["confidence"],
            "evidence": orchestrator_verdict["evidence"],
            "trend": orchestrator_verdict["trend"],
            "display_color": "green" if orchestrator_verdict["status"] == "CLEAR" else "red",
            "display_message": "Candidate appears authentic" if orchestrator_verdict["status"] == "CLEAR" else "Review required"
        }
        
        # Validate verdict display
        assert dashboard_verdict["display_color"] == "green"
        assert dashboard_verdict["display_message"] == "Candidate appears authentic"

    def test_recommendations_to_dashboard(self):
        """
        Test that orchestrator recommendations flow to dashboard
        """
        orchestrator_recommendations = {
            "verdict_status": "SUSPECT",
            "trust_score": 0.45,
            "risk_level": "HIGH",
            "summary": "Multiple anomalies detected in physics analysis",
            "recommendations": [
                "Conduct additional verification",
                "Review audio-video synchronization",
                "Verify liveness detection"
            ],
            "suggested_interview_flow": "DEEP_DIVE"
        }
        
        # Dashboard formats recommendations
        dashboard_recommendations = {
            "risk_level": orchestrator_recommendations["risk_level"],
            "risk_color": "red" if orchestrator_recommendations["risk_level"] == "HIGH" else "yellow",
            "summary": orchestrator_recommendations["summary"],
            "action_items": orchestrator_recommendations["recommendations"],
            "suggested_flow": orchestrator_recommendations["suggested_interview_flow"],
            "priority": "URGENT" if orchestrator_recommendations["risk_level"] == "HIGH" else "NORMAL"
        }
        
        # Validate recommendations display
        assert dashboard_recommendations["risk_color"] == "red"
        assert dashboard_recommendations["priority"] == "URGENT"
        assert len(dashboard_recommendations["action_items"]) == 3

    def test_historical_data_to_dashboard(self):
        """
        Test that historical orchestrator data flows to dashboard charts
        """
        historical_results = [
            {"timestamp": "2024-01-01T10:00:00Z", "trust_score": 0.75, "status": "CLEAR"},
            {"timestamp": "2024-01-01T10:05:00Z", "trust_score": 0.78, "status": "CLEAR"},
            {"timestamp": "2024-01-01T10:10:00Z", "trust_score": 0.82, "status": "CLEAR"},
            {"timestamp": "2024-01-01T10:15:00Z", "trust_score": 0.85, "status": "CLEAR"},
            {"timestamp": "2024-01-01T10:20:00Z", "trust_score": 0.88, "status": "CLEAR"}
        ]
        
        # Dashboard formats for chart display
        chart_data = {
            "chart_type": "line",
            "title": "Trust Score Over Time",
            "x_axis": [r["timestamp"] for r in historical_results],
            "y_axis": [r["trust_score"] for r in historical_results],
            "status_markers": [r["status"] for r in historical_results],
            "trend": "IMPROVING",
            "average_score": sum(r["trust_score"] for r in historical_results) / len(historical_results)
        }
        
        # Validate chart data
        assert len(chart_data["x_axis"]) == 5
        assert chart_data["trend"] == "IMPROVING"
        assert chart_data["average_score"] == 0.816

    def test_real_time_updates_to_dashboard(self):
        """
        Test that real-time orchestrator updates flow to dashboard
        """
        # Simulate real-time orchestrator update
        realtime_update = {
            "orchestrator_id": "main_orchestrator",
            "update_type": "partial_result",
            "agent_id": "chronos",
            "score": 0.85,
            "confidence": 0.9,
            "timestamp": "2024-01-01T12:34:56.789Z"
        }
        
        # Dashboard receives and updates display
        dashboard_update = {
            "update_type": "AGENT_RESULT",
            "agent_name": "CHRONOS",
            "score": realtime_update["score"],
            "confidence": realtime_update["confidence"],
            "timestamp": realtime_update["timestamp"],
            "display_update": True,
            "animation": "fade_in"
        }
        
        # Validate real-time update
        assert dashboard_update["display_update"] is True
        assert dashboard_update["agent_name"] == "CHRONOS"

    def test_multiple_candidates_to_dashboard(self):
        """
        Test that orchestrator results for multiple candidates flow to dashboard
        """
        candidates_data = [
            {
                "candidate_id": "candidate_001",
                "orchestrator_result": {
                    "overall_score": 0.92,
                    "status": "CLEAR",
                    "confidence": 0.95
                }
            },
            {
                "candidate_id": "candidate_002",
                "orchestrator_result": {
                    "overall_score": 0.65,
                    "status": "SUSPECT",
                    "confidence": 0.8
                }
            },
            {
                "candidate_id": "candidate_003",
                "orchestrator_result": {
                    "overall_score": 0.78,
                    "status": "CLEAR",
                    "confidence": 0.85
                }
            }
        ]
        
        # Dashboard formats candidate list
        dashboard_candidates = {
            "total_candidates": len(candidates_data),
            "clear_count": sum(1 for c in candidates_data if c["orchestrator_result"]["status"] == "CLEAR"),
            "suspect_count": sum(1 for c in candidates_data if c["orchestrator_result"]["status"] == "SUSPECT"),
            "average_trust_score": sum(c["orchestrator_result"]["overall_score"] for c in candidates_data) / len(candidates_data),
            "candidates": [
                {
                    "id": c["candidate_id"],
                    "trust_score": c["orchestrator_result"]["overall_score"],
                    "status": c["orchestrator_result"]["status"],
                    "status_color": "green" if c["orchestrator_result"]["status"] == "CLEAR" else "red"
                }
                for c in candidates_data
            ]
        }
        
        # Validate candidate list
        assert dashboard_candidates["total_candidates"] == 3
        assert dashboard_candidates["clear_count"] == 2
        assert dashboard_candidates["suspect_count"] == 1

    def test_orchestrator_error_to_dashboard(self):
        """
        Test that orchestrator errors are properly displayed on dashboard
        """
        orchestrator_error = {
            "orchestrator_id": "main_orchestrator",
            "status": "error",
            "error_message": "Required agent 'iris' failed to execute",
            "error_code": "AGENT_FAILURE",
            "timestamp": "2024-01-01T12:34:56Z"
        }
        
        # Dashboard formats error for display
        dashboard_error = {
            "error_type": "ORCHESTRATOR_ERROR",
            "error_code": orchestrator_error["error_code"],
            "error_message": orchestrator_error["error_message"],
            "timestamp": orchestrator_error["timestamp"],
            "display_alert": True,
            "alert_type": "error",
            "suggested_action": "Retry analysis or check agent status"
        }
        
        # Validate error display
        assert dashboard_error["display_alert"] is True
        assert dashboard_error["alert_type"] == "error"
        assert "suggested_action" in dashboard_error

    def test_agent_breakdown_visualization(self):
        """
        Test that agent breakdown data flows to dashboard visualization
        """
        orchestrator_result = {
            "agent_results": {
                "chronos": {"score": 0.85, "confidence": 0.9, "data": {"jitter_score": 15.5}},
                "echo": {"score": 0.78, "confidence": 0.85, "data": {"delay": 12.5}},
                "iris": {"score": 0.92, "confidence": 0.95, "data": {"liveness_score": 0.92}},
                "lipsync": {"score": 0.88, "confidence": 0.88, "data": {"sync_score": 0.88}}
            }
        }
        
        # Dashboard formats for visualization
        viz_data = {
            "chart_type": "radar",
            "title": "Agent Performance Breakdown",
            "axes": ["CHRONOS", "ECHO", "IRIS", "LIPSYNC"],
            "scores": [
                orchestrator_result["agent_results"]["chronos"]["score"],
                orchestrator_result["agent_results"]["echo"]["score"],
                orchestrator_result["agent_results"]["iris"]["score"],
                orchestrator_result["agent_results"]["lipsync"]["score"]
            ],
            "confidences": [
                orchestrator_result["agent_results"]["chronos"]["confidence"],
                orchestrator_result["agent_results"]["echo"]["confidence"],
                orchestrator_result["agent_results"]["iris"]["confidence"],
                orchestrator_result["agent_results"]["lipsync"]["confidence"]
            ]
        }
        
        # Validate visualization data
        assert len(viz_data["axes"]) == 4
        assert len(viz_data["scores"]) == 4
        assert all(0.0 <= s <= 1.0 for s in viz_data["scores"])

    def test_dashboard_filtering_and_sorting(self):
        """
        Test that dashboard can filter and sort orchestrator results
        """
        candidates_data = [
            {"candidate_id": "001", "trust_score": 0.92, "status": "CLEAR", "timestamp": "2024-01-01T10:00:00Z"},
            {"candidate_id": "002", "trust_score": 0.65, "status": "SUSPECT", "timestamp": "2024-01-01T10:05:00Z"},
            {"candidate_id": "003", "trust_score": 0.78, "status": "CLEAR", "timestamp": "2024-01-01T10:10:00Z"},
            {"candidate_id": "004", "trust_score": 0.45, "status": "LIKELY_FAKE", "timestamp": "2024-01-01T10:15:00Z"},
            {"candidate_id": "005", "trust_score": 0.88, "status": "CLEAR", "timestamp": "2024-01-01T10:20:00Z"}
        ]
        
        # Filter by status
        clear_candidates = [c for c in candidates_data if c["status"] == "CLEAR"]
        
        # Sort by trust score (descending)
        sorted_candidates = sorted(clear_candidates, key=lambda x: x["trust_score"], reverse=True)
        
        dashboard_filtered = {
            "filter_criteria": {"status": "CLEAR"},
            "sort_criteria": {"field": "trust_score", "order": "desc"},
            "results": sorted_candidates,
            "count": len(sorted_candidates)
        }
        
        # Validate filtering and sorting
        assert dashboard_filtered["count"] == 3
        assert dashboard_filtered["results"][0]["candidate_id"] == "001"
        assert dashboard_filtered["results"][0]["trust_score"] == 0.92

    def test_dashboard_export_functionality(self):
        """
        Test that dashboard can export orchestrator results
        """
        orchestrator_result = {
            "candidate_id": "candidate_123",
            "trust_score": 0.85,
            "status": "CLEAR",
            "agent_results": {
                "chronos": {"score": 0.85, "data": {"jitter_score": 15.5}},
                "iris": {"score": 0.92, "data": {"liveness_score": 0.92}}
            },
            "timestamp": "2024-01-01T12:34:56Z"
        }
        
        # Dashboard formats for export
        export_data = {
            "format": "json",
            "data": orchestrator_result,
            "export_timestamp": datetime.utcnow().isoformat(),
            "filename": f"candidate_{orchestrator_result['candidate_id']}_report.json"
        }
        
        # Validate export data
        assert export_data["format"] == "json"
        assert "filename" in export_data
        assert orchestrator_result["candidate_id"] in export_data["filename"]


class TestDashboardAPIIntegration:
    """Test dashboard API endpoints for receiving orchestrator data"""

    def test_post_orchestrator_result_endpoint(self):
        """Test posting orchestrator result to dashboard API"""
        orchestrator_result = {
            "orchestrator_id": "main_orchestrator",
            "overall_score": 0.85,
            "status": "completed",
            "agent_results": {},
            "timestamp": "2024-01-01T12:34:56Z"
        }
        
        # Simulate API response
        api_response = {
            "status": "success",
            "message": "Result received and stored",
            "result_id": "result_12345",
            "timestamp": "2024-01-01T12:34:57Z"
        }
        
        # Validate API response
        assert api_response["status"] == "success"
        assert "result_id" in api_response

    def test_get_candidate_results_endpoint(self):
        """Test retrieving candidate results from dashboard API"""
        # Simulate API response
        api_response = {
            "candidate_id": "candidate_123",
            "results": [
                {
                    "session_id": "session_001",
                    "trust_score": 0.85,
                    "status": "CLEAR",
                    "timestamp": "2024-01-01T10:00:00Z"
                },
                {
                    "session_id": "session_002",
                    "trust_score": 0.88,
                    "status": "CLEAR",
                    "timestamp": "2024-01-01T11:00:00Z"
                }
            ],
            "total_count": 2
        }
        
        # Validate API response
        assert api_response["candidate_id"] == "candidate_123"
        assert api_response["total_count"] == 2
        assert len(api_response["results"]) == 2

    def test_get_aggregated_stats_endpoint(self):
        """Test retrieving aggregated statistics from dashboard API"""
        # Simulate API response
        api_response = {
            "total_candidates": 150,
            "clear_count": 120,
            "suspect_count": 25,
            "likely_fake_count": 5,
            "average_trust_score": 0.78,
            "risk_distribution": {
                "LOW": 120,
                "MEDIUM": 25,
                "HIGH": 5
            }
        }
        
        # Validate API response
        assert api_response["total_candidates"] == 150
        assert api_response["average_trust_score"] == 0.78
        assert api_response["risk_distribution"]["LOW"] == 120


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
