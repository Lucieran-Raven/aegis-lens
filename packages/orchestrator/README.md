# Aegis Orchestrator

Bayesian Engine for AI Agent Fusion in Aegis Lens.

## Overview

The Orchestrator is the central intelligence hub that:
- Fuses results from multiple AI agents using Bayesian inference
- Calculates trust scores based on agent reliability
- Generates final verdicts on candidate authenticity
- Provides real-time trend analysis and anomaly detection

## Installation

```bash
pip install -e .
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black src/

# Lint
flake8 src/
```

## Architecture

- **Bayesian Engine**: Probabilistic fusion of agent results
- **Trust Score Calculation**: Dynamic weighting based on agent performance
- **Verdict Generation**: Final authenticity determination
- **Trend Analysis**: Real-time pattern detection
- **Anomaly Detection**: Statistical outlier identification

## License

MIT
