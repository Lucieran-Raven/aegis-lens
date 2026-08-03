import { create } from 'zustand';

export interface SessionState {
  sessionId: string | null;
  candidateName: string | null;
  isConnected: boolean;
  isRecording: boolean;
  timeRemaining: number;
  currentQuestion: string | null;
  questionIndex: number;
  totalQuestions: number;
}

export interface MediaState {
  isCameraEnabled: boolean;
  isMicrophoneEnabled: boolean;
  isScreenSharing: boolean;
  cameraStream: MediaStream | null;
  microphoneStream: MediaStream | null;
  screenStream: MediaStream | null;
}

export interface TelemetryState {
  chronosScore: number | null;
  echoScore: number | null;
  irisScore: number | null;
  lipsyncScore: number | null;
  overallTrustScore: number | null;
  lastUpdate: number | null;
}

export interface ConnectionState {
  websocketConnected: boolean;
  webrtcConnected: boolean;
  signalingConnected: boolean;
  latency: number;
}

interface SessionStore extends SessionState {
  setSessionId: (sessionId: string) => void;
  setCandidateName: (name: string) => void;
  setConnected: (connected: boolean) => void;
  setRecording: (recording: boolean) => void;
  setTimeRemaining: (time: number) => void;
  setCurrentQuestion: (question: string) => void;
  nextQuestion: () => void;
  resetSession: () => void;
}

interface MediaStore extends MediaState {
  setCameraEnabled: (enabled: boolean) => void;
  setMicrophoneEnabled: (enabled: boolean) => void;
  setScreenSharing: (sharing: boolean) => void;
  setCameraStream: (stream: MediaStream | null) => void;
  setMicrophoneStream: (stream: MediaStream | null) => void;
  setScreenStream: (stream: MediaStream | null) => void;
  resetMedia: () => void;
}

interface TelemetryStore extends TelemetryState {
  setChronosScore: (score: number) => void;
  setEchoScore: (score: number) => void;
  setIrisScore: (score: number) => void;
  setLipsyncScore: (score: number) => void;
  setOverallTrustScore: (score: number) => void;
  updateTelemetry: (data: Partial<TelemetryState>) => void;
  resetTelemetry: () => void;
}

interface ConnectionStore extends ConnectionState {
  setWebsocketConnected: (connected: boolean) => void;
  setWebrtcConnected: (connected: boolean) => void;
  setSignalingConnected: (connected: boolean) => void;
  setLatency: (latency: number) => void;
  resetConnection: () => void;
}

export const useSessionStore = create<SessionStore>((set) => ({
  sessionId: null,
  candidateName: null,
  isConnected: false,
  isRecording: false,
  timeRemaining: 3600,
  currentQuestion: null,
  questionIndex: 0,
  totalQuestions: 10,
  setSessionId: (sessionId) => set({ sessionId }),
  setCandidateName: (candidateName) => set({ candidateName }),
  setConnected: (isConnected) => set({ isConnected }),
  setRecording: (isRecording) => set({ isRecording }),
  setTimeRemaining: (timeRemaining) => set({ timeRemaining }),
  setCurrentQuestion: (currentQuestion) => set({ currentQuestion }),
  nextQuestion: () => set((state) => ({
    questionIndex: state.questionIndex + 1,
  })),
  resetSession: () => set({
    sessionId: null,
    candidateName: null,
    isConnected: false,
    isRecording: false,
    timeRemaining: 3600,
    currentQuestion: null,
    questionIndex: 0,
  }),
}));

export const useMediaStore = create<MediaStore>((set) => ({
  isCameraEnabled: false,
  isMicrophoneEnabled: false,
  isScreenSharing: false,
  cameraStream: null,
  microphoneStream: null,
  screenStream: null,
  setCameraEnabled: (isCameraEnabled) => set({ isCameraEnabled }),
  setMicrophoneEnabled: (isMicrophoneEnabled) => set({ isMicrophoneEnabled }),
  setScreenSharing: (isScreenSharing) => set({ isScreenSharing }),
  setCameraStream: (cameraStream) => set({ cameraStream }),
  setMicrophoneStream: (microphoneStream) => set({ microphoneStream }),
  setScreenStream: (screenStream) => set({ screenStream }),
  resetMedia: () => set({
    isCameraEnabled: false,
    isMicrophoneEnabled: false,
    isScreenSharing: false,
    cameraStream: null,
    microphoneStream: null,
    screenStream: null,
  }),
}));

export const useTelemetryStore = create<TelemetryStore>((set) => ({
  chronosScore: null,
  echoScore: null,
  irisScore: null,
  lipsyncScore: null,
  overallTrustScore: null,
  lastUpdate: null,
  setChronosScore: (chronosScore) => set({ chronosScore }),
  setEchoScore: (echoScore) => set({ echoScore }),
  setIrisScore: (irisScore) => set({ irisScore }),
  setLipsyncScore: (lipsyncScore) => set({ lipsyncScore }),
  setOverallTrustScore: (overallTrustScore) => set({ overallTrustScore }),
  updateTelemetry: (data) => set((state) => ({
    ...state,
    ...data,
    lastUpdate: Date.now(),
  })),
  resetTelemetry: () => set({
    chronosScore: null,
    echoScore: null,
    irisScore: null,
    lipsyncScore: null,
    overallTrustScore: null,
    lastUpdate: null,
  }),
}));

export const useConnectionStore = create<ConnectionStore>((set) => ({
  websocketConnected: false,
  webrtcConnected: false,
  signalingConnected: false,
  latency: 0,
  setWebsocketConnected: (websocketConnected) => set({ websocketConnected }),
  setWebrtcConnected: (webrtcConnected) => set({ webrtcConnected }),
  setSignalingConnected: (signalingConnected) => set({ signalingConnected }),
  setLatency: (latency) => set({ latency }),
  resetConnection: () => set({
    websocketConnected: false,
    webrtcConnected: false,
    signalingConnected: false,
    latency: 0,
  }),
}));
