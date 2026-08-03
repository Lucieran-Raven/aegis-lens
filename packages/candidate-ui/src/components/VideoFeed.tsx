import { useRef, useEffect, useState } from 'react';
import { Video, VideoOff, AlertCircle } from 'lucide-react';

interface VideoFeedProps {
  stream: MediaStream | null;
  muted?: boolean;
  className?: string;
  placeholder?: string;
}

export function VideoFeed({ stream, muted = false, className = '', placeholder = 'No video signal' }: VideoFeedProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    const videoElement = videoRef.current;
    if (!videoElement) return;

    if (stream) {
      videoElement.srcObject = stream;
      videoElement.muted = muted;

      const handlePlay = () => setIsPlaying(true);
      const handlePause = () => setIsPlaying(false);
      const handleError = () => setHasError(true);

      videoElement.addEventListener('play', handlePlay);
      videoElement.addEventListener('pause', handlePause);
      videoElement.addEventListener('error', handleError);

      videoElement.play().catch((error) => {
        console.error('Error playing video:', error);
        setHasError(true);
      });

      return () => {
        videoElement.removeEventListener('play', handlePlay);
        videoElement.removeEventListener('pause', handlePause);
        videoElement.removeEventListener('error', handleError);
        videoElement.srcObject = null;
      };
    } else {
      videoElement.srcObject = null;
      setIsPlaying(false);
      setHasError(false);
    }
  }, [stream, muted]);

  if (hasError) {
    return (
      <div className={`flex items-center justify-center bg-gray-800 ${className}`}>
        <div className="text-center text-gray-400">
          <AlertCircle className="w-12 h-12 mx-auto mb-2" />
          <p className="text-sm">Video error</p>
        </div>
      </div>
    );
  }

  if (!stream) {
    return (
      <div className={`flex items-center justify-center bg-gray-800 ${className}`}>
        <div className="text-center text-gray-400">
          <VideoOff className="w-12 h-12 mx-auto mb-2" />
          <p className="text-sm">{placeholder}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative bg-black ${className}`}>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted={muted}
        className="w-full h-full object-cover"
      />
      {!isPlaying && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50">
          <Video className="w-12 h-12 text-white" />
        </div>
      )}
    </div>
  );
}
