# AEGIS LENS

**Physics-Based HR Intelligence Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/aegis-lens/aegis-lens)
[![Platform](https://img.shields.io/badge/platform-web--assembly-blue)](https://webassembly.org/)

---

## Overview

Aegis Lens is a cutting-edge HR intelligence platform that combines physics-based detection with AI-powered behavioral analysis to ensure interview integrity and candidate authenticity.

### Core Technology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHYSICS PIPELINES (Rust → WASM)                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  CHRONOS  │ Frame-Timing Entropy Detection                                 │
│  ECHO     │ Acoustic Time-of-Flight Analysis                               │
│  IRIS     │ Corneal Reflection Parallax Detection                           │
│  LIPSYNC  │ AV-Sync Drift Analysis                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  AI AGENTS (Python/FastAPI)                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  CHRONOS  │ Hardware Integrity Agent                                        │
│  ECHO     │ Audio Integrity Agent                                           │
│  IRIS     │ Visual Liveness Agent                                           │
│  LIPSYNC  │ Media Integrity Agent                                           │
│  NOVA     │ Behavioral Linguistics Agent                                    │
│  SENTIENT │ Micro-Expression + Gaze Agent                                   │
│  AURA     │ Physiological Proxies Agent                                     │
│  KAI      │ Knowledge Acquisition Agent                                     │
│  SPIDER   │ Web Intelligence Agent                                          │
│  ORACLE   │ Question Generation Agent                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Bayesian Engine for Trust Score Calculation & Verdict Generation          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Features

- **Physics-Based Detection**: 4 independent pipelines detect VM/emulator usage
- **AI-Powered Analysis**: 10 specialized agents analyze behavioral patterns
- **Real-Time Processing**: WebAssembly for high-performance client-side analysis
- **Zero-PII Architecture**: Privacy-first design with no personal data storage
- **Enterprise-Grade**: Scalable microservices architecture with Kubernetes
- **Comprehensive Dashboard**: Real-time HR analytics and candidate insights

---

## Architecture

```
aegis-lens/
├── packages/
│   ├── chronos/          # Frame-timing entropy (Rust → WASM)
│   ├── echo/              # Acoustic time-of-flight (Rust → WASM)
│   ├── iris/              # Corneal reflection (Rust → WASM)
│   ├── lipsync/           # AV-sync drift (Rust → WASM)
│   ├── nova/              # Behavioral linguistics (Python/FastAPI)
│   ├── sentient/          # Micro-expression + gaze (Python/FastAPI)
│   ├── aura/              # Physiological proxies (Python/FastAPI)
│   ├── kai/               # Knowledge acquisition (Python/FastAPI)
│   ├── spider/            # Web intelligence (Python/FastAPI)
│   ├── oracle/            # Question generation (Python/FastAPI)
│   ├── orchestrator/      # Bayesian engine (Python/FastAPI)
│   ├── signaling/         # WebRTC signaling server (Node.js)
│   ├── candidate-ui/      # Candidate interview interface (React)
│   └── hr-dashboard/      # HR analytics dashboard (React)
├── docker/                # Docker configurations
├── kubernetes/            # Kubernetes manifests
└── docs/                  # Documentation
```

---

## Technology Stack

### Physics Pipelines
- **Rust** for high-performance computation
- **WebAssembly** for browser execution
- **wasm-bindgen** for JavaScript interop

### AI Agents
- **Python 3.11+** for AI/ML processing
- **FastAPI** for REST APIs
- **PyTorch** for deep learning models
- **spaCy** for NLP processing
- **OpenCV + MediaPipe** for computer vision
- **Neo4j** for knowledge graphs

### Frontend
- **React 18+** with TypeScript
- **WebRTC** for real-time video/audio
- **Socket.io** for real-time communication
- **TailwindCSS** for styling

### Infrastructure
- **Docker** for containerization
- **Kubernetes** for orchestration
- **Redis** for caching and pub/sub
- **PostgreSQL** for relational data
- **TimescaleDB** for time-series metrics
- **Neo4j** for graph data

---

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- Rust 1.70+
- Docker Desktop
- Kubernetes (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/aegis-lens/aegis-lens.git
cd aegis-lens

# Install dependencies
npm install
pip install -r requirements.txt

# Start infrastructure
docker-compose up -d

# Start development servers
npm run dev
```

---

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

### Running Tests

```bash
# Run all tests
npm test

# Run physics pipeline tests
cd packages/chronos && cargo test

# Run AI agent tests
cd packages/nova && pytest
```

---

## Security

Aegis Lens follows a Zero-PII architecture:
- No personal data is stored
- All processing is done in real-time
- Encrypted communication via TLS
- Role-based access control
- Regular security audits

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

- **Website**: https://aegis-lens.io
- **Documentation**: https://docs.aegis-lens.io
- **Issues**: https://github.com/aegis-lens/aegis-lens/issues

---

## Acknowledgments

Built with ❤️ for ensuring interview integrity and fair hiring practices.
