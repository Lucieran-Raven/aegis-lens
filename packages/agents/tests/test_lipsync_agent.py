"""
Unit tests for LIPSYNC Agent
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from src.agents.lipsync_agent import LipsyncAgent
from src.base import AgentConfig, AgentStatus


@pytest.fixture
def lipsync_config():
    """Create LIPSYNC agent configuration"""
    return AgentConfig(
        agent_id="lipsync_test",
        priority="medium",
        timeout_ms=5000,
        max_retries=3,
    )


@pytest.fixture
def lipsync_agent(lipsync_config):
    """Create LIPSYNC agent instance"""
    # Mock the WASM path finding to avoid dependency
    with patch.object(LipsyncAgent, "_find_wasm_path", return_value="/mock/path"):
        agent = LipsyncAgent(lipsync_config)
        return agent


class TestLipsyncAgentInitialization:
    """Tests for LIPSYNC agent initialization"""

    def test_initialization(self, lipsync_config):
        """Test agent initialization"""
        with patch.object(LipsyncAgent, "_find_wasm_path", return_value="/mock/path"):
            agent = LipsyncAgent(lipsync_config)
            assert agent.config.agent_id == "lipsync_test"
            assert agent.wasm_path == "/mock/path"

    def test_find_wasm_path(self):
        """Test WASM path finding"""
        config = AgentConfig(agent_id="lipsync_test")
        with patch("pathlib.Path.exists", return_value=True):
            agent = LipsyncAgent(config, wasm_path="/custom/path")
            assert agent.wasm_path == "/custom/path"


class TestLipsyncAgentValidation:
    """Tests for input validation"""

    def test_validate_input_valid(self, lipsync_agent):
        """Test validation with valid input"""
        input_data = {
            "audio_features": [[0.1, 0.2, 0.3]] * 100,
            "video_features": [[0.4, 0.5, 0.6]] * 100,
            "sync_data": [[0, 0]] * 100,
        }
        assert lipsync_agent.validate_input(input_data) is True

    def test_validate_input_missing_audio_features(self, lipsync_agent):
        """Test validation with missing audio_features field"""
        input_data = {
            "video_features": [[0.4, 0.5, 0.6]] * 100,
            "sync_data": [[0, 0]] * 100,
        }
        assert lipsync_agent.validate_input(input_data) is False

    def test_validate_input_missing_video_features(self, lipsync_agent):
        """Test validation with missing video_features field"""
        input_data = {
            "audio_features": [[0.1, 0.2, 0.3]] * 100,
            "sync_data": [[0, 0]] * 100,
        }
        assert lipsync_agent.validate_input(input_data) is False

    def test_validate_input_missing_sync_data(self, lipsync_agent):
        """Test validation with missing sync_data field"""
        input_data = {
            "audio_features": [[0.1, 0.2, 0.3]] * 100,
            "video_features": [[0.4, 0.5, 0.6]] * 100,
        }
        assert lipsync_agent.validate_input(input_data) is False

    def test_validate_input_invalid_audio_features_type(self, lipsync_agent):
        """Test validation with invalid audio_features type"""
        input_data = {
            "audio_features": "not a list",
            "video_features": [[0.4, 0.5, 0.6]] * 100,
            "sync_data": [[0, 0]] * 100,
        }
        assert lipsync_agent.validate_input(input_data) is False

    def test_validate_input_insufficient_audio_features(self, lipsync_agent):
        """Test validation with insufficient audio features"""
        input_data = {
            "audio_features": [[0.1, 0.2, 0.3]] * 5,
            "video_features": [[0.4, 0.5, 0.6]] * 5,
            "sync_data": [[0, 0]] * 5,
        }
        assert lipsync_agent.validate_input(input_data) is False

    def test_validate_input_mismatched_lengths(self, lipsync_agent):
        """Test validation with mismatched audio and video feature lengths"""
        input_data = {
            "audio_features": [[0.1, 0.2, 0.3]] * 100,
            "video_features": [[0.4, 0.5, 0.6]] * 50,
            "sync_data": [[0, 0]] * 100,
        }
        assert lipsync_agent.validate_input(input_data) is False


class TestLipsyncAgentProcessing:
    """Tests for data processing"""

    @patch.object(LipsyncAgent, "_call_wasm_module")
    def test_process_success(self, mock_call_wasm, lipsync_agent):
        """Test successful processing"""
        mock_call_wasm.return_value = {
            "sync_score": 85.0,
            "sync_error": 15.0,
            "phoneme_match_rate": 0.9,
            "mouth_openness_variance": 20.0,
        }

        input_data = {
            "audio_features": [[0.1, 0.2, 0.3]] * 100,
            "video_features": [[0.4, 0.5, 0.6]] * 100,
            "sync_data": [[0, 0]] * 100,
        }

        result = lipsync_agent.process(input_data)

        assert result.agent_id == "lipsync_test"
        assert result.status == AgentStatus.COMPLETED
        assert 0.0 <= result.score <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.data["sync_score"] == 85.0
        assert result.data["sync_error"] == 15.0
        assert result.data["phoneme_match_rate"] == 0.9

    @patch.object(LipsyncAgent, "_call_wasm_module")
    def test_process_high_sync(self, mock_call_wasm, lipsync_agent):
        """Test processing with high sync score"""
        mock_call_wasm.return_value = {
            "sync_score": 95.0,
            "sync_error": 5.0,
            "phoneme_match_rate": 0.95,
            "mouth_openness_variance": 15.0,
        }

        input_data = {
            "audio_features": [[0.1, 0.2, 0.3]] * 100,
            "video_features": [[0.4, 0.5, 0.6]] * 100,
            "sync_data": [[0, 0]] * 100,
        }

        result = lipsync_agent.process(input_data)

        assert result.score > 0.7  # High sync score
        assert result.status == AgentStatus.COMPLETED

    @patch.object(LipsyncAgent, "_call_wasm_module")
    def test_process_low_sync(self, mock_call_wasm, lipsync_agent):
        """Test processing with low sync score"""
        mock_call_wasm.return_value = {
            "sync_score": 20.0,
            "sync_error": 80.0,
            "phoneme_match_rate": 0.3,
            "mouth_openness_variance": 120.0,
        }

        input_data = {
            "audio_features": [[0.1, 0.2, 0.3]] * 100,
            "video_features": [[0.4, 0.5, 0.6]] * 100,
            "sync_data": [[0, 0]] * 100,
        }

        result = lipsync_agent.process(input_data)

        assert result.score < 0.3  # Low sync score
        assert result.status == AgentStatus.ERROR


class TestLipsyncAgentWasmIntegration:
    """Tests for WASM integration"""

    @patch("subprocess.run")
    def test_call_wasm_module_success(self, mock_run, lipsync_agent):
        """Test successful WASM module call"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"sync_score": 85.0, "sync_error": 15.0, "phoneme_match_rate": 0.9, "mouth_openness_variance": 20.0}',
            stderr="",
        )

        input_data = {
            "audioFeatures": [[0.1, 0.2, 0.3]] * 100,
            "videoFeatures": [[0.4, 0.5, 0.6]] * 100,
            "syncData": [[0, 0]] * 100,
        }

        result = lipsync_agent._call_wasm_module(input_data)

        assert result["sync_score"] == 85.0
        assert result["phoneme_match_rate"] == 0.9

    @patch("subprocess.run")
    def test_call_wasm_module_failure(self, mock_run, lipsync_agent):
        """Test WASM module call failure"""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="WASM execution error")

        input_data = {
            "audioFeatures": [[0.1, 0.2, 0.3]] * 100,
            "videoFeatures": [[0.4, 0.5, 0.6]] * 100,
            "syncData": [[0, 0]] * 100,
        }

        with pytest.raises(RuntimeError, match="WASM execution failed"):
            lipsync_agent._call_wasm_module(input_data)

    @patch("subprocess.run")
    def test_call_wasm_module_timeout(self, mock_run, lipsync_agent):
        """Test WASM module call timeout"""
        from subprocess import TimeoutExpired

        mock_run.side_effect = TimeoutExpired("node", 5)

        input_data = {
            "audioFeatures": [[0.1, 0.2, 0.3]] * 100,
            "videoFeatures": [[0.4, 0.5, 0.6]] * 100,
            "syncData": [[0, 0]] * 100,
        }

        with pytest.raises(TimeoutError, match="timed out"):
            lipsync_agent._call_wasm_module(input_data)


class TestLipsyncAgentScoreNormalization:
    """Tests for score normalization"""

    def test_normalize_score_low(self, lipsync_agent):
        """Test normalizing low score"""
        assert lipsync_agent._normalize_score(20) == 0.2

    def test_normalize_score_medium(self, lipsync_agent):
        """Test normalizing medium score"""
        assert lipsync_agent._normalize_score(50) == 0.5

    def test_normalize_score_high(self, lipsync_agent):
        """Test normalizing high score"""
        assert lipsync_agent._normalize_score(90) == 0.9

    def test_normalize_score_clamp_low(self, lipsync_agent):
        """Test clamping negative score"""
        assert lipsync_agent._normalize_score(-10) == 0.0

    def test_normalize_score_clamp_high(self, lipsync_agent):
        """Test clamping score above 100"""
        assert lipsync_agent._normalize_score(150) == 1.0


class TestLipsyncAgentStatusMapping:
    """Tests for status mapping"""

    def test_map_status_high_score(self, lipsync_agent):
        """Test mapping high score to status"""
        assert lipsync_agent._map_status(0.8) == AgentStatus.COMPLETED

    def test_map_status_medium_score(self, lipsync_agent):
        """Test mapping medium score to status"""
        assert lipsync_agent._map_status(0.5) == AgentStatus.COMPLETED

    def test_map_status_low_score(self, lipsync_agent):
        """Test mapping low score to status"""
        assert lipsync_agent._map_status(0.2) == AgentStatus.ERROR


class TestLipsyncAgentConfidenceCalculation:
    """Tests for confidence calculation"""

    def test_calculate_confidence_normal(self, lipsync_agent):
        """Test confidence calculation with normal result"""
        result = {
            "phoneme_match_rate": 0.9,
            "sync_error": 15.0,
            "mouth_openness_variance": 20.0,
        }
        confidence = lipsync_agent._calculate_confidence(result)
        assert 0.0 <= confidence <= 1.0
        assert confidence >= 0.8  # Should be high confidence

    def test_calculate_confidence_low_phoneme_match(self, lipsync_agent):
        """Test confidence calculation with low phoneme match rate"""
        result = {
            "phoneme_match_rate": 0.3,
            "sync_error": 15.0,
            "mouth_openness_variance": 20.0,
        }
        confidence = lipsync_agent._calculate_confidence(result)
        assert confidence < 0.5  # Should be low confidence

    def test_calculate_confidence_high_sync_error(self, lipsync_agent):
        """Test confidence calculation with high sync error"""
        result = {
            "phoneme_match_rate": 0.9,
            "sync_error": 60.0,
            "mouth_openness_variance": 20.0,
        }
        confidence = lipsync_agent._calculate_confidence(result)
        assert confidence < 0.8  # Should reduce confidence

    def test_calculate_confidence_high_variance(self, lipsync_agent):
        """Test confidence calculation with high mouth openness variance"""
        result = {
            "phoneme_match_rate": 0.9,
            "sync_error": 15.0,
            "mouth_openness_variance": 120.0,
        }
        confidence = lipsync_agent._calculate_confidence(result)
        assert confidence < 0.9  # Should reduce confidence slightly


class TestLipsyncAgentOutputValidation:
    """Tests for output validation"""

    @patch.object(LipsyncAgent, "_call_wasm_module")
    def test_validate_output_valid(self, mock_call_wasm, lipsync_agent):
        """Test validating valid output"""
        mock_call_wasm.return_value = {
            "sync_score": 85.0,
            "sync_error": 15.0,
            "phoneme_match_rate": 0.9,
            "mouth_openness_variance": 20.0,
        }

        input_data = {
            "audio_features": [[0.1, 0.2, 0.3]] * 100,
            "video_features": [[0.4, 0.5, 0.6]] * 100,
            "sync_data": [[0, 0]] * 100,
        }

        result = lipsync_agent.process(input_data)
        assert lipsync_agent.validate_output(result) is True

    @patch.object(LipsyncAgent, "_call_wasm_module")
    def test_validate_output_invalid_score(self, mock_call_wasm, lipsync_agent):
        """Test validating output with invalid score"""
        mock_call_wasm.return_value = {
            "sync_score": 85.0,
            "sync_error": 15.0,
            "phoneme_match_rate": 0.9,
            "mouth_openness_variance": 20.0,
        }

        input_data = {
            "audio_features": [[0.1, 0.2, 0.3]] * 100,
            "video_features": [[0.4, 0.5, 0.6]] * 100,
            "sync_data": [[0, 0]] * 100,
        }

        result = lipsync_agent.process(input_data)
        result.score = 1.5  # Invalid score
        assert lipsync_agent.validate_output(result) is False

    @patch.object(LipsyncAgent, "_call_wasm_module")
    def test_validate_output_missing_field(self, mock_call_wasm, lipsync_agent):
        """Test validating output with missing field"""
        mock_call_wasm.return_value = {
            "sync_score": 85.0,
            "sync_error": 15.0,
            "phoneme_match_rate": 0.9,
            "mouth_openness_variance": 20.0,
        }

        input_data = {
            "audio_features": [[0.1, 0.2, 0.3]] * 100,
            "video_features": [[0.4, 0.5, 0.6]] * 100,
            "sync_data": [[0, 0]] * 100,
        }

        result = lipsync_agent.process(input_data)
        del result.data["phoneme_match_rate"]
        assert lipsync_agent.validate_output(result) is False
