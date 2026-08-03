# Aegis Lens - Candidate UI

Candidate-facing UI for the Aegis Lens platform, providing a secure and authenticated interview experience with real-time video, audio analysis, and trust scoring.

## Features

- **Real-time Video Conferencing**: WebRTC-based video calls with low latency
- **Picture-in-Picture Self-View**: Draggable, expandable self-view component
- **Audio Processing**: Real-time audio analysis for authenticity detection
- **Physics Integration**: Support for CHRONOS, ECHO, IRIS, and LIPSYNC modules
- **Screen Sharing**: Built-in screen sharing capabilities
- **Trust Score Display**: Real-time trust score visualization
- **Responsive Design**: Mobile-first, responsive UI using Tailwind CSS
- **Error Handling**: Comprehensive error boundary and error states
- **Loading States**: Skeleton loaders and loading overlays

## Tech Stack

- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Zustand**: Lightweight state management
- **React Router DOM**: Client-side routing
- **Lucide React**: Beautiful icon library
- **Vitest**: Unit and integration testing

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd packages/candidate-ui
npm install
```

### Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

### Testing

```bash
npm test
```

## Project Structure

```
src/
├── components/          # React components
│   ├── __tests__/      # Component tests
│   ├── VideoFeed.tsx   # Video feed component
│   ├── SelfView.tsx    # Picture-in-picture self-view
│   ├── QuestionDisplay.tsx  # Question display
│   ├── Controls.tsx    # Control buttons
│   ├── StatusBar.tsx   # Status bar
│   ├── ErrorBoundary.tsx  # Error boundary
│   └── Loading.tsx     # Loading components
├── hooks/              # Custom React hooks
│   ├── useWebRTC.ts    # WebRTC connection management
│   ├── useWebSocket.ts # WebSocket connection
│   ├── useTelemetry.ts # Telemetry data collection
│   ├── usePhysics.ts   # Physics module integration
│   ├── useAudioProcessing.ts  # Audio processing
│   └── useScreenSharing.ts    # Screen sharing
├── routes/             # Route components
│   ├── Join.tsx        # Join session page
│   └── Session.tsx     # Session page
├── store/              # Zustand stores
│   └── useSessionStore.ts  # Session state management
├── test/               # Test configuration
│   └── setup.ts        # Test setup
├── App.tsx             # Main app component
└── index.css           # Global styles
```

## Environment Variables

No environment variables are required for local development. For production, configure the following:

- `VITE_API_URL`: API endpoint URL
- `VITE_WS_URL`: WebSocket URL
- `VITE_SIGNALING_URL`: WebRTC signaling server URL

## Docker Deployment

### Build Docker Image

```bash
docker build -t aegislens/candidate-ui:latest .
```

### Run Container

```bash
docker run -p 80:80 aegislens/candidate-ui:latest
```

### Docker Compose

```yaml
services:
  candidate-ui:
    build: ./packages/candidate-ui
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=http://api:8000
      - VITE_WS_URL=ws://api:8000/ws
```

## CI/CD

The project uses GitHub Actions for CI/CD:

- **Test**: Runs on every push and PR
- **Build**: Builds the application after tests pass
- **Docker**: Builds and pushes Docker images on main/develop branches

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Security

- Content Security Policy headers
- HTTPS required for production
- Secure WebSocket connections
- Input validation and sanitization

## License

Proprietary - All rights reserved
