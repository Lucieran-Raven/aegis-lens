"""
Unit tests for IRIS Agent
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from src.agents.iris_agent import IrisAgent
from src.base import AgentConfig, AgentStatus


@pytest.fixture
def iris_config():
    """Create IRIS agent configuration"""
    return AgentConfig(
        agent_id="iris_test",
        priority="medium",
        timeout_ms=5000,
        max_retries=3,
    )


@pytest.fixture
def iris_agent(iris_config):
    """Create IRIS agent instance"""
    # Mock the WASM path finding to avoid dependency
    with patch.object(IrisAgent, '_find_wasm_path', return_value='/mock/path'):
        agent = IrisAgent(iris_config)
        return agent


class TestIrisAgentInitialization:
    """Tests for IRIS agent initialization"""
    
    def test_initialization(self, iris_config):
        """Test agent initialization"""
        with patch.object(IrisAgent, '_find_wasm_path', return_value='/mock/path'):
            agent = IrisAgent(iris_config)
            assert agent.config.agent_id == "iris_test"
            assert agent.wasm_path == "/mock/path"
    
    def test_find_wasm_path(self):
        """Test WASM path finding"""
        config = AgentConfig(agent_id="iris_test")
        with patch('pathlib.Path.exists', return_value=True):
            agent = IrisAgent(config, wasm_path="/custom/path")
            assert agent.wasm_path == "/custom/path"


class TestIrisAgentValidation:
    """Tests for input validation"""
    
    def test_validate_input_valid(self, iris_agent):
        """Test validation with valid input"""
        input_data = {
            "eye_vectors": [[0.5, 0.5]] * 100,
            "frame_count": 1000,
            "fps": 30,
        }
        assert iris_agent.validate_input(input_data) is True
    
    def test_validate_input_missing_eye_vectors(self, iris_agent):
        """Test validation with missing eye_vectors field"""
        input_data = {
            "frame_count": 1000,
            "fps": 30,
        }
        assert iris_agent.validate_input(input_data) is False
    
    def test_validate_input_missing_frame_count(self, iris_agent):
        """Test validation with missing frame_count field"""
        input_data = {
            "eye_vectors": [[0.5, 0.5]] * 100,
            "fps": 30,
        }
        assert iris_agent.validate_input(input_data) is False
    
    def test_validate_input_missing_fps(self, iris_agent):
        """Test validation with missing fps field"""
        input_data = {
            "eye_vectors": [[0.5, 0.5]] * 100,
            "frame_count": 1000,
        }
        assert iris_agent.validate_input(input_data) is False
    
    def test_validate_input_invalid_eye_vectors_type(self, iris_agent):
        """Test validation with invalid eye_vectors type"""
        input_data = {
            "eye_vectors": "not a list",
            "frame_count": 1000,
            "fps": 30,
        }
        assert iris_agent.validate_input(input_data) is False
    
    def test_validate_input_insufficient_eye_vectors(self, iris_agent):
        """Test validation with insufficient eye vectors"""
        input_data = {
            "eye_vectors": [[0.5, 0.5]] * 5,
            "frame_count": 1000,
            "fps": 30,
        }
        assert iris_agent.validate_input(input_data) is False
    
    def test_validate_input_invalid_frame_count(self, iris_agent):
        """Test validation with invalid frame_count"""
        input_data = {
            "eye_vectors": [[0.5, 0.5]] * 100,
            "frame_count": -1,
            "fps": 30,
        }
        assert iris_agent.validate_input(input_data) is False
    
    def test_validate_input_invalid_fps(self, iris_agent):
        """Test validation with invalid fps"""
        input_data = {
            "eye_vectors": [[0.5, 0.5]] * 100,
            "frame_count": 1000,
            "fps": -1,
        }
        assert iris_agent.validate_input(input_data) is False


class TestIrisAgentProcessing:
    """Tests for data processing"""
    
    @patch.object(IrisAgent, '_call_wasm_module')
    def test_process_success(self, mock_call_wasm, iris_agent):
        """Test successful processing"""
        mock_call_wasm.return_value = {
            "liveness_score": 85.0,
            "trajectory_smoothness": 0.9,
            "blink_rate": 15,
            "fixation_count": 10,
        }
        
        input_data = {
            "eye_vectors": [[0.5, 0.5]] * 100,
            "frame_count": 1000,
            "fps": 30,
        }
        
        result = iris_agent.process(input_data)
        
        assert result.agent_id == "iris_test"
        assert result.status == AgentStatus.COMPLETED
        assert 0.0 <= result.score <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.data["liveness_score"] == 85.0
        assert result.data["trajectory_smoothness"] == 0.9
        assert result.data["blink_rate"] == 15
    
    @patch.object(IrisAgent, '_call_wasm_module')
    def test_process_high_liveness(self, mock_call_wasm, iris_agent):
        """Test processing with high liveness"""
        mock_call_wasm.return_value = {
            "liveness_score": 95.0,
            "trajectory_smoothness": 0.95,
            "blink_rate": 18,
            "fixation_count": 12,
        }
        
        input_data = {
            "eye_vectors": [[0.5, 0.5]] * 100,
            "frame_count": 1000,
            "fps": 30,
        }
        
        result = iris_agent.process(input_data)
        
        assert result.score > 0.7  # High liveness score
        assert result.status == AgentStatus.COMPLETED
    
    @patch.object(IrisAgent, '_call_wasm_module')
    def test_process_low_liveness(self, mock_call_wasm, iris_agent):
        """Test processing with low liveness"""
        mock_call_wasm.return_value = {
            "liveness_score": 20.0,
            "trajectory_smoothness": 0.3,
            "blink_rate": 3,
            "fixation_count": 2,
        }
        
        input_data = {
            "eye_vectors": [[0.5, 0.5]] * 100,
            "frame_count": 1000,
            "fps": 30,
        }
        
        result = iris_agent.process(input_data)
        
        assert result.score < 0.3  # Low liveness score
        assert result.status == AgentStatus.ERROR


class TestIrisAgentWasmIntegration:
    """Tests for WASM integration"""
    
    @patch('subprocess.run')
    def test_call_wasm_module_success(self, mock_run, iris_agent):
        """Test successful WASM module call"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"liveness_score": 85.0, "trajectory_smoothness": 0.9, "blink_rate": 15, "fixation_count": 10}',
            stderr=""
        )
        
        input_data = {
            "vectors": [[0.5, 0.5]] * 100,
            "frameCount": 1000,
            "fps": 30,
        }
        
        result = iris_agent._call_wasm_module(input_data)
        
        assert result["liveness_score"] == 85.0
        assert result["fixation_count"] == 10
    
    @patch('subprocess.run')
    def test_call_wasm_module_failure(self, mock_run, iris_agent):
        """Test WASM module call failure"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="WASM execution error"
        )
        
        input_data = {
            "vectors": [[0.5, 0.5]] * 100,
            "frameCount": 1000,
            "fps": 30,
        }
        
        with pytest.raises(RuntimeError, match="WASM execution failed"):
            iris_agent._call_wasm_module(input_data)
    
    @patch('subprocess.run')
    def test_call_wasm_module_timeout(self, mock_run, iris_agent):
        """Test WASM module call timeout"""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("node", 5)
        
        input_data = {
            "vectors": [[0.5, 0.5]] * 100,
            "frameCount": 1000,
            "fps": 30,
        }
        
        with pytest.raises(TimeoutError, match="timed out"):
            iris_agent._call_wasm_module(input_data)


class TestIrisAgentScoreNormalization:
    """Tests for score normalization"""
    
    def test_normalize_score_low(self, iris_agent):
        """Test normalizing low score"""
        assert iris_agent._normalize_score(20) == 0.2
    
    def test_normalize_score_medium(self, iris_agent):
        """Test normalizing medium score"""
        assert iris_agent._normalize_score(50) == 0.5
    
    def test_normalize_score_high(self, iris_agent):
        """Test normalizing high score"""
        assert iris_agent._normalize_score(90) == 0.9
    
    def test_normalize_score_clamp_low(self, iris_agent):
        """Test clamping negative score"""
        assert iris_agent._normalize_score(-10) == 0.0
    
    def test_normalize_score_clamp_high(self, iris_agent):
        """Test clamping score above 100"""
        assert iris_agent._normalize_score(150) == 1.0


class TestIrisAgentStatusMapping:
    """Tests for status mapping"""
    
    def test_map_status_high_score(self, iris_agent):
        """Test mapping high score to status"""
        assert iris_agent._map_status(0.8) == AgentStatus.COMPLETED
    
    def test_map_status_medium_score(self, iris_agent):
        """Test mapping medium score to status"""
        assert iris_agent._map_status(0.5) == AgentStatus.COMPLETED
    
    def test_map_status_low_score(self, iris_agent):
        """Test mapping low score to status"""
        assert iris_agent._map_status(0.2) == AgentStatus.ERROR


class TestIrisAgentConfidenceCalculation:
    """Tests for confidence calculation"""
    
    def test_calculate_confidence_normal(self, iris_agent):
        """Test confidence calculation with normal result"""
        result = {
            "trajectory_smoothness": 0.9,
            "blink_rate": 15,
        }
        confidence = iris_agent._calculate_confidence(result)
        assert 0.0 <= confidence <= 1.0
        assert confidence >= 0.8  # Should be high confidence
    
    def test_calculate_confidence_low_blink_rate(self, iris_agent):
        """Test confidence calculation with low blink rate"""
        result = {
            "trajectory_smoothness": 0.9,
            "blink_rate": 3,
        }
        confidence = iris_agent._calculate_confidence(result)
        assert confidence < 0.8  # Should reduce confidence
    
    def test_calculate_confidence_high_blink_rate(self, iris_agent):
        """Test confidence calculation with high blink rate"""
        result = {
            "trajectory_smoothness": 0.9,
            "blink_rate": 35,
        }
        confidence = iris_agent._calculate_confidence(result)
        assert confidence < 0.8  # Should reduce confidence
    
    def test_calculate_confidence_low_smoothness(self, iris_agent):
        """Test confidence calculation with low smoothness"""
        result = {
            "trajectory_smoothness": 0.3,
            "blink_rate": 15,
        }
        confidence = iris_agent._calculate_confidence(result)
        assert confidence < 0.5  # Should be low confidence


class TestIrisAgentOutputValidation:
    """Tests for output validation"""
    
    @patch.object(IrisAgent, '_call_wasm_module')
    def test_validate_output_valid(self, mock_call_wasm, iris_agent):
        """Test validating valid output"""
        mock_call_wasm.return_value = {
            "liveness_score": 85.0,
            "trajectory_smoothness": 0.9,
            "blink_rate": 15,
            "fixation_count": 10,
        }
        
        input_data = {
            "eye_vectors": [[0.5, 0.5]] * 100,
            "frame_count": 1000,
            "fps": 30,
        }
        
        result = iris_agent.process(input_data)
        assert iris_agent.validate_output(result) is True
    
    @patch.object(IrisAgent, '_call_wasm_module')
    def test_validate_output_invalid_score(self, mock_call_wasm, iris_agent):
        """Test validating output with invalid score"""
        mock_call_wasm.return_value = {
            "liveness_score": 85.0,
            "trajectory_smoothness": 0.9,
            "blink_rate": 15,
            "fixation_count": 10,
        }
        
        input_data = {
            "eye_vectors": [[0.5, 0.5]] * 100,
            "frame_count": 1000,
            "fps": 30,
        }
        
        result = iris_agent.process(input_data)
        result.score = 1.5  # Invalid score
        assert iris_agent.validate_output(result) is False
    
    @patch.object(IrisAgent, '_call_wasm_module')
    def test_validate_output_missing_field(self, mock_call_wasm, iris_agent):
        """Test validating output with missing field"""
        mock_call_wasm.return_value = {
            "liveness_score": 85.0,
            "trajectory_smoothness": 0.9,
            "blink_rate": 15,
            "fixation_count": 10,
        }
        
        input_data = {
            "eye_vectors": [[0.5, 0.5]] * 100,
            "frame_count": 1000,
            "fps": 30,
        }
        
        result = iris_agent.process(input_data)
        del result.data["blink_rate"]
        assert iris_agent.validate_output(result) is False
