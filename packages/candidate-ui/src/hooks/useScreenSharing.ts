import { useEffect, useRef, useState, useCallback } from 'react';

interface ScreenSharingConfig {
  onStream?: (stream: MediaStream) => void;
  onError?: (error: Error) => void;
}

interface ScreenSharingState {
  isSharing: boolean;
  isRequesting: boolean;
  error: string | null;
  stream: MediaStream | null;
}

export function useScreenSharing(config: ScreenSharingConfig = {}) {
  const { onStream, onError } = config;
  const [state, setState] = useState<ScreenSharingState>({
    isSharing: false,
    isRequesting: false,
    error: null,
    stream: null,
  });

  const streamRef = useRef<MediaStream | null>(null);

  const startSharing = useCallback(async () => {
    try {
      setState((prev) => ({ ...prev, isRequesting: true, error: null }));

      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          displaySurface: 'monitor',
        } as MediaTrackConstraints,
        audio: false,
      });

      streamRef.current = stream;

      // Handle stream end (user clicked "Stop sharing")
      stream.getVideoTracks()[0].onended = () => {
        stopSharing();
      };

      setState((prev) => ({
        ...prev,
        isSharing: true,
        isRequesting: false,
        stream,
      }));

      onStream?.(stream);
    } catch (error) {
      console.error('Error starting screen sharing:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to start screen sharing';
      setState((prev) => ({
        ...prev,
        isRequesting: false,
        error: errorMessage,
      }));
      onError?.(error instanceof Error ? error : new Error(errorMessage));
    }
  }, [onStream, onError]);

  const stopSharing = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    setState((prev) => ({
      ...prev,
      isSharing: false,
      stream: null,
      error: null,
    }));
  }, []);

  const toggleSharing = useCallback(() => {
    if (state.isSharing) {
      stopSharing();
    } else {
      startSharing();
    }
  }, [state.isSharing, startSharing, stopSharing]);

  useEffect(() => {
    return () => {
      stopSharing();
    };
  }, [stopSharing]);

  return {
    ...state,
    startSharing,
    stopSharing,
    toggleSharing,
  };
}
