import { describe, it, expect, beforeEach } from 'vitest';
import { useDashboardStore } from '../useDashboardStore';

describe('useDashboardStore', () => {
  beforeEach(() => {
    useDashboardStore.setState({
      candidates: [],
      selectedCandidate: null,
      agentStatuses: {},
      intelligenceFeed: [],
      questionQueue: [],
      scoringMetrics: [],
      connectionStatus: 'disconnected',
    });
  });

  it('initializes with empty state', () => {
    const state = useDashboardStore.getState();
    
    expect(state.candidates).toEqual([]);
    expect(state.selectedCandidate).toBeNull();
    expect(state.agentStatuses).toEqual({});
    expect(state.intelligenceFeed).toEqual([]);
    expect(state.questionQueue).toEqual([]);
    expect(state.scoringMetrics).toEqual([]);
    expect(state.connectionStatus).toBe('disconnected');
  });

  it('adds candidate', () => {
    const candidate = {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      role: 'Developer',
      status: 'interviewing' as const,
      trustScore: 85,
      sessionId: 'session-123',
    };

    useDashboardStore.getState().addCandidate(candidate);
    
    const state = useDashboardStore.getState();
    expect(state.candidates).toHaveLength(1);
    expect(state.candidates[0]).toEqual(candidate);
  });

  it('updates candidate', () => {
    const candidate = {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      role: 'Developer',
      status: 'interviewing' as const,
      trustScore: 85,
      sessionId: 'session-123',
    };

    useDashboardStore.getState().addCandidate(candidate);
    useDashboardStore.getState().updateCandidate('1', { trustScore: 90 });
    
    const state = useDashboardStore.getState();
    expect(state.candidates[0].trustScore).toBe(90);
  });

  it('sets selected candidate', () => {
    const candidate = {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      role: 'Developer',
      status: 'interviewing' as const,
      trustScore: 85,
      sessionId: 'session-123',
    };

    useDashboardStore.getState().setSelectedCandidate(candidate);
    
    const state = useDashboardStore.getState();
    expect(state.selectedCandidate).toEqual(candidate);
  });

  it('adds intelligence item', () => {
    const item = {
      id: '1',
      type: 'contradiction' as const,
      severity: 'high' as const,
      message: 'Test message',
      timestamp: new Date(),
      sessionId: 'session-123',
    };

    useDashboardStore.getState().addIntelligenceItem(item);
    
    const state = useDashboardStore.getState();
    expect(state.intelligenceFeed).toHaveLength(1);
    expect(state.intelligenceFeed[0]).toEqual(item);
  });

  it('clears intelligence feed', () => {
    const item = {
      id: '1',
      type: 'contradiction' as const,
      severity: 'high' as const,
      message: 'Test message',
      timestamp: new Date(),
      sessionId: 'session-123',
    };

    useDashboardStore.getState().addIntelligenceItem(item);
    useDashboardStore.getState().clearIntelligenceFeed();
    
    const state = useDashboardStore.getState();
    expect(state.intelligenceFeed).toEqual([]);
  });

  it('adds question', () => {
    const question = {
      id: '1',
      text: 'Test question',
      suggestedBy: 'HR',
      status: 'pending' as const,
      timestamp: new Date(),
    };

    useDashboardStore.getState().addQuestion(question);
    
    const state = useDashboardStore.getState();
    expect(state.questionQueue).toHaveLength(1);
    expect(state.questionQueue[0]).toEqual(question);
  });

  it('updates question', () => {
    const question = {
      id: '1',
      text: 'Test question',
      suggestedBy: 'HR',
      status: 'pending' as const,
      timestamp: new Date(),
    };

    useDashboardStore.getState().addQuestion(question);
    useDashboardStore.getState().updateQuestion('1', { status: 'asked' });
    
    const state = useDashboardStore.getState();
    expect(state.questionQueue[0].status).toBe('asked');
  });

  it('updates agent status', () => {
    useDashboardStore.getState().updateAgentStatus('Chronos', {
      name: 'Chronos',
      status: 'running',
      lastUpdate: new Date(),
    });
    
    const state = useDashboardStore.getState();
    expect(state.agentStatuses.Chronos.status).toBe('running');
  });

  it('updates connection status', () => {
    useDashboardStore.getState().setConnectionStatus('connected');
    
    const state = useDashboardStore.getState();
    expect(state.connectionStatus).toBe('connected');
  });
});
