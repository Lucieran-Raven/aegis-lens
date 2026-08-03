import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { VideoFeed } from '../components/VideoFeed';
import { SelfView } from '../components/SelfView';
import { QuestionDisplay } from '../components/QuestionDisplay';
import { Controls } from '../components/Controls';
import { StatusBar } from '../components/StatusBar';
import { LoadingOverlay } from '../components/Loading';
import { useSessionStore, useMediaStore, useTelemetryStore, useConnectionStore } from '../store/useSessionStore';
import { useWebRTC } from '../hooks/useWebRTC';
import { useWebSocket } from '../hooks/useWebSocket';
import { useTelemetry } from '../hooks/useTelemetry';
import { useScreenSharing } from '../hooks/useScreenSharing';

export function Session() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  
  // Store state
  const timeRemaining = useSessionStore((state) => state.timeRemaining);
  const setTimeRemaining = useSessionStore((state) => state.setTimeRemaining);
  const currentQuestion = useSessionStore((state) => state.currentQuestion);
  const questionIndex = useSessionStore((state) => state.questionIndex);
  const totalQuestions = useSessionStore((state) => state.totalQuestions);
  
  const isCameraEnabled = useMediaStore((state) => state.isCameraEnabled);
  const isMicrophoneEnabled = useMediaStore((state) => state.isMicrophoneEnabled);
  const isScreenSharing = useMediaStore((state) => state.isScreenSharing);
  const cameraStream = useMediaStore((state) => state.cameraStream);
  const setCameraEnabled = useMediaStore((state) => state.setCameraEnabled);
  const setMicrophoneEnabled = useMediaStore((state) => state.setMicrophoneEnabled);
  const setScreenSharing = useMediaStore((state) => state.setScreenSharing);
  const setCameraStream = useMediaStore((state) => state.setCameraStream);
  
  const overallTrustScore = useTelemetryStore((state) => state.overallTrustScore);
  const websocketConnected = useConnectionStore((state) => state.websocketConnected);
  const latency = useConnectionStore((state) => state.latency);
  
  // Local state
  const [isLoading, setIsLoading] = useState(true);
  const [remoteStream, setRemoteStream] = useState<MediaStream | null>(null);

  // WebRTC hook
  const { connect: connectWebRTC, disconnect: disconnectWebRTC, isConnected: webrtcConnected } = useWebRTC({
    signalingUrl: 'ws://localhost:8001/signaling',
    sessionId: sessionId || '',
    onStream: (stream) => setRemoteStream(stream),
  });

  // WebSocket hook
  useWebSocket({
    url: 'ws://localhost:8001/ws',
    sessionId: sessionId || '',
    onMessage: (data) => {
      console.log('WebSocket message:', data);
    },
  });

  // Telemetry hook
  useTelemetry({
    enabled: true,
    interval: 1000,
  });

  // Screen sharing hook
  const { startSharing: startScreenShare, stopSharing: stopScreenShare } = useScreenSharing({
    onStream: () => {
      console.log('Screen share started');
    },
  });

  useEffect(() => {
    // Initialize session
    const initSession = async () => {
      try {
        // Get camera stream
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        setCameraStream(stream);
        setCameraEnabled(true);
        setMicrophoneEnabled(true);

        // Connect WebRTC
        await connectWebRTC();

        setIsLoading(false);
      } catch (error) {
        console.error('Error initializing session:', error);
        setIsLoading(false);
      }
    };

    initSession();

    return () => {
      disconnectWebRTC();
    };
  }, [sessionId, connectWebRTC, disconnectWebRTC, setCameraStream, setCameraEnabled, setMicrophoneEnabled]);

  useEffect(() => {
    if (timeRemaining > 0) {
      const timer = setInterval(() => {
        setTimeRemaining(timeRemaining - 1);
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [timeRemaining, setTimeRemaining]);

  const handleEndCall = () => {
    disconnectWebRTC();
    navigate('/');
  };

  const handleToggleCamera = () => {
    setCameraEnabled(!isCameraEnabled);
  };

  const handleToggleMicrophone = () => {
    setMicrophoneEnabled(!isMicrophoneEnabled);
  };

  const handleToggleScreenShare = () => {
    if (isScreenSharing) {
      stopScreenShare();
    } else {
      startScreenShare();
    }
    setScreenSharing(!isScreenSharing);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return <LoadingOverlay text="Connecting to session..." />;
  }

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-4 md:px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2 md:gap-4">
            <h1 className="text-white font-semibold text-sm md:text-base">Aegis Lens</h1>
            <span className="text-gray-400 hidden md:inline">|</span>
            <span className="text-gray-300 text-sm hidden md:inline">Session: {sessionId}</span>
            <span className="text-gray-300 text-sm md:hidden">{sessionId?.slice(0, 8)}...</span>
          </div>
          <div className="flex items-center gap-2 md:gap-4">
            <div className="text-gray-300 text-sm font-mono">
              {formatTime(timeRemaining)}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Video Area */}
        <div className="flex-1 p-4 md:p-6 relative">
          <div className="h-full bg-gray-800 rounded-lg overflow-hidden relative">
            {/* Main Video Feed */}
            <VideoFeed 
              stream={remoteStream} 
              className="w-full h-full"
              placeholder="Waiting for interviewer..."
            />

            {/* Self View (PiP) */}
            <SelfView stream={cameraStream} />
          </div>
        </div>

        {/* Sidebar */}
        <div className="w-full lg:w-80 bg-gray-800 border-t lg:border-t-0 lg:border-l border-gray-700 p-4 md:p-6 overflow-y-auto max-h-96 lg:max-h-full">
          <div className="space-y-4 md:space-y-6">
            {/* Question Display */}
            {currentQuestion && (
              <QuestionDisplay
                question={currentQuestion}
                questionNumber={questionIndex + 1}
                totalQuestions={totalQuestions}
                timeRemaining={timeRemaining}
              />
            )}

            {/* Instructions */}
            <div className="card bg-gray-700">
              <h3 className="text-white font-semibold mb-3 text-sm md:text-base">Instructions</h3>
              <ul className="text-gray-300 text-xs md:text-sm space-y-2">
                <li>• Keep your camera on at all times</li>
                <li>• Speak clearly and at a normal pace</li>
                <li>• Ensure good lighting</li>
                <li>• Minimize background noise</li>
              </ul>
            </div>

            {/* Trust Score */}
            {overallTrustScore !== null && (
              <div className="card bg-gray-700">
                <h3 className="text-white font-semibold mb-3 text-sm md:text-base">Trust Score</h3>
                <div className="flex items-center justify-center">
                  <span className={`text-3xl md:text-4xl font-bold ${
                    overallTrustScore >= 80 ? 'text-success-400' :
                    overallTrustScore >= 60 ? 'text-warning-400' :
                    'text-error-400'
                  }`}>
                    {overallTrustScore}%
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer Controls */}
      <footer className="bg-gray-800 border-t border-gray-700 px-4 md:px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-center gap-2 md:gap-4">
          <Controls
            isCameraEnabled={isCameraEnabled}
            isMicrophoneEnabled={isMicrophoneEnabled}
            isScreenSharing={isScreenSharing}
            onToggleCamera={handleToggleCamera}
            onToggleMicrophone={handleToggleMicrophone}
            onToggleScreenShare={handleToggleScreenShare}
            onEndCall={handleEndCall}
          />
        </div>
      </footer>

      {/* Status Bar */}
      <StatusBar
        isConnected={webrtcConnected || websocketConnected}
        latency={latency}
        trustScore={overallTrustScore || undefined}
      />
    </div>
  );
}
