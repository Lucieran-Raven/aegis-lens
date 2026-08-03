import { useEffect, useRef, useCallback, useState } from 'react';
import { useDashboardStore } from '../store/useDashboardStore';

interface WebSocketMessage {
  type: 'candidate_update' | 'agent_status' | 'intelligence' | 'question' | 'scoring' | 'transcript' | 'heartbeat';
  data: any;
  timestamp: string;
}

export function useWebSocket(url: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const heartbeatIntervalRef = useRef<NodeJS.Timeout>();
  const messageQueueRef = useRef<any[]>([]);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 10;
  
  const [lastMessageTime, setLastMessageTime] = useState<Date | null>(null);
  
  const { setConnected, updateAgentStatus, addIntelligenceItem, addQuestion, updateScoringMetrics, updateCandidate } = useDashboardStore();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setConnected(true);
        reconnectAttemptsRef.current = 0;
        
        // Send queued messages
        while (messageQueueRef.current.length > 0) {
          const message = messageQueueRef.current.shift();
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
          }
        }
        
        // Start heartbeat
        startHeartbeat();
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessageTime(new Date());
          
          // Handle heartbeat response
          if (message.type === 'heartbeat') {
            return;
          }
          
          handleMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        setConnected(false);
        stopHeartbeat();
        
        // Exponential backoff reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const backoffDelay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          reconnectAttemptsRef.current++;
          
          console.log(`Reconnection attempt ${reconnectAttemptsRef.current} in ${backoffDelay}ms`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, backoffDelay);
        } else {
          console.error('Max reconnection attempts reached');
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
    }
  }, [url, setConnected]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    messageQueueRef.current = [];
    reconnectAttemptsRef.current = 0;
    setConnected(false);
  }, [setConnected]);

  const startHeartbeat = useCallback(() => {
    heartbeatIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'heartbeat', timestamp: new Date().toISOString() }));
      }
    }, 30000); // Send heartbeat every 30 seconds
  }, []);

  const stopHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected, queuing message');
      messageQueueRef.current.push(message);
    }
  }, []);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'candidate_update':
        if (message.data.id) {
          updateCandidate(message.data.id, message.data);
        }
        break;
      
      case 'agent_status':
        if (message.data.name) {
          updateAgentStatus(message.data.name, {
            name: message.data.name,
            status: message.data.status,
            lastUpdate: new Date(message.timestamp),
            metrics: message.data.metrics,
          });
        }
        break;
      
      case 'intelligence':
        addIntelligenceItem({
          id: message.data.id || Date.now().toString(),
          type: message.data.type,
          severity: message.data.severity,
          message: message.data.message,
          timestamp: new Date(message.timestamp),
          sessionId: message.data.sessionId,
        });
        break;
      
      case 'question':
        addQuestion({
          id: message.data.id || Date.now().toString(),
          text: message.data.text,
          suggestedBy: message.data.suggestedBy,
          status: message.data.status || 'pending',
          timestamp: new Date(message.timestamp),
        });
        break;
      
      case 'scoring':
        updateScoringMetrics(message.data);
        break;
      
      case 'transcript':
        // Handle transcript updates
        console.log('Transcript update:', message.data);
        break;
      
      default:
        console.warn('Unknown message type:', message.type);
    }
  }, [updateCandidate, updateAgentStatus, addIntelligenceItem, addQuestion, updateScoringMetrics]);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    sendMessage,
    disconnect,
    lastMessageTime,
  };
}
