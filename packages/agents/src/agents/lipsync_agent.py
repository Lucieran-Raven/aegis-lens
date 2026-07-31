"""
LIPSYNC Agent - Lip Synchronization Detection Agent

This agent analyzes lip synchronization between audio and video streams
to detect potential manipulation or deepfake content.
"""

import json
import subprocess
import logging
from typing import Dict, Any
from pathlib import Path

from src.base import BaseAgent, AgentConfig, AgentResult, AgentStatus


class LipsyncAgent(BaseAgent):
    """
    LIPSYNC agent for detecting lip synchronization between audio and video.

    This agent uses the LIPSYNC WASM module to analyze audio-visual
    synchronization and detect anomalies that may indicate manipulation
    or deepfake content.
    """

    def __init__(self, config: AgentConfig, wasm_path: str = None):
        """
        Initialize LIPSYNC agent.

        Args:
            config: Agent configuration
            wasm_path: Path to LIPSYNC WASM module directory
        """
        super().__init__(config)
        self.wasm_path = wasm_path or self._find_wasm_path()
        self.logger.info(f"LIPSYNC agent initialized with WASM path: {self.wasm_path}")

    def _find_wasm_path(self) -> str:
        """
        Find the LIPSYNC WASM module path.

        Returns:
            Path to LIPSYNC WASM module
        """
        # Try to find LIPSYNC package relative to this file
        current_dir = Path(__file__).parent.parent.parent.parent
        possible_paths = [
            current_dir / "lipsync" / "pkg",
            current_dir / "packages" / "lipsync" / "pkg",
            Path("/app/lipsync/pkg"),  # Docker path
        ]

        for path in possible_paths:
            if path.exists() and (path / "lipsync.js").exists():
                return str(path)

        raise FileNotFoundError(
            "LIPSYNC WASM module not found. " "Please ensure the LIPSYNC package is built."
        )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data for LIPSYNC agent.

        Expected input:
        - audio_features: List of audio feature vectors (MFCCs, etc.)
        - video_features: List of video feature vectors (mouth landmarks)
        - sync_data: List of timestamp pairs for audio-video alignment

        Args:
            input_data: Input data to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["audio_features", "video_features", "sync_data"]

        # Check required fields
        for field in required_fields:
            if field not in input_data:
                self.logger.error(f"Missing required field: {field}")
                return False

        # Validate audio_features
        audio_features = input_data["audio_features"]
        if not isinstance(audio_features, list) or len(audio_features) < 10:
            self.logger.error("audio_features must be a list with at least 10 elements")
            return False

        # Validate video_features
        video_features = input_data["video_features"]
        if not isinstance(video_features, list) or len(video_features) < 10:
            self.logger.error("video_features must be a list with at least 10 elements")
            return False

        # Validate sync_data
        sync_data = input_data["sync_data"]
        if not isinstance(sync_data, list) or len(sync_data) < 10:
            self.logger.error("sync_data must be a list with at least 10 elements")
            return False

        # Check that audio and video features have matching lengths
        if len(audio_features) != len(video_features):
            self.logger.error(
                f"audio_features and video_features must have same length: "
                f"{len(audio_features)} != {len(video_features)}"
            )
            return False

        return True

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Process audio-video synchronization data with LIPSYNC WASM module.

        Args:
            input_data: Input data with audio_features, video_features, and sync_data

        Returns:
            AgentResult with synchronization analysis
        """
        try:
            # Prepare input for WASM module
            wasm_input = {
                "audioFeatures": input_data["audio_features"],
                "videoFeatures": input_data["video_features"],
                "syncData": input_data["sync_data"],
            }

            # Call WASM module via Node.js
            result = self._call_wasm_module(wasm_input)

            # Normalize score (0-1)
            normalized_score = self._normalize_score(result.get("sync_score", 0))

            # Map status
            status = self._map_status(normalized_score)

            return AgentResult(
                agent_id=self.config.agent_id,
                status=status,
                score=normalized_score,
                confidence=self._calculate_confidence(result),
                data={
                    "sync_score": result.get("sync_score", 0),
                    "sync_error": result.get("sync_error", 0),
                    "phoneme_match_rate": result.get("phoneme_match_rate", 0),
                    "mouth_openness_variance": result.get("mouth_openness_variance", 0),
                },
                metadata={
                    "wasm_version": "0.1.0",
                    "input_length": len(input_data["audio_features"]),
                    "audio_feature_dim": (
                        len(input_data["audio_features"][0]) if input_data["audio_features"] else 0
                    ),
                    "video_feature_dim": (
                        len(input_data["video_features"][0]) if input_data["video_features"] else 0
                    ),
                },
            )

        except Exception as e:
            self.logger.error(f"LIPSYNC processing failed: {str(e)}")
            raise

    def _call_wasm_module(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call LIPSYNC WASM module via Node.js.

        Args:
            input_data: Input data for WASM module

        Returns:
            Result from WASM module
        """
        # Create a temporary Node.js script to run the WASM module
        script = f"""
const Lipsync = require('{self.wasm_path}/lipsync.js');
const input = {json.dumps(input_data)};

async function run() {{
    try {{
        const result = await Lipsync.analyze_sync(
            input.audioFeatures,
            input.videoFeatures,
            input.syncData
        );
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
        Normalize raw sync score to 0-1 range.

        Higher sync score indicates better audio-video synchronization.

        Args:
            raw_score: Raw sync score from WASM

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
        # Base confidence on phoneme match rate
        phoneme_match = result.get("phoneme_match_rate", 0.5)

        # Higher confidence with better phoneme matching
        confidence = phoneme_match

        # Reduce confidence if sync error is high
        sync_error = result.get("sync_error", 0)
        if sync_error > 50:
            confidence -= 0.2
        elif sync_error > 30:
            confidence -= 0.1

        # Reduce confidence if mouth openness variance is abnormal
        variance = result.get("mouth_openness_variance", 0)
        if variance > 100:
            confidence -= 0.1

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
        required_fields = [
            "sync_score",
            "sync_error",
            "phoneme_match_rate",
            "mouth_openness_variance",
        ]
        for field in required_fields:
            if field not in result.data:
                return False

        return True
