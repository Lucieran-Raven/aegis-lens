"""
Unit tests for ECHO Agent
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from src.agents.echo_agent import EchoAgent
from src.base import AgentConfig, AgentStatus


@pytest.fixture
def echo_config():
    """Create ECHO agent configuration"""
    return AgentConfig(
        agent_id="echo_test",
        priority="medium",
        timeout_ms=5000,
        max_retries=3,
    )


@pytest.fixture
def echo_agent(echo_config):
    """Create ECHO agent instance"""
    # Mock the WASM path finding to avoid dependency
    with patch.object(EchoAgent, '_find_wasm_path', return_value='/mock/path'):
        agent = EchoAgent(echo_config)
        return agent


class TestEchoAgentInitialization:
    """Tests for ECHO agent initialization"""
    
    def test_initialization(self, echo_config):
        """Test agent initialization"""
        with patch.object(EchoAgent, '_find_wasm_path', return_value='/mock/path'):
            agent = EchoAgent(echo_config)
            assert agent.config.agent_id == "echo_test"
            assert agent.wasm_path == "/mock/path"
    
    def test_find_wasm_path(self):
        """Test WASM path finding"""
        config = AgentConfig(agent_id="echo_test")
        with patch('pathlib.Path.exists', return_value=True):
            agent = EchoAgent(config, wasm_path="/custom/path")
            assert agent.wasm_path == "/custom/path"


class TestEchoAgentValidation:
    """Tests for input validation"""
    
    def test_validate_input_valid(self, echo_agent):
        """Test validation with valid input"""
        input_data = {
            "audio_samples": [0.0] * 1000,
            "sample_rate": 44100,
        }
        assert echo_agent.validate_input(input_data) is True
    
    def test_validate_input_missing_audio_samples(self, echo_agent):
        """Test validation with missing audio_samples field"""
        input_data = {
            "sample_rate": 44100,
        }
        assert echo_agent.validate_input(input_data) is False
    
    def test_validate_input_missing_sample_rate(self, echo_agent):
        """Test validation with missing sample_rate field"""
        input_data = {
            "audio_samples": [0.0] * 1000,
        }
        assert echo_agent.validate_input(input_data) is False
    
    def test_validate_input_invalid_audio_samples_type(self, echo_agent):
        """Test validation with invalid audio_samples type"""
        input_data = {
            "audio_samples": "not a list",
            "sample_rate": 44100,
        }
        assert echo_agent.validate_input(input_data) is False
    
    def test_validate_input_insufficient_audio_samples(self, echo_agent):
        """Test validation with insufficient audio samples"""
        input_data = {
            "audio_samples": [0.0] * 50,
            "sample_rate": 44100,
        }
        assert echo_agent.validate_input(input_data) is False
    
    def test_validate_input_invalid_sample_rate(self, echo_agent):
        """Test validation with invalid sample_rate"""
        input_data = {
            "audio_samples": [0.0] * 1000,
            "sample_rate": -1,
        }
        assert echo_agent.validate_input(input_data) is False
    
    def test_validate_input_zero_sample_rate(self, echo_agent):
        """Test validation with zero sample_rate"""
        input_data = {
            "audio_samples": [0.0] * 1000,
            "sample_rate": 0,
        }
        assert echo_agent.validate_input(input_data) is False


class TestEchoAgentProcessing:
    """Tests for data processing"""
    
    @patch.object(EchoAgent, '_call_wasm_module')
    def test_process_success(self, mock_call_wasm, echo_agent):
        """Test successful processing"""
        mock_call_wasm.return_value = {
            "delay_score": 100.0,
            "delay_ms": 50.0,
            "threshold_crossed": False,
            "signal_quality": 0.9,
        }
        
        input_data = {
            "audio_samples": [0.0] * 1000,
            "sample_rate": 44100,
        }
        
        result = echo_agent.process(input_data)
        
        assert result.agent_id == "echo_test"
        assert result.status == AgentStatus.COMPLETED
        assert 0.0 <= result.score <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.data["delay_score"] == 100.0
        assert result.data["delay_ms"] == 50.0
        assert result.data["threshold_crossed"] is False
    
    @patch.object(EchoAgent, '_call_wasm_module')
    def test_process_high_delay(self, mock_call_wasm, echo_agent):
        """Test processing with high delay"""
        mock_call_wasm.return_value = {
            "delay_score": 400.0,
            "delay_ms": 200.0,
            "threshold_crossed": True,
            "signal_quality": 0.7,
        }
        
        input_data = {
            "audio_samples": [0.0] * 1000,
            "sample_rate": 44100,
        }
        
        result = echo_agent.process(input_data)
        
        assert result.score > 0.5  # High delay score
        assert result.status == AgentStatus.ERROR
    
    @patch.object(EchoAgent, '_call_wasm_module')
    def test_process_low_delay(self, mock_call_wasm, echo_agent):
        """Test processing with low delay"""
        mock_call_wasm.return_value = {
            "delay_score": 50.0,
            "delay_ms": 25.0,
            "threshold_crossed": False,
            "signal_quality": 0.95,
        }
        
        input_data = {
            "audio_samples": [0.0] * 1000,
            "sample_rate": 44100,
        }
        
        result = echo_agent.process(input_data)
        
        assert result.score < 0.2  # Low delay score
        assert result.status == AgentStatus.COMPLETED


class TestEchoAgentWasmIntegration:
    """Tests for WASM integration"""
    
    @patch('subprocess.run')
    def test_call_wasm_module_success(self, mock_run, echo_agent):
        """Test successful WASM module call"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"delay_score": 100.0, "delay_ms": 50.0, "threshold_crossed": false, "signal_quality": 0.9}',
            stderr=""
        )
        
        input_data = {
            "samples": [0.0] * 1000,
            "sampleRate": 44100,
            "referenceChirp": None,
        }
        
        result = echo_agent._call_wasm_module(input_data)
        
        assert result["delay_score"] == 100.0
        assert result["threshold_crossed"] is False
    
    @patch('subprocess.run')
    def test_call_wasm_module_failure(self, mock_run, echo_agent):
        """Test WASM module call failure"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="WASM execution error"
        )
        
        input_data = {
            "samples": [0.0] * 1000,
            "sampleRate": 44100,
            "referenceChirp": None,
        }
        
        with pytest.raises(RuntimeError, match="WASM execution failed"):
            echo_agent._call_wasm_module(input_data)
    
    @patch('subprocess.run')
    def test_call_wasm_module_timeout(self, mock_run, echo_agent):
        """Test WASM module call timeout"""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("node", 5)
        
        input_data = {
            "samples": [0.0] * 1000,
            "sampleRate": 44100,
            "referenceChirp": None,
        }
        
        with pytest.raises(TimeoutError, match="timed out"):
            echo_agent._call_wasm_module(input_data)


class TestEchoAgentScoreNormalization:
    """Tests for score normalization"""
    
    def test_normalize_score_low(self, echo_agent):
        """Test normalizing low score"""
        assert echo_agent._normalize_score(50) == 0.1
    
    def test_normalize_score_medium(self, echo_agent):
        """Test normalizing medium score"""
        assert echo_agent._normalize_score(250) == 0.5
    
    def test_normalize_score_high(self, echo_agent):
        """Test normalizing high score"""
        assert echo_agent._normalize_score(450) == 0.9
    
    def test_normalize_score_clamp_low(self, echo_agent):
        """Test clamping negative score"""
        assert echo_agent._normalize_score(-10) == 0.0
    
    def test_normalize_score_clamp_high(self, echo_agent):
        """Test clamping score above 500"""
        assert echo_agent._normalize_score(600) == 1.0


class TestEchoAgentStatusMapping:
    """Tests for status mapping"""
    
    def test_map_status_low_score(self, echo_agent):
        """Test mapping low score to status"""
        assert echo_agent._map_status(0.1) == AgentStatus.COMPLETED
    
    def test_map_status_medium_score(self, echo_agent):
        """Test mapping medium score to status"""
        assert echo_agent._map_status(0.3) == AgentStatus.COMPLETED
    
    def test_map_status_high_score(self, echo_agent):
        """Test mapping high score to status"""
        assert echo_agent._map_status(0.7) == AgentStatus.ERROR


class TestEchoAgentConfidenceCalculation:
    """Tests for confidence calculation"""
    
    def test_calculate_confidence_normal(self, echo_agent):
        """Test confidence calculation with normal result"""
        result = {
            "threshold_crossed": False,
            "signal_quality": 0.9,
        }
        confidence = echo_agent._calculate_confidence(result)
        assert 0.0 <= confidence <= 1.0
        assert confidence >= 0.8  # Should be high confidence
    
    def test_calculate_confidence_threshold_crossed(self, echo_agent):
        """Test confidence calculation with threshold crossed"""
        result = {
            "threshold_crossed": True,
            "signal_quality": 0.9,
        }
        confidence = echo_agent._calculate_confidence(result)
        assert confidence < 0.8  # Should reduce confidence
    
    def test_calculate_confidence_low_signal_quality(self, echo_agent):
        """Test confidence calculation with low signal quality"""
        result = {
            "threshold_crossed": False,
            "signal_quality": 0.3,
        }
        confidence = echo_agent._calculate_confidence(result)
        assert confidence < 0.5  # Should be low confidence


class TestEchoAgentOutputValidation:
    """Tests for output validation"""
    
    @patch.object(EchoAgent, '_call_wasm_module')
    def test_validate_output_valid(self, mock_call_wasm, echo_agent):
        """Test validating valid output"""
        mock_call_wasm.return_value = {
            "delay_score": 100.0,
            "delay_ms": 50.0,
            "threshold_crossed": False,
            "signal_quality": 0.9,
        }
        
        input_data = {
            "audio_samples": [0.0] * 1000,
            "sample_rate": 44100,
        }
        
        result = echo_agent.process(input_data)
        assert echo_agent.validate_output(result) is True
    
    @patch.object(EchoAgent, '_call_wasm_module')
    def test_validate_output_invalid_score(self, mock_call_wasm, echo_agent):
        """Test validating output with invalid score"""
        mock_call_wasm.return_value = {
            "delay_score": 100.0,
            "delay_ms": 50.0,
            "threshold_crossed": False,
            "signal_quality": 0.9,
        }
        
        input_data = {
            "audio_samples": [0.0] * 1000,
            "sample_rate": 44100,
        }
        
        result = echo_agent.process(input_data)
        result.score = 1.5  # Invalid score
        assert echo_agent.validate_output(result) is False
    
    @patch.object(EchoAgent, '_call_wasm_module')
    def test_validate_output_missing_field(self, mock_call_wasm, echo_agent):
        """Test validating output with missing field"""
        mock_call_wasm.return_value = {
            "delay_score": 100.0,
            "delay_ms": 50.0,
            "threshold_crossed": False,
            "signal_quality": 0.9,
        }
        
        input_data = {
            "audio_samples": [0.0] * 1000,
            "sample_rate": 44100,
        }
        
        result = echo_agent.process(input_data)
        del result.data["delay_ms"]
        assert echo_agent.validate_output(result) is False
