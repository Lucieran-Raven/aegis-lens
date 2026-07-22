# ECHO - Acoustic Time-of-Flight Analysis

ECHO is a high-performance acoustic time-of-flight measurement and analysis engine for interview sessions. It measures audio characteristics and uses spectral analysis to detect potential replay attacks or synthetic speech.

## Features

- **Acoustic time-of-flight measurement**: Microsecond-level timing analysis
- **Spectral analysis**: Spectral centroid and zero-crossing rate calculation
- **Anomaly detection**: Clear, Suspect, or Anomaly status classification
- **Cross-platform**: Native Rust with WebAssembly support
- **Real-time**: Continuous measurement with sliding window (1000 samples)
- **Zero-PII**: No personal data collected, only acoustic metrics

## Installation

### Rust (Native)

Add to your `Cargo.toml`:

```toml
[dependencies]
echo = { path = "../packages/echo" }
```

### JavaScript (WASM)

```bash
npm install @aegis-lens/echo-js
```

## Usage

### Rust

```rust
use echo::EchoEngine;

// Create engine
let mut engine = EchoEngine::new_native();

// Measure time-of-flight samples
for _ in 0..100 {
    let tof = engine.measure_native();
    println!("TOF: {}ms", tof);
}

// Analyze results
let result = engine.analyze_native();
println!("Score: {}", result.score);
println!("Status: {}", result.status);
```

### JavaScript

```javascript
import { initEcho, measureToF, analyze } from '@aegis-lens/echo-js';

// Initialize
await initEcho();

// Measure time-of-flight
for (let i = 0; i < 100; i++) {
    measureToF();
}

// Analyze
const result = analyze();
console.log('Score:', result.score);
console.log('Status:', result.status);
```

### Browser

```html
<script type="module">
  import { initEcho, measureToF, analyze } from '@aegis-lens/echo-js';

  // Initialize
  await window.Echo.init();

  // Measure
  window.Echo.measure();
  
  // Analyze
  const result = window.Echo.analyze();
  console.log(result);
</script>
```

## API Reference

### EchoEngine

#### `new_native()`
Creates a new EchoEngine for native environments.

#### `new()`
Creates a new EchoEngine for WASM environments.

#### `measure_native() -> f64`
Measures a single time-of-flight sample and returns the value in milliseconds.

#### `measure() -> f64`
WASM-compatible version of `measure_native()`.

#### `analyze_native() -> EchoResult`
Performs full acoustic analysis and returns the result.

#### `analyze() -> JsValue`
WASM-compatible version of `analyze_native()`.

#### `sample_count() -> usize`
Returns the current number of samples in the window.

#### `clear()`
Clears all samples from the window.

### EchoResult

```rust
pub struct EchoResult {
    pub score: f64,              // 0.0 to 1.0, higher is better
    pub status: String,          // "CLEAR", "SUSPECT", "ANOMALY", "INSUFFICIENT_DATA"
    pub mean_tof: f64,           // Mean time-of-flight in milliseconds
    pub std_tof: f64,            // Standard deviation
    pub spectral_centroid: f64,  // Spectral centroid (0-1)
    pub zero_crossing_rate: f64, // Zero crossing rate
    pub sample_count: usize,     // Number of samples analyzed
}
```

## Status Classification

- **CLEAR** (score > 0.8): Normal acoustic patterns, no anomalies detected
- **SUSPECT** (0.5 < score ≤ 0.8): Some irregularities, warrants attention
- **ANOMALY** (score ≤ 0.5): Significant anomalies detected
- **INSUFFICIENT_DATA** (sample_count < 10): Not enough samples for analysis

## Building

### Rust

```bash
cd packages/echo
cargo build --release
cargo test
```

### WASM

```bash
cd packages/echo
./build.sh
```

Or manually:

```bash
cargo install wasm-pack
rustup target add wasm32-unknown-unknown
wasm-pack build --target web --out-dir pkg --release
```

### JavaScript

```bash
cd packages/echo/js
npm install
npm test
```

## Testing

### Rust Tests

```bash
cd packages/echo
cargo test
```

### JavaScript Tests

```bash
cd packages/echo/js
npm test
```

## Performance

- **Measurement overhead**: ~100ns per sample
- **Analysis time**: ~40μs for 1000 samples
- **Full workflow**: ~15μs for 100 samples
- **Sample count query**: ~400ps
- **Clear operation**: ~50μs
- **Memory usage**: ~8KB for 1000 samples
- **WASM size**: ~38KB (gzipped)

## Architecture

ECHO uses a sliding window approach with a fixed-size buffer (1000 samples). Each measurement captures the time-of-flight of audio signals, representing the acoustic characteristics.

### Acoustic Analysis

1. **Mean TOF**: Average time-of-flight
2. **Standard Deviation**: Measure of variability
3. **Spectral Centroid**: Frequency distribution center of mass
4. **Zero Crossing Rate**: Signal frequency indicator

### Scoring Algorithm

```
score = 1.0 - penalties
- TOF deviation penalty: -0.3
- Variance penalty: -0.2
- Spectral centroid penalty: -0.2
- Zero crossing rate penalty: -0.2
- Sample count penalty: -0.1
```

## Security & Privacy

- **Zero-PII**: No personal data collected
- **Local processing**: All analysis happens client-side
- **No network calls**: No data transmission
- **Open source**: Fully auditable code

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `cargo test` and `npm test`
5. Submit a pull request

## Support

For issues, questions, or contributions, please open an issue on the repository.
