"""
Unit tests for CHRONOS Agent
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from src.agents.chronos_agent import ChronosAgent
from src.base import AgentConfig, AgentStatus


@pytest.fixture
def chronos_config():
    """Create CHRONOS agent configuration"""
    return AgentConfig(
        agent_id="chronos_test",
        priority="medium",
        timeout_ms=5000,
        max_retries=3,
    )


@pytest.fixture
def chronos_agent(chronos_config):
    """Create CHRONOS agent instance"""
    # Mock the WASM path finding to avoid dependency
    with patch.object(ChronosAgent, "_find_wasm_path", return_value="/mock/path"):
        agent = ChronosAgent(chronos_config)
        return agent


class TestChronosAgentInitialization:
    """Tests for CHRONOS agent initialization"""

    def test_initialization(self, chronos_config):
        """Test agent initialization"""
        with patch.object(ChronosAgent, "_find_wasm_path", return_value="/mock/path"):
            agent = ChronosAgent(chronos_config)
            assert agent.config.agent_id == "chronos_test"
            assert agent.wasm_path == "/mock/path"

    def test_find_wasm_path(self):
        """Test WASM path finding"""
        config = AgentConfig(agent_id="chronos_test")
        with patch("pathlib.Path.exists", return_value=True):
            agent = ChronosAgent(config, wasm_path="/custom/path")
            assert agent.wasm_path == "/custom/path"


class TestChronosAgentValidation:
    """Tests for input validation"""

    def test_validate_input_valid(self, chronos_agent):
        """Test validation with valid input"""
        input_data = {
            "timestamps": [0, 100, 200, 300],
            "sample_rate": 44100,
        }
        assert chronos_agent.validate_input(input_data) is True

    def test_validate_input_missing_timestamps(self, chronos_agent):
        """Test validation with missing timestamps field"""
        input_data = {
            "sample_rate": 44100,
        }
        assert chronos_agent.validate_input(input_data) is False

    def test_validate_input_missing_sample_rate(self, chronos_agent):
        """Test validation with missing sample_rate field"""
        input_data = {
            "timestamps": [0, 100, 200],
        }
        assert chronos_agent.validate_input(input_data) is False

    def test_validate_input_invalid_timestamps_type(self, chronos_agent):
        """Test validation with invalid timestamps type"""
        input_data = {
            "timestamps": "not a list",
            "sample_rate": 44100,
        }
        assert chronos_agent.validate_input(input_data) is False

    def test_validate_input_insufficient_timestamps(self, chronos_agent):
        """Test validation with insufficient timestamps"""
        input_data = {
            "timestamps": [0],
            "sample_rate": 44100,
        }
        assert chronos_agent.validate_input(input_data) is False

    def test_validate_input_invalid_sample_rate(self, chronos_agent):
        """Test validation with invalid sample_rate"""
        input_data = {
            "timestamps": [0, 100, 200],
            "sample_rate": -1,
        }
        assert chronos_agent.validate_input(input_data) is False

    def test_validate_input_zero_sample_rate(self, chronos_agent):
        """Test validation with zero sample_rate"""
        input_data = {
            "timestamps": [0, 100, 200],
            "sample_rate": 0,
        }
        assert chronos_agent.validate_input(input_data) is False


class TestChronosAgentProcessing:
    """Tests for data processing"""

    @patch.object(ChronosAgent, "_call_wasm_module")
    def test_process_success(self, mock_call_wasm, chronos_agent):
        """Test successful processing"""
        mock_call_wasm.return_value = {
            "jitter_score": 25.5,
            "jitter_std": 10.2,
            "jitter_mean": 15.0,
            "anomaly_count": 2,
        }

        input_data = {
            "timestamps": [0, 100, 200, 300],
            "sample_rate": 44100,
        }

        result = chronos_agent.process(input_data)

        assert result.agent_id == "chronos_test"
        assert result.status == AgentStatus.COMPLETED
        assert 0.0 <= result.score <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.data["jitter_score"] == 25.5
        assert result.data["jitter_std"] == 10.2
        assert result.data["anomaly_count"] == 2

    @patch.object(ChronosAgent, "_call_wasm_module")
    def test_process_high_jitter(self, mock_call_wasm, chronos_agent):
        """Test processing with high jitter"""
        mock_call_wasm.return_value = {
            "jitter_score": 85.0,
            "jitter_std": 60.0,
            "jitter_mean": 50.0,
            "anomaly_count": 15,
        }

        input_data = {
            "timestamps": [0, 100, 200, 300],
            "sample_rate": 44100,
        }

        result = chronos_agent.process(input_data)

        assert result.score > 0.7  # High jitter score
        assert result.status == AgentStatus.ERROR

    @patch.object(ChronosAgent, "_call_wasm_module")
    def test_process_low_jitter(self, mock_call_wasm, chronos_agent):
        """Test processing with low jitter"""
        mock_call_wasm.return_value = {
            "jitter_score": 5.0,
            "jitter_std": 2.0,
            "jitter_mean": 3.0,
            "anomaly_count": 0,
        }

        input_data = {
            "timestamps": [0, 100, 200, 300],
            "sample_rate": 44100,
        }

        result = chronos_agent.process(input_data)

        assert result.score < 0.3  # Low jitter score
        assert result.status == AgentStatus.COMPLETED


class TestChronosAgentWasmIntegration:
    """Tests for WASM integration"""

    @patch("subprocess.run")
    def test_call_wasm_module_success(self, mock_run, chronos_agent):
        """Test successful WASM module call"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"jitter_score": 25.5, "jitter_std": 10.2, "jitter_mean": 15.0, "anomaly_count": 2}',
            stderr="",
        )

        input_data = {
            "timestamps": [0, 100, 200],
            "sampleRate": 44100,
        }

        result = chronos_agent._call_wasm_module(input_data)

        assert result["jitter_score"] == 25.5
        assert result["anomaly_count"] == 2

    @patch("subprocess.run")
    def test_call_wasm_module_failure(self, mock_run, chronos_agent):
        """Test WASM module call failure"""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="WASM execution error")

        input_data = {
            "timestamps": [0, 100, 200],
            "sampleRate": 44100,
        }

        with pytest.raises(RuntimeError, match="WASM execution failed"):
            chronos_agent._call_wasm_module(input_data)

    @patch("subprocess.run")
    def test_call_wasm_module_timeout(self, mock_run, chronos_agent):
        """Test WASM module call timeout"""
        from subprocess import TimeoutExpired

        mock_run.side_effect = TimeoutExpired("node", 5)

        input_data = {
            "timestamps": [0, 100, 200],
            "sampleRate": 44100,
        }

        with pytest.raises(TimeoutError, match="timed out"):
            chronos_agent._call_wasm_module(input_data)


class TestChronosAgentScoreNormalization:
    """Tests for score normalization"""

    def test_normalize_score_low(self, chronos_agent):
        """Test normalizing low score"""
        assert chronos_agent._normalize_score(10) == 0.1

    def test_normalize_score_medium(self, chronos_agent):
        """Test normalizing medium score"""
        assert chronos_agent._normalize_score(50) == 0.5

    def test_normalize_score_high(self, chronos_agent):
        """Test normalizing high score"""
        assert chronos_agent._normalize_score(90) == 0.9

    def test_normalize_score_clamp_low(self, chronos_agent):
        """Test clamping negative score"""
        assert chronos_agent._normalize_score(-10) == 0.0

    def test_normalize_score_clamp_high(self, chronos_agent):
        """Test clamping score above 100"""
        assert chronos_agent._normalize_score(150) == 1.0


class TestChronosAgentStatusMapping:
    """Tests for status mapping"""

    def test_map_status_low_score(self, chronos_agent):
        """Test mapping low score to status"""
        assert chronos_agent._map_status(0.2) == AgentStatus.COMPLETED

    def test_map_status_medium_score(self, chronos_agent):
        """Test mapping medium score to status"""
        assert chronos_agent._map_status(0.5) == AgentStatus.COMPLETED

    def test_map_status_high_score(self, chronos_agent):
        """Test mapping high score to status"""
        assert chronos_agent._map_status(0.8) == AgentStatus.ERROR


class TestChronosAgentConfidenceCalculation:
    """Tests for confidence calculation"""

    def test_calculate_confidence_normal(self, chronos_agent):
        """Test confidence calculation with normal result"""
        result = {
            "anomaly_count": 2,
            "jitter_std": 10,
        }
        confidence = chronos_agent._calculate_confidence(result)
        assert 0.0 <= confidence <= 1.0
        assert confidence >= 0.7  # Should be high confidence

    def test_calculate_confidence_many_anomalies(self, chronos_agent):
        """Test confidence calculation with many anomalies"""
        result = {
            "anomaly_count": 15,
            "jitter_std": 10,
        }
        confidence = chronos_agent._calculate_confidence(result)
        assert confidence < 0.7  # Should reduce confidence

    def test_calculate_confidence_high_jitter(self, chronos_agent):
        """Test confidence calculation with high jitter"""
        result = {
            "anomaly_count": 2,
            "jitter_std": 60,
        }
        confidence = chronos_agent._calculate_confidence(result)
        assert confidence < 0.8  # Should reduce confidence


class TestChronosAgentOutputValidation:
    """Tests for output validation"""

    @patch.object(ChronosAgent, "_call_wasm_module")
    def test_validate_output_valid(self, mock_call_wasm, chronos_agent):
        """Test validating valid output"""
        mock_call_wasm.return_value = {
            "jitter_score": 25.5,
            "jitter_std": 10.2,
            "jitter_mean": 15.0,
            "anomaly_count": 2,
        }

        input_data = {
            "timestamps": [0, 100, 200],
            "sample_rate": 44100,
        }

        result = chronos_agent.process(input_data)
        assert chronos_agent.validate_output(result) is True

    @patch.object(ChronosAgent, "_call_wasm_module")
    def test_validate_output_invalid_score(self, mock_call_wasm, chronos_agent):
        """Test validating output with invalid score"""
        mock_call_wasm.return_value = {
            "jitter_score": 25.5,
            "jitter_std": 10.2,
            "jitter_mean": 15.0,
            "anomaly_count": 2,
        }

        input_data = {
            "timestamps": [0, 100, 200],
            "sample_rate": 44100,
        }

        result = chronos_agent.process(input_data)
        result.score = 1.5  # Invalid score
        assert chronos_agent.validate_output(result) is False

    @patch.object(ChronosAgent, "_call_wasm_module")
    def test_validate_output_missing_field(self, mock_call_wasm, chronos_agent):
        """Test validating output with missing field"""
        mock_call_wasm.return_value = {
            "jitter_score": 25.5,
            "jitter_std": 10.2,
            "jitter_mean": 15.0,
            "anomaly_count": 2,
        }

        input_data = {
            "timestamps": [0, 100, 200],
            "sample_rate": 44100,
        }

        result = chronos_agent.process(input_data)
        del result.data["jitter_std"]
        assert chronos_agent.validate_output(result) is False
