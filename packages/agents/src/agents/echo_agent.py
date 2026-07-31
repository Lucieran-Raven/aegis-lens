"""
ECHO Agent - Audio Delay Detection Agent

This agent analyzes audio delay patterns to detect potential manipulation
or inconsistencies in the candidate's response timing.
"""

import json
import subprocess
import logging
from typing import Dict, Any
from pathlib import Path

from src.base import BaseAgent, AgentConfig, AgentResult, AgentStatus


class EchoAgent(BaseAgent):
    """
    ECHO agent for detecting audio delay in audio streams.
    
    This agent uses the ECHO WASM module to analyze audio delay patterns
    and detect anomalies that may indicate manipulation or deception.
    """
    
    def __init__(self, config: AgentConfig, wasm_path: str = None):
        """
        Initialize ECHO agent.
        
        Args:
            config: Agent configuration
            wasm_path: Path to ECHO WASM module directory
        """
        super().__init__(config)
        self.wasm_path = wasm_path or self._find_wasm_path()
        self.logger.info(f"ECHO agent initialized with WASM path: {self.wasm_path}")
    
    def _find_wasm_path(self) -> str:
        """
        Find the ECHO WASM module path.
        
        Returns:
            Path to ECHO WASM module
        """
        # Try to find ECHO package relative to this file
        current_dir = Path(__file__).parent.parent.parent.parent
        possible_paths = [
            current_dir / "echo" / "pkg",
            current_dir / "packages" / "echo" / "pkg",
            Path("/app/echo/pkg"),  # Docker path
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "echo.js").exists():
                return str(path)
        
        raise FileNotFoundError(
            "ECHO WASM module not found. "
            "Please ensure the ECHO package is built."
        )
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data for ECHO agent.
        
        Expected input:
        - audio_samples: List of audio sample values
        - sample_rate: Audio sample rate (Hz)
        - reference_chirp: Reference chirp signal (optional)
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["audio_samples", "sample_rate"]
        
        # Check required fields
        for field in required_fields:
            if field not in input_data:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Validate audio_samples
        audio_samples = input_data["audio_samples"]
        if not isinstance(audio_samples, list) or len(audio_samples) < 100:
            self.logger.error("audio_samples must be a list with at least 100 elements")
            return False
        
        # Validate sample_rate
        sample_rate = input_data["sample_rate"]
        if not isinstance(sample_rate, (int, float)) or sample_rate <= 0:
            self.logger.error("sample_rate must be a positive number")
            return False
        
        return True
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Process audio data with ECHO WASM module.
        
        Args:
            input_data: Input data with audio_samples and sample_rate
            
        Returns:
            AgentResult with delay analysis
        """
        try:
            # Prepare input for WASM module
            wasm_input = {
                "samples": input_data["audio_samples"],
                "sampleRate": input_data["sample_rate"],
                "referenceChirp": input_data.get("reference_chirp", None),
            }
            
            # Call WASM module via Node.js
            result = self._call_wasm_module(wasm_input)
            
            # Normalize score (0-1)
            normalized_score = self._normalize_score(result.get("delay_score", 0))
            
            # Map status
            status = self._map_status(normalized_score)
            
            return AgentResult(
                agent_id=self.config.agent_id,
                status=status,
                score=normalized_score,
                confidence=self._calculate_confidence(result),
                data={
                    "delay_score": result.get("delay_score", 0),
                    "delay_ms": result.get("delay_ms", 0),
                    "threshold_crossed": result.get("threshold_crossed", False),
                    "signal_quality": result.get("signal_quality", 0),
                },
                metadata={
                    "wasm_version": "0.1.0",
                    "input_length": len(input_data["audio_samples"]),
                    "sample_rate": input_data["sample_rate"],
                },
            )
            
        except Exception as e:
            self.logger.error(f"ECHO processing failed: {str(e)}")
            raise
    
    def _call_wasm_module(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call ECHO WASM module via Node.js.
        
        Args:
            input_data: Input data for WASM module
            
        Returns:
            Result from WASM module
        """
        # Create a temporary Node.js script to run the WASM module
        script = f"""
const Echo = require('{self.wasm_path}/echo.js');
const input = {json.dumps(input_data)};

async function run() {{
    try {{
        const result = await Echo.analyze_delay(input.samples, input.sampleRate, input.referenceChirp);
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
        Normalize raw delay score to 0-1 range.
        
        Higher delay indicates more potential manipulation.
        
        Args:
            raw_score: Raw delay score from WASM
            
        Returns:
            Normalized score (0-1)
        """
        # Clamp to reasonable range (0-500ms)
        clamped = max(0, min(raw_score, 500))
        
        # Normalize to 0-1
        normalized = clamped / 500.0
        
        return normalized
    
    def _map_status(self, score: float) -> AgentStatus:
        """
        Map score to agent status.
        
        Args:
            score: Normalized score (0-1)
            
        Returns:
            AgentStatus
        """
        if score < 0.2:
            return AgentStatus.COMPLETED
        elif score < 0.5:
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
        # Base confidence on signal quality
        signal_quality = result.get("signal_quality", 0.5)
        
        # Higher confidence with better signal quality
        confidence = signal_quality
        
        # Reduce confidence if threshold was crossed
        if result.get("threshold_crossed", False):
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
        required_fields = ["delay_score", "delay_ms", "threshold_crossed", "signal_quality"]
        for field in required_fields:
            if field not in result.data:
                return False
        
        return True
