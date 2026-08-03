import { useState, useRef, useEffect } from 'react';
import { useDashboardStore } from '../store/useDashboardStore';
import { VideoOff, Maximize, Minimize, Volume2, VolumeX } from 'lucide-react';

export function VideoFeed() {
  const { selectedCandidate } = useDashboardStore();
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isVideoConnected] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isFullscreen && containerRef.current) {
      containerRef.current.requestFullscreen?.();
    } else if (!isFullscreen && document.fullscreenElement) {
      document.exitFullscreen?.();
    }
  }, [isFullscreen]);

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  if (!selectedCandidate) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Video Feed</h3>
        <p className="text-gray-500">No candidate selected</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Video Feed</h3>
          <p className="text-sm text-gray-500">{selectedCandidate.name}</p>
        </div>
        <div className="flex items-center gap-2">
          {isVideoConnected ? (
            <span className="badge badge-success flex items-center gap-1">
              <span className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
              Live
            </span>
          ) : (
            <span className="badge badge-danger">Disconnected</span>
          )}
        </div>
      </div>

      <div
        ref={containerRef}
        className={`relative bg-gray-900 rounded-lg overflow-hidden ${
          isFullscreen ? 'fixed inset-0 z-50' : 'aspect-video'
        }`}
      >
        {isVideoConnected ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted={isMuted}
            className="w-full h-full object-cover"
          >
            <source src="" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <VideoOff className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">Video feed unavailable</p>
            </div>
          </div>
        )}

        {/* Video Controls Overlay */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={toggleMute}
                className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
              >
                {isMuted ? (
                  <VolumeX className="w-5 h-5 text-white" />
                ) : (
                  <Volume2 className="w-5 h-5 text-white" />
                )}
              </button>
              
              <div className="text-white text-sm">
                <span className="font-medium">00:00</span>
                <span className="mx-1">/</span>
                <span className="text-gray-300">00:00</span>
              </div>
            </div>

            <button
              onClick={toggleFullscreen}
              className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
            >
              {isFullscreen ? (
                <Minimize className="w-5 h-5 text-white" />
              ) : (
                <Maximize className="w-5 h-5 text-white" />
              )}
            </button>
          </div>
        </div>

        {/* Session Info Overlay */}
        <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-sm rounded-lg px-3 py-2">
          <p className="text-white text-sm font-medium">
            Session: {selectedCandidate.sessionId}
          </p>
          <p className="text-gray-300 text-xs">
            {selectedCandidate.role}
          </p>
        </div>
      </div>
    </div>
  );
}
