import { useEffect, useRef, useState, useCallback } from 'react';

interface AudioProcessingConfig {
  enabled?: boolean;
  bufferSize?: number;
  onAudioData?: (data: Float32Array) => void;
  onAudioBuffer?: (buffer: AudioBuffer) => void;
}

interface AudioProcessingState {
  isActive: boolean;
  volume: number;
  frequency: number;
}

export function useAudioProcessing(config: AudioProcessingConfig = {}) {
  const { enabled = true, bufferSize = 4096, onAudioData, onAudioBuffer } = config;
  const [state, setState] = useState<AudioProcessingState>({
    isActive: false,
    volume: 0,
    frequency: 0,
  });

  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const calculateVolume = useCallback((dataArray: Uint8Array) => {
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      sum += dataArray[i] * dataArray[i];
    }
    const rms = Math.sqrt(sum / dataArray.length);
    return (rms / 255) * 100;
  }, []);

  const calculateFrequency = useCallback((analyser: AnalyserNode, dataArray: Uint8Array) => {
    analyser.getByteFrequencyData(dataArray as Uint8Array<ArrayBuffer>);
    let maxIndex = 0;
    let maxValue = 0;
    for (let i = 0; i < dataArray.length; i++) {
      if (dataArray[i] > maxValue) {
        maxValue = dataArray[i];
        maxIndex = i;
      }
    }
    const nyquist = audioContextRef.current?.sampleRate || 44100;
    return (maxIndex * nyquist) / dataArray.length / 2;
  }, []);

  const startProcessing = useCallback(async (stream: MediaStream) => {
    if (!enabled) return;

    try {
      streamRef.current = stream;

      // Create audio context
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioContext;

      // Create analyser
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;
      analyserRef.current = analyser;

      // Create source from stream
      const source = audioContext.createMediaStreamSource(stream);
      sourceRef.current = source;

      // Connect source to analyser
      source.connect(analyser);

      // Create script processor for audio data
      const processor = audioContext.createScriptProcessor(bufferSize, 1, 1);
      processorRef.current = processor;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      processor.onaudioprocess = (event) => {
        if (!analyserRef.current) return;

        const inputData = event.inputBuffer.getChannelData(0);
        onAudioData?.(inputData);

        // Calculate volume
        analyserRef.current.getByteTimeDomainData(dataArray);
        const volume = calculateVolume(dataArray);

        // Calculate frequency
        const frequency = calculateFrequency(analyserRef.current, dataArray);

        setState((prev) => ({
          ...prev,
          volume,
          frequency,
        }));

        // Send audio buffer periodically
        if (onAudioBuffer && Math.random() < 0.1) {
          const buffer = audioContext.createBuffer(1, inputData.length, audioContext.sampleRate);
          buffer.copyToChannel(inputData, 0);
          onAudioBuffer(buffer);
        }
      };

      // Connect processor
      analyser.connect(processor);
      processor.connect(audioContext.destination);

      setState((prev) => ({ ...prev, isActive: true }));
    } catch (error) {
      console.error('Error starting audio processing:', error);
    }
  }, [enabled, bufferSize, calculateVolume, calculateFrequency, onAudioData, onAudioBuffer]);

  const stopProcessing = useCallback(() => {
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }

    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }

    if (analyserRef.current) {
      analyserRef.current.disconnect();
      analyserRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    streamRef.current = null;
    setState((prev) => ({ ...prev, isActive: false, volume: 0, frequency: 0 }));
  }, []);

  const getAudioBuffer = useCallback(async (duration: number = 1.0): Promise<AudioBuffer | null> => {
    if (!audioContextRef.current || !streamRef.current) return null;

    try {
      const audioContext = audioContextRef.current;
      const stream = streamRef.current;
      const sampleRate = audioContext.sampleRate;
      const length = sampleRate * duration;

      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);

      const buffer = audioContext.createBuffer(1, length, sampleRate);
      const channelData = buffer.getChannelData(0);
      let offset = 0;

      return new Promise((resolve) => {
        processor.onaudioprocess = (event) => {
          const inputData = event.inputBuffer.getChannelData(0);
          for (let i = 0; i < inputData.length && offset < length; i++) {
            channelData[offset++] = inputData[i];
          }

          if (offset >= length) {
            source.disconnect();
            processor.disconnect();
            resolve(buffer);
          }
        };

        source.connect(processor);
        processor.connect(audioContext.destination);
      });
    } catch (error) {
      console.error('Error getting audio buffer:', error);
      return null;
    }
  }, []);

  useEffect(() => {
    return () => {
      stopProcessing();
    };
  }, [stopProcessing]);

  return {
    ...state,
    startProcessing,
    stopProcessing,
    getAudioBuffer,
  };
}
