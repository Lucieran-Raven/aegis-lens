import { WebSocketServer, WebSocket } from 'ws';
import { createServer } from 'http';

interface Client {
  id: string;
  socket: WebSocket;
  roomId?: string;
}

const PORT = process.env.PORT || 8083;
const server = createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'healthy', service: 'signaling' }));
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

const wss = new WebSocketServer({ server });
const clients: Map<string, Client> = new Map();

wss.on('connection', (ws: WebSocket) => {
  const clientId = generateClientId();
  clients.set(clientId, { id: clientId, socket: ws });

  ws.on('message', (data: string) => {
    const message = JSON.parse(data);
    handleMessage(clientId, message);
  });

  ws.on('close', () => {
    clients.delete(clientId);
  });

  ws.send(JSON.stringify({ type: 'connected', clientId }));
});

function generateClientId(): string {
  return Math.random().toString(36).substring(2, 15);
}

function handleMessage(clientId: string, message: any) {
  const client = clients.get(clientId);
  if (!client) return;

  switch (message.type) {
    case 'join-room':
      client.roomId = message.roomId;
      broadcastToRoom(message.roomId, {
        type: 'user-joined',
        clientId,
      });
      break;
    case 'signal':
      if (client.roomId) {
        broadcastToRoom(client.roomId, {
          type: 'signal',
          clientId,
          data: message.data,
        }, clientId);
      }
      break;
  }
}

function broadcastToRoom(roomId: string, message: any, excludeClientId?: string) {
  for (const [id, client] of clients) {
    if (client.roomId === roomId && id !== excludeClientId) {
      client.socket.send(JSON.stringify(message));
    }
  }
}

server.listen(PORT, () => {
  console.log(`Signaling server running on port ${PORT}`);
});
