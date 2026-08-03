import { useDashboardStore } from '../store/useDashboardStore';
import { useWebSocket } from '../hooks/useWebSocket';
import { Header } from '../components/Header';
import { Sidebar } from '../components/Sidebar';
import { TrustScore } from '../components/TrustScore';
import { AgentStatus } from '../components/AgentStatus';
import { IntelligenceFeed } from '../components/IntelligenceFeed';
import { QuestionCoPilot } from '../components/QuestionCoPilot';
import { CandidateAnalytics } from '../components/CandidateAnalytics';
import { VideoFeed } from '../components/VideoFeed';
import { LiveTranscript } from '../components/LiveTranscript';
import { EmotionalDashboard } from '../components/EmotionalDashboard';
import { ContradictionAlerts } from '../components/ContradictionAlerts';
import { RealTimeFactCheck } from '../components/RealTimeFactCheck';
import { QuestionQueue } from '../components/QuestionQueue';
import { ScoringMetrics } from '../components/ScoringMetrics';
import { SessionControls } from '../components/SessionControls';

const WS_URL = (import.meta as any).env.VITE_WS_URL || 'ws://localhost:8080';

export function Dashboard() {
  const { isConnected, selectedCandidate } = useDashboardStore();
  useWebSocket(WS_URL);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="flex">
        <Sidebar />
        
        <main className="flex-1 p-6">
          {!selectedCandidate ? (
            <div className="text-center py-12">
              <h2 className="text-2xl font-semibold text-gray-700 mb-4">
                Select a candidate to view their session
              </h2>
              <p className="text-gray-500">
                Use the sidebar to select an active interview session
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Top Row: Video Feed and Trust Score */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <VideoFeed />
                </div>
                <div>
                  <TrustScore />
                </div>
              </div>

              {/* Second Row: Agent Status and Emotional Dashboard */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <AgentStatus />
                <EmotionalDashboard />
              </div>

              {/* Third Row: Intelligence Feed and Question CoPilot */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <IntelligenceFeed />
                <QuestionCoPilot />
              </div>

              {/* Fourth Row: Candidate Analytics and Scoring Metrics */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <CandidateAnalytics />
                <ScoringMetrics />
              </div>

              {/* Fifth Row: Live Transcript and Contradiction Alerts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <LiveTranscript />
                <ContradictionAlerts />
              </div>

              {/* Sixth Row: Real-time Fact Check and Question Queue */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <RealTimeFactCheck />
                <QuestionQueue />
              </div>

              {/* Session Controls */}
              <SessionControls />
            </div>
          )}
        </main>
      </div>

      {/* Connection Status Indicator */}
      <div className={`fixed bottom-4 right-4 px-4 py-2 rounded-full text-white text-sm font-medium ${
        isConnected ? 'bg-success-500' : 'bg-danger-500'
      }`}>
        {isConnected ? '● Connected' : '● Disconnected'}
      </div>
    </div>
  );
}
