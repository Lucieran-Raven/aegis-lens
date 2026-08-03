import { useEffect, useRef, useState, useCallback } from 'react';

interface WebRTCConfig {
  signalingUrl: string;
  sessionId: string;
  onStream?: (stream: MediaStream) => void;
  onDataChannel?: (data: any) => void;
}

interface WebRTCState {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  localStream: MediaStream | null;
  remoteStream: MediaStream | null;
}

export function useWebRTC(config: WebRTCConfig) {
  const [state, setState] = useState<WebRTCState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    localStream: null,
    remoteStream: null,
  });

  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);

  const createPeerConnection = useCallback(() => {
    const pc = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
      ],
    });

    pc.onicecandidate = (event) => {
      if (event.candidate) {
        // Send ICE candidate via signaling server
        console.log('ICE candidate:', event.candidate);
      }
    };

    pc.onconnectionstatechange = () => {
      console.log('Connection state:', pc.connectionState);
      setState((prev) => ({
        ...prev,
        isConnected: pc.connectionState === 'connected',
      }));
    };

    pc.ontrack = (event) => {
      console.log('Received remote track');
      const remoteStream = new MediaStream();
      event.streams[0].getTracks().forEach((track) => {
        remoteStream.addTrack(track);
      });
      setState((prev) => ({ ...prev, remoteStream }));
      config.onStream?.(remoteStream);
    };

    return pc;
  }, [config]);

  const connect = useCallback(async () => {
    try {
      setState((prev) => ({ ...prev, isConnecting: true, error: null }));

      // Get local media stream
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });

      localStreamRef.current = stream;
      setState((prev) => ({ ...prev, localStream: stream }));

      // Create peer connection
      const pc = createPeerConnection();
      peerConnectionRef.current = pc;

      // Add local tracks to peer connection
      stream.getTracks().forEach((track) => {
        pc.addTrack(track, stream);
      });

      // Create data channel
      const dataChannel = pc.createDataChannel('telemetry');
      dataChannelRef.current = dataChannel;

      dataChannel.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          config.onDataChannel?.(data);
        } catch (error) {
          console.error('Error parsing data channel message:', error);
        }
      };

      // Create offer
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      // Send offer via signaling server
      console.log('Sending offer:', offer);

      setState((prev) => ({ ...prev, isConnecting: false }));
    } catch (error) {
      console.error('WebRTC connection error:', error);
      setState((prev) => ({
        ...prev,
        isConnecting: false,
        error: error instanceof Error ? error.message : 'Connection failed',
      }));
    }
  }, [config, createPeerConnection]);

  const disconnect = useCallback(() => {
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }

    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach((track) => track.stop());
      localStreamRef.current = null;
    }

    if (dataChannelRef.current) {
      dataChannelRef.current.close();
      dataChannelRef.current = null;
    }

    setState({
      isConnected: false,
      isConnecting: false,
      error: null,
      localStream: null,
      remoteStream: null,
    });
  }, []);

  const sendData = useCallback((data: any) => {
    if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
      dataChannelRef.current.send(JSON.stringify(data));
    }
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    ...state,
    connect,
    disconnect,
    sendData,
  };
}
