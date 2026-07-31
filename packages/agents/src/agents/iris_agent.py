"""
IRIS Agent - Eye Tracking and Liveness Detection Agent

This agent analyzes eye movement patterns to detect potential manipulation
or inconsistencies in the candidate's behavior.
"""

import json
import subprocess
import logging
from typing import Dict, Any
from pathlib import Path

from src.base import BaseAgent, AgentConfig, AgentResult, AgentStatus


class IrisAgent(BaseAgent):
    """
    IRIS agent for detecting eye movement patterns and liveness.
    
    This agent uses the IRIS WASM module to analyze eye tracking data
    and detect anomalies that may indicate manipulation or deception.
    """
    
    def __init__(self, config: AgentConfig, wasm_path: str = None):
        """
        Initialize IRIS agent.
        
        Args:
            config: Agent configuration
            wasm_path: Path to IRIS WASM module directory
        """
        super().__init__(config)
        self.wasm_path = wasm_path or self._find_wasm_path()
        self.logger.info(f"IRIS agent initialized with WASM path: {self.wasm_path}")
    
    def _find_wasm_path(self) -> str:
        """
        Find the IRIS WASM module path.
        
        Returns:
            Path to IRIS WASM module
        """
        # Try to find IRIS package relative to this file
        current_dir = Path(__file__).parent.parent.parent.parent
        possible_paths = [
            current_dir / "iris" / "pkg",
            current_dir / "packages" / "iris" / "pkg",
            Path("/app/iris/pkg"),  # Docker path
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "iris.js").exists():
                return str(path)
        
        raise FileNotFoundError(
            "IRIS WASM module not found. "
            "Please ensure the IRIS package is built."
        )
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data for IRIS agent.
        
        Expected input:
        - eye_vectors: List of eye tracking vectors
        - frame_count: Number of video frames
        - fps: Video frame rate
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["eye_vectors", "frame_count", "fps"]
        
        # Check required fields
        for field in required_fields:
            if field not in input_data:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Validate eye_vectors
        eye_vectors = input_data["eye_vectors"]
        if not isinstance(eye_vectors, list) or len(eye_vectors) < 10:
            self.logger.error("eye_vectors must be a list with at least 10 elements")
            return False
        
        # Validate frame_count
        frame_count = input_data["frame_count"]
        if not isinstance(frame_count, int) or frame_count <= 0:
            self.logger.error("frame_count must be a positive integer")
            return False
        
        # Validate fps
        fps = input_data["fps"]
        if not isinstance(fps, (int, float)) or fps <= 0:
            self.logger.error("fps must be a positive number")
            return False
        
        return True
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Process eye tracking data with IRIS WASM module.
        
        Args:
            input_data: Input data with eye_vectors, frame_count, and fps
            
        Returns:
            AgentResult with trajectory analysis
        """
        try:
            # Prepare input for WASM module
            wasm_input = {
                "vectors": input_data["eye_vectors"],
                "frameCount": input_data["frame_count"],
                "fps": input_data["fps"],
            }
            
            # Call WASM module via Node.js
            result = self._call_wasm_module(wasm_input)
            
            # Normalize score (0-1)
            normalized_score = self._normalize_score(result.get("liveness_score", 0))
            
            # Map status
            status = self._map_status(normalized_score)
            
            return AgentResult(
                agent_id=self.config.agent_id,
                status=status,
                score=normalized_score,
                confidence=self._calculate_confidence(result),
                data={
                    "liveness_score": result.get("liveness_score", 0),
                    "trajectory_smoothness": result.get("trajectory_smoothness", 0),
                    "blink_rate": result.get("blink_rate", 0),
                    "fixation_count": result.get("fixation_count", 0),
                },
                metadata={
                    "wasm_version": "0.1.0",
                    "input_length": len(input_data["eye_vectors"]),
                    "frame_count": input_data["frame_count"],
                    "fps": input_data["fps"],
                },
            )
            
        except Exception as e:
            self.logger.error(f"IRIS processing failed: {str(e)}")
            raise
    
    def _call_wasm_module(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call IRIS WASM module via Node.js.
        
        Args:
            input_data: Input data for WASM module
            
        Returns:
            Result from WASM module
        """
        # Create a temporary Node.js script to run the WASM module
        script = f"""
const Iris = require('{self.wasm_path}/iris.js');
const input = {json.dumps(input_data)};

async function run() {{
    try {{
        const result = await Iris.analyze_vectors(input.vectors, input.frameCount, input.fps);
        console.log(JSON.stringify(result));
    }} catch (error) {{
        console.error(JSON.stringify({{error: error.message}}));
        process.exit(1);
    }}
}}

run();
"""
        
        try:
            # Run Node.js script
            result = subprocess.run(
                ["node", "-e", script],
                capture_output=True,
                text=True,
                timeout=self.config.timeout_ms / 1000,
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"WASM execution failed: {result.stderr}")
            
            return json.loads(result.stdout)
            
        except subprocess.TimeoutExpired:
            raise TimeoutError("WASM execution timed out")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse WASM output: {str(e)}")
    
    def _normalize_score(self, raw_score: float) -> float:
        """
        Normalize raw liveness score to 0-1 range.
        
        Higher liveness score indicates more authentic behavior.
        
        Args:
            raw_score: Raw liveness score from WASM
            
        Returns:
            Normalized score (0-1)
        """
        # Clamp to reasonable range (0-100)
        clamped = max(0, min(raw_score, 100))
        
        # Normalize to 0-1
        normalized = clamped / 100.0
        
        return normalized
    
    def _map_status(self, score: float) -> AgentStatus:
        """
        Map score to agent status.
        
        Args:
            score: Normalized score (0-1)
            
        Returns:
            AgentStatus
        """
        if score >= 0.7:
            return AgentStatus.COMPLETED
        elif score >= 0.3:
            return AgentStatus.COMPLETED
        else:
            return AgentStatus.ERROR
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """
        Calculate confidence based on result quality.
        
        Args:
            result: Result from WASM module
            
        Returns:
            Confidence score (0-1)
        """
        # Base confidence on trajectory smoothness
        smoothness = result.get("trajectory_smoothness", 0.5)
        
        # Higher confidence with smoother trajectories
        confidence = smoothness
        
        # Reduce confidence if blink rate is abnormal
        blink_rate = result.get("blink_rate", 15)
        if blink_rate < 5 or blink_rate > 30:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def validate_output(self, result: AgentResult) -> bool:
        """
        Validate output result.
        
        Args:
            result: Result to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check score range
        if not 0.0 <= result.score <= 1.0:
            return False
        
        # Check confidence range
        if not 0.0 <= result.confidence <= 1.0:
            return False
        
        # Check required data fields
        required_fields = ["liveness_score", "trajectory_smoothness", "blink_rate", "fixation_count"]
        for field in required_fields:
            if field not in result.data:
                return False
        
        return True
