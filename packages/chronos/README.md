# CHRONOS - Jitter Measurement & Anomaly Detection

CHRONOS is a high-performance timing measurement and anomaly detection engine for interview sessions. It measures response time jitter and uses statistical analysis to detect potential anomalies that may indicate deception or stress.

## Features

- **High-precision timing**: Microsecond-level jitter measurement
- **Statistical analysis**: Mean, standard deviation, Shapiro-Wilk test, KL divergence
- **Anomaly detection**: Clear, Suspect, or Anomaly status classification
- **Cross-platform**: Native Rust with WebAssembly support
- **Real-time**: Continuous measurement with sliding window (1000 samples)
- **Zero-PII**: No personal data collected, only timing metrics

## Installation

### Rust (Native)

Add to your `Cargo.toml`:

```toml
[dependencies]
chronos = { path = "../packages/chronos" }
```

### JavaScript (WASM)

```bash
npm install @aegis-lens/chronos-js
```

## Usage

### Rust

```rust
use chronos::ChronosEngine;

// Create engine
let mut engine = ChronosEngine::new_native();

// Measure jitter samples
for _ in 0..100 {
    let jitter = engine.measure_native();
    println!("Jitter: {}ms", jitter);
}

// Analyze results
let result = engine.analyze_native();
println!("Score: {}", result.score);
println!("Status: {}", result.status);
```

### JavaScript

```javascript
import { initChronos, measureJitter, analyze } from '@aegis-lens/chronos-js';

// Initialize
await initChronos();

// Measure jitter
for (let i = 0; i < 100; i++) {
    measureJitter();
}

// Analyze
const result = analyze();
console.log('Score:', result.score);
console.log('Status:', result.status);
```

### Browser

```html
<script type="module">
  import { initChronos, measureJitter, analyze } from '@aegis-lens/chronos-js';

  // Initialize
  await window.Chronos.init();

  // Measure
  window.Chronos.measure();
  
  // Analyze
  const result = window.Chronos.analyze();
  console.log(result);
</script>
```

## API Reference

### ChronosEngine

#### `new_native()`
Creates a new ChronosEngine for native environments.

#### `new()`
Creates a new ChronosEngine for WASM environments.

#### `measure_native() -> f64`
Measures a single timing sample and returns the jitter value in milliseconds.

#### `measure() -> f64`
WASM-compatible version of `measure_native()`.

#### `analyze_native() -> ChronosResult`
Performs full statistical analysis and returns the result.

#### `analyze() -> JsValue`
WASM-compatible version of `analyze_native()`.

#### `sample_count() -> usize`
Returns the current number of samples in the window.

#### `clear()`
Clears all samples from the window.

### ChronosResult

```rust
pub struct ChronosResult {
    pub score: f64,           // 0.0 to 1.0, higher is better
    pub status: String,       // "CLEAR", "SUSPECT", "ANOMALY", "INSUFFICIENT_DATA"
    pub mean_jitter: f64,     // Mean jitter in milliseconds
    pub std_jitter: f64,      // Standard deviation
    pub shapiro_w: f64,       // Shapiro-Wilk statistic
    pub kl_divergence: f64,   // KL divergence from normal distribution
    pub sample_count: usize,  // Number of samples analyzed
}
```

## Status Classification

- **CLEAR** (score > 0.7): Normal jitter patterns, no anomalies detected
- **SUSPECT** (0.4 < score ≤ 0.7): Some irregularities, warrants attention
- **ANOMALY** (score ≤ 0.4): Significant anomalies detected
- **INSUFFICIENT_DATA** (sample_count < 10): Not enough samples for analysis

## Building

### Rust

```bash
cd packages/chronos
cargo build --release
cargo test
```

### WASM

```bash
cd packages/chronos
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
cd packages/chronos/js
npm install
npm test
```

## Testing

### Rust Tests

```bash
cd packages/chronos
cargo test
```

### JavaScript Tests

```bash
cd packages/chronos/js
npm test
```

## Performance

- **Measurement overhead**: < 1μs per sample
- **Analysis time**: < 1ms for 1000 samples
- **Memory usage**: ~8KB for 1000 samples
- **WASM size**: ~36KB (gzipped)

## Architecture

CHRONOS uses a sliding window approach with a fixed-size buffer (1000 samples). Each measurement captures the time difference between consecutive calls, representing the jitter in response timing.

### Statistical Analysis

1. **Mean Jitter**: Average of all samples
2. **Standard Deviation**: Measure of variability
3. **Shapiro-Wilk Test**: Normality test (0-1, higher = more normal)
4. **KL Divergence**: Distance from normal distribution

### Scoring Algorithm

```
score = (shapiro_w * 0.4) + (1 - kl_divergence) * 0.3 + (1 / (1 + std_jitter)) * 0.3
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
