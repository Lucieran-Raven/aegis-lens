import { useEffect, useRef, useState, useCallback } from 'react';

interface PhysicsModule {
  chronos?: any;
  echo?: any;
  iris?: any;
  lipsync?: any;
}

interface PhysicsResult {
  chronos?: number;
  echo?: number;
  iris?: number;
  lipsync?: number;
  timestamp: number;
}

interface PhysicsConfig {
  enabled?: boolean;
  wasmPath?: string;
  onResult?: (result: PhysicsResult) => void;
}

export function usePhysics(config: PhysicsConfig = {}) {
  const { enabled = true, wasmPath = '/wasm/', onResult } = config;
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const modulesRef = useRef<PhysicsModule>({});
  const videoElementRef = useRef<HTMLVideoElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  const initializeModules = useCallback(async () => {
    if (!enabled || isInitialized) return;
    
    try {
      setIsLoading(true);
      setError(null);

      // Load CHRONOS module (Frame-Timing Entropy)
      try {
        const chronosModule = await import(`${wasmPath}chronos`);
        modulesRef.current.chronos = chronosModule;
        console.log('CHRONOS module loaded');
      } catch (e) {
        console.warn('CHRONOS module not available:', e);
      }

      // Load ECHO module (Acoustic Time-of-Flight)
      try {
        const echoModule = await import(`${wasmPath}echo`);
        modulesRef.current.echo = echoModule;
        console.log('ECHO module loaded');
      } catch (e) {
        console.warn('ECHO module not available:', e);
      }

      // Load IRIS module (Corneal Reflection Parallax)
      try {
        const irisModule = await import(`${wasmPath}iris`);
        modulesRef.current.iris = irisModule;
        console.log('IRIS module loaded');
      } catch (e) {
        console.warn('IRIS module not available:', e);
      }

      // Load LIPSYNC module (AV-Sync Drift Analysis)
      try {
        const lipsyncModule = await import(`${wasmPath}lipsync`);
        modulesRef.current.lipsync = lipsyncModule;
        console.log('LIPSYNC module loaded');
      } catch (e) {
        console.warn('LIPSYNC module not available:', e);
      }

      setIsInitialized(true);
    } catch (error) {
      console.error('Error initializing physics modules:', error);
      setError(error instanceof Error ? error.message : 'Initialization failed');
    } finally {
      setIsLoading(false);
    }
  }, [enabled, isInitialized, wasmPath]);

  const analyzeFrame = useCallback(async (videoElement: HTMLVideoElement) => {
    if (!isInitialized || !videoElement) return null;

    videoElementRef.current = videoElement;
    const result: PhysicsResult = { timestamp: Date.now() };

    try {
      // CHRONOS: Frame-Timing Entropy Analysis
      if (modulesRef.current.chronos) {
        const chronosResult = await modulesRef.current.chronos.analyzeFrame(videoElement);
        result.chronos = chronosResult.score;
      }

      // IRIS: Corneal Reflection Parallax Analysis
      if (modulesRef.current.iris) {
        const irisResult = await modulesRef.current.iris.analyzeFrame(videoElement);
        result.iris = irisResult.score;
      }

      onResult?.(result);
      return result;
    } catch (error) {
      console.error('Error analyzing frame:', error);
      return null;
    }
  }, [isInitialized, onResult]);

  const analyzeAudio = useCallback(async (audioBuffer: AudioBuffer) => {
    if (!isInitialized || !audioBuffer) return null;

    const result: PhysicsResult = { timestamp: Date.now() };

    try {
      // ECHO: Acoustic Time-of-Flight Analysis
      if (modulesRef.current.echo) {
        const echoResult = await modulesRef.current.echo.analyzeAudio(audioBuffer);
        result.echo = echoResult.score;
      }

      onResult?.(result);
      return result;
    } catch (error) {
      console.error('Error analyzing audio:', error);
      return null;
    }
  }, [isInitialized, onResult]);

  const analyzeSync = useCallback(async (videoElement: HTMLVideoElement, audioBuffer: AudioBuffer) => {
    if (!isInitialized || !videoElement || !audioBuffer) return null;

    const result: PhysicsResult = { timestamp: Date.now() };

    try {
      // LIPSYNC: AV-Sync Drift Analysis
      if (modulesRef.current.lipsync) {
        const lipsyncResult = await modulesRef.current.lipsync.analyzeSync(videoElement, audioBuffer);
        result.lipsync = lipsyncResult.score;
      }

      onResult?.(result);
      return result;
    } catch (error) {
      console.error('Error analyzing sync:', error);
      return null;
    }
  }, [isInitialized, onResult]);

  const startAudioContext = useCallback(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    return audioContextRef.current;
  }, []);

  useEffect(() => {
    initializeModules();

    return () => {
      // Cleanup
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [initializeModules]);

  return {
    isInitialized,
    isLoading,
    error,
    analyzeFrame,
    analyzeAudio,
    analyzeSync,
    startAudioContext,
  };
}
