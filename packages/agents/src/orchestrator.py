"""
Agent Orchestrator - Coordinates multiple agents and aggregates results
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from src.base import BaseAgent, AgentConfig, AgentResult, AgentStatus


class OrchestratorStrategy(Enum):
    """Strategies for orchestrating multiple agents"""
    SEQUENTIAL = "sequential"  # Run agents one after another
    PARALLEL = "parallel"  # Run all agents simultaneously
    PRIORITY_BASED = "priority_based"  # Run based on agent priority
    CONDITIONAL = "conditional"  # Run based on conditions


@dataclass
class OrchestratorConfig:
    """Configuration for agent orchestrator"""
    orchestrator_id: str
    strategy: OrchestratorStrategy = OrchestratorStrategy.SEQUENTIAL
    timeout_ms: int = 30000
    max_retries: int = 3
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    log_level: str = "INFO"
    required_agents: List[str] = field(default_factory=list)
    optional_agents: List[str] = field(default_factory=list)
    aggregation_method: str = "weighted_average"  # weighted_average, majority_vote, min, max


@dataclass
class OrchestratorResult:
    """Result from orchestrator execution"""
    orchestrator_id: str
    status: AgentStatus
    overall_score: float
    overall_confidence: float
    agent_results: Dict[str, AgentResult] = field(default_factory=dict)
    aggregated_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class AgentOrchestrator:
    """
    Orchestrator for coordinating multiple agents.
    
    This class manages the execution of multiple agents, aggregates their results,
    and provides a unified interface for multi-agent analysis.
    """

    def __init__(self, config: OrchestratorConfig):
        """
        Initialize agent orchestrator.
        
        Args:
            config: Orchestrator configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"orchestrator.{config.orchestrator_id}")
        self.logger.setLevel(getattr(logging, config.log_level.upper()))
        
        self.agents: Dict[str, BaseAgent] = {}
        self.logger.info(f"Orchestrator {config.orchestrator_id} initialized with strategy {config.strategy}")

    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent: Agent to register
        """
        self.agents[agent.config.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.config.agent_id}")

    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent from the orchestrator.
        
        Args:
            agent_id: ID of agent to unregister
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent: {agent_id}")

    def validate_agents(self) -> bool:
        """
        Validate that required agents are registered.
        
        Returns:
            True if all required agents are registered, False otherwise
        """
        for agent_id in self.config.required_agents:
            if agent_id not in self.agents:
                self.logger.error(f"Required agent not registered: {agent_id}")
                return False
        return True

    def execute(self, input_data: Dict[str, Any]) -> OrchestratorResult:
        """
        Execute all registered agents and aggregate results.
        
        Args:
            input_data: Input data for agents
            
        Returns:
            OrchestratorResult with aggregated results
        """
        if not self.validate_agents():
            return OrchestratorResult(
                orchestrator_id=self.config.orchestrator_id,
                status=AgentStatus.ERROR,
                overall_score=0.0,
                overall_confidence=0.0,
                error_message="Required agents not registered"
            )

        try:
            # Execute based on strategy
            if self.config.strategy == OrchestratorStrategy.SEQUENTIAL:
                agent_results = self._execute_sequential(input_data)
            elif self.config.strategy == OrchestratorStrategy.PARALLEL:
                agent_results = self._execute_parallel(input_data)
            elif self.config.strategy == OrchestratorStrategy.PRIORITY_BASED:
                agent_results = self._execute_priority_based(input_data)
            else:
                agent_results = self._execute_sequential(input_data)

            # Aggregate results
            overall_score, overall_confidence, aggregated_data = self._aggregate_results(agent_results)

            # Determine overall status
            overall_status = self._determine_overall_status(agent_results)

            return OrchestratorResult(
                orchestrator_id=self.config.orchestrator_id,
                status=overall_status,
                overall_score=overall_score,
                overall_confidence=overall_confidence,
                agent_results=agent_results,
                aggregated_data=aggregated_data,
                metadata={
                    "strategy": self.config.strategy.value,
                    "agents_executed": len(agent_results),
                    "aggregation_method": self.config.aggregation_method,
                }
            )

        except Exception as e:
            self.logger.error(f"Orchestrator execution failed: {str(e)}")
            return OrchestratorResult(
                orchestrator_id=self.config.orchestrator_id,
                status=AgentStatus.ERROR,
                overall_score=0.0,
                overall_confidence=0.0,
                error_message=str(e)
            )

    def _execute_sequential(self, input_data: Dict[str, Any]) -> Dict[str, AgentResult]:
        """
        Execute agents sequentially.
        
        Args:
            input_data: Input data for agents
            
        Returns:
            Dictionary of agent results
        """
        results = {}
        for agent_id in self.config.required_agents + self.config.optional_agents:
            if agent_id in self.agents:
                try:
                    result = self.agents[agent_id].execute(input_data)
                    results[agent_id] = result
                    self.logger.info(f"Agent {agent_id} executed: {result.status}")
                except Exception as e:
                    self.logger.error(f"Agent {agent_id} execution failed: {str(e)}")
                    # Continue with other agents even if one fails
        return results

    def _execute_parallel(self, input_data: Dict[str, Any]) -> Dict[str, AgentResult]:
        """
        Execute agents in parallel.
        
        Args:
            input_data: Input data for agents
            
        Returns:
            Dictionary of agent results
        """
        import concurrent.futures
        
        results = {}
        
        def execute_agent(agent_id: str) -> tuple:
            if agent_id in self.agents:
                try:
                    result = self.agents[agent_id].execute(input_data)
                    return agent_id, result
                except Exception as e:
                    self.logger.error(f"Agent {agent_id} execution failed: {str(e)}")
                    return agent_id, None
            return agent_id, None

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(execute_agent, agent_id)
                for agent_id in self.config.required_agents + self.config.optional_agents
                if agent_id in self.agents
            ]
            
            for future in concurrent.futures.as_completed(futures):
                agent_id, result = future.result()
                if result:
                    results[agent_id] = result
                    self.logger.info(f"Agent {agent_id} executed: {result.status}")

        return results

    def _execute_priority_based(self, input_data: Dict[str, Any]) -> Dict[str, AgentResult]:
        """
        Execute agents based on priority.
        
        Args:
            input_data: Input data for agents
            
        Returns:
            Dictionary of agent results
        """
        # Sort agents by priority (high > medium > low)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        
        agent_ids = self.config.required_agents + self.config.optional_agents
        agent_ids = [aid for aid in agent_ids if aid in self.agents]
        agent_ids.sort(key=lambda aid: priority_order.get(self.agents[aid].config.priority, 999))
        
        results = {}
        for agent_id in agent_ids:
            try:
                result = self.agents[agent_id].execute(input_data)
                results[agent_id] = result
                self.logger.info(f"Agent {agent_id} executed: {result.status}")
            except Exception as e:
                self.logger.error(f"Agent {agent_id} execution failed: {str(e)}")
        
        return results

    def _aggregate_results(self, agent_results: Dict[str, AgentResult]) -> tuple:
        """
        Aggregate results from multiple agents.
        
        Args:
            agent_results: Dictionary of agent results
            
        Returns:
            Tuple of (overall_score, overall_confidence, aggregated_data)
        """
        if not agent_results:
            return 0.0, 0.0, {}

        method = self.config.aggregation_method
        
        if method == "weighted_average":
            return self._aggregate_weighted_average(agent_results)
        elif method == "majority_vote":
            return self._aggregate_majority_vote(agent_results)
        elif method == "min":
            return self._aggregate_min(agent_results)
        elif method == "max":
            return self._aggregate_max(agent_results)
        else:
            return self._aggregate_weighted_average(agent_results)

    def _aggregate_weighted_average(self, agent_results: Dict[str, AgentResult]) -> tuple:
        """
        Aggregate using weighted average based on confidence.
        
        Args:
            agent_results: Dictionary of agent results
            
        Returns:
            Tuple of (overall_score, overall_confidence, aggregated_data)
        """
        total_weight = 0.0
        weighted_score = 0.0
        weighted_confidence = 0.0
        
        for result in agent_results.values():
            weight = result.confidence
            weighted_score += result.score * weight
            weighted_confidence += result.confidence * weight
            total_weight += weight
        
        if total_weight > 0:
            overall_score = weighted_score / total_weight
            overall_confidence = weighted_confidence / total_weight
        else:
            overall_score = 0.0
            overall_confidence = 0.0
        
        aggregated_data = {
            "method": "weighted_average",
            "agent_count": len(agent_results),
            "total_weight": total_weight,
        }
        
        return overall_score, overall_confidence, aggregated_data

    def _aggregate_majority_vote(self, agent_results: Dict[str, AgentResult]) -> tuple:
        """
        Aggregate using majority vote on status.
        
        Args:
            agent_results: Dictionary of agent results
            
        Returns:
            Tuple of (overall_score, overall_confidence, aggregated_data)
        """
        status_counts = {}
        for result in agent_results.values():
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        majority_status = max(status_counts, key=status_counts.get) if status_counts else "error"
        
        # Calculate average score and confidence for majority status
        majority_results = [r for r in agent_results.values() if r.status.value == majority_status]
        if majority_results:
            overall_score = sum(r.score for r in majority_results) / len(majority_results)
            overall_confidence = sum(r.confidence for r in majority_results) / len(majority_results)
        else:
            overall_score = 0.0
            overall_confidence = 0.0
        
        aggregated_data = {
            "method": "majority_vote",
            "agent_count": len(agent_results),
            "status_counts": status_counts,
            "majority_status": majority_status,
        }
        
        return overall_score, overall_confidence, aggregated_data

    def _aggregate_min(self, agent_results: Dict[str, AgentResult]) -> tuple:
        """
        Aggregate using minimum score (most conservative).
        
        Args:
            agent_results: Dictionary of agent results
            
        Returns:
            Tuple of (overall_score, overall_confidence, aggregated_data)
        """
        if not agent_results:
            return 0.0, 0.0, {}
        
        overall_score = min(r.score for r in agent_results.values())
        overall_confidence = min(r.confidence for r in agent_results.values())
        
        aggregated_data = {
            "method": "min",
            "agent_count": len(agent_results),
        }
        
        return overall_score, overall_confidence, aggregated_data

    def _aggregate_max(self, agent_results: Dict[str, AgentResult]) -> tuple:
        """
        Aggregate using maximum score (most optimistic).
        
        Args:
            agent_results: Dictionary of agent results
            
        Returns:
            Tuple of (overall_score, overall_confidence, aggregated_data)
        """
        if not agent_results:
            return 0.0, 0.0, {}
        
        overall_score = max(r.score for r in agent_results.values())
        overall_confidence = max(r.confidence for r in agent_results.values())
        
        aggregated_data = {
            "method": "max",
            "agent_count": len(agent_results),
        }
        
        return overall_score, overall_confidence, aggregated_data

    def _determine_overall_status(self, agent_results: Dict[str, AgentResult]) -> AgentStatus:
        """
        Determine overall status based on agent results.
        
        Args:
            agent_results: Dictionary of agent results
            
        Returns:
            Overall AgentStatus
        """
        if not agent_results:
            return AgentStatus.ERROR
        
        # Check if any required agent failed
        for agent_id in self.config.required_agents:
            if agent_id in agent_results and agent_results[agent_id].status == AgentStatus.ERROR:
                return AgentStatus.ERROR
        
        # If all required agents completed, return completed
        return AgentStatus.COMPLETED
