import { useEffect, useRef, useState, useCallback } from 'react';
import { useTelemetryStore } from '../store/useSessionStore';

interface TelemetryData {
  chronosScore?: number;
  echoScore?: number;
  irisScore?: number;
  lipsyncScore?: number;
  overallTrustScore?: number;
  timestamp: number;
}

interface TelemetryConfig {
  enabled?: boolean;
  interval?: number;
  onTelemetryUpdate?: (data: TelemetryData) => void;
}

export function useTelemetry(config: TelemetryConfig = {}) {
  const { enabled = true, interval = 1000, onTelemetryUpdate } = config;
  const [isCollecting, setIsCollecting] = useState(false);
  const [lastData, setLastData] = useState<TelemetryData | null>(null);
  
  const intervalRef = useRef<number | null>(null);
  const updateTelemetry = useTelemetryStore((state) => state.updateTelemetry);

  const startCollection = useCallback(() => {
    if (isCollecting || !enabled) return;
    setIsCollecting(true);

    intervalRef.current = window.setInterval(() => {
      // Simulate telemetry data collection
      const telemetryData: TelemetryData = {
        chronosScore: Math.random() * 100,
        echoScore: Math.random() * 100,
        irisScore: Math.random() * 100,
        lipsyncScore: Math.random() * 100,
        overallTrustScore: Math.random() * 100,
        timestamp: Date.now(),
      };

      setLastData(telemetryData);
      updateTelemetry(telemetryData);
      onTelemetryUpdate?.(telemetryData);
    }, interval);
  }, [isCollecting, enabled, interval, updateTelemetry, onTelemetryUpdate]);

  const stopCollection = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsCollecting(false);
  }, []);

  const sendTelemetry = useCallback((data: Partial<TelemetryData>) => {
    const telemetryData: TelemetryData = {
      ...data,
      timestamp: Date.now(),
    } as TelemetryData;

    setLastData(telemetryData);
    updateTelemetry(telemetryData);
    onTelemetryUpdate?.(telemetryData);
  }, [updateTelemetry, onTelemetryUpdate]);

  useEffect(() => {
    if (enabled) {
      startCollection();
    }

    return () => {
      stopCollection();
    };
  }, [enabled, startCollection, stopCollection]);

  return {
    isCollecting,
    lastData,
    startCollection,
    stopCollection,
    sendTelemetry,
  };
}
