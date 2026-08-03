import { create } from 'zustand';

export interface Candidate {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'pending' | 'interviewing' | 'completed' | 'rejected';
  trustScore: number;
  sessionId: string;
  startTime?: Date;
  endTime?: Date;
}

export interface AgentStatus {
  name: string;
  status: 'idle' | 'running' | 'error';
  lastUpdate: Date;
  metrics?: {
    accuracy?: number;
    latency?: number;
    confidence?: number;
  };
}

export interface IntelligenceItem {
  id: string;
  type: 'contradiction' | 'fact_check' | 'emotion' | 'behavior';
  severity: 'low' | 'medium' | 'high';
  message: string;
  timestamp: Date;
  sessionId: string;
}

export interface Question {
  id: string;
  text: string;
  suggestedBy?: string;
  status: 'pending' | 'asked' | 'answered';
  timestamp: Date;
}

export interface ScoringMetric {
  category: string;
  score: number;
  weight: number;
  details: string[];
}

interface DashboardState {
  // Candidate data
  candidates: Candidate[];
  selectedCandidate: Candidate | null;
  setSelectedCandidate: (candidate: Candidate | null) => void;
  addCandidate: (candidate: Candidate) => void;
  updateCandidate: (id: string, updates: Partial<Candidate>) => void;

  // Agent status
  agentStatuses: Record<string, AgentStatus>;
  updateAgentStatus: (agentName: string, status: AgentStatus) => void;

  // Intelligence feed
  intelligenceFeed: IntelligenceItem[];
  addIntelligenceItem: (item: IntelligenceItem) => void;
  clearIntelligenceFeed: () => void;

  // Question queue
  questionQueue: Question[];
  addQuestion: (question: Question) => void;
  updateQuestion: (id: string, updates: Partial<Question>) => void;

  // Scoring metrics
  scoringMetrics: ScoringMetric[];
  updateScoringMetrics: (metrics: ScoringMetric[]) => void;

  // Connection status
  isConnected: boolean;
  setConnected: (connected: boolean) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  // Candidate data
  candidates: [],
  selectedCandidate: null,
  setSelectedCandidate: (candidate) => set({ selectedCandidate: candidate }),
  addCandidate: (candidate) =>
    set((state) => ({ candidates: [...state.candidates, candidate] })),
  updateCandidate: (id, updates) =>
    set((state) => ({
      candidates: state.candidates.map((c) =>
        c.id === id ? { ...c, ...updates } : c
      ),
    })),

  // Agent status
  agentStatuses: {},
  updateAgentStatus: (agentName, status) =>
    set((state) => ({
      agentStatuses: { ...state.agentStatuses, [agentName]: status },
    })),

  // Intelligence feed
  intelligenceFeed: [],
  addIntelligenceItem: (item) =>
    set((state) => ({ intelligenceFeed: [item, ...state.intelligenceFeed] })),
  clearIntelligenceFeed: () => set({ intelligenceFeed: [] }),

  // Question queue
  questionQueue: [],
  addQuestion: (question) =>
    set((state) => ({ questionQueue: [...state.questionQueue, question] })),
  updateQuestion: (id, updates) =>
    set((state) => ({
      questionQueue: state.questionQueue.map((q) =>
        q.id === id ? { ...q, ...updates } : q
      ),
    })),

  // Scoring metrics
  scoringMetrics: [],
  updateScoringMetrics: (metrics) => set({ scoringMetrics: metrics }),

  // Connection status
  isConnected: false,
  setConnected: (connected) => set({ isConnected: connected }),
}));
