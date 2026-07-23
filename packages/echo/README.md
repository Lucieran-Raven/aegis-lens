# ECHO - Acoustic Time-of-Flight Analysis

ECHO is a high-performance acoustic time-of-flight measurement and analysis engine for interview sessions. It measures audio characteristics and uses spectral analysis to detect potential replay attacks or synthetic speech.

## Features

- **Acoustic time-of-flight measurement**: Microsecond-level timing analysis
- **Spectral analysis**: Spectral centroid, spectral flux, spectral rolloff, and zero-crossing rate calculation
- **FFT-based cross-correlation**: High-performance signal correlation analysis
- **Chirp generation**: Linear frequency sweep signal generation for audio testing
- **Peak lag detection**: Identify time delays in correlated signals
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

// Generate chirp signal
let config = echo::ChirpConfig {
    start_frequency: 1000.0,
    end_frequency: 8000.0,
    duration: 0.1,
    sample_rate: 44100.0,
};
let chirp = engine.generate_chirp_native(&config);
println!("Generated {} chirp samples", chirp.samples.len());

// FFT cross-correlation
let signal1 = vec![1.0, 2.0, 3.0, 4.0, 5.0];
let signal2 = vec![1.0, 2.0, 3.0, 4.0, 5.0];
let correlation = EchoEngine::cross_correlation_fft_native(&signal1, &signal2);
let (lag, value) = EchoEngine::find_peak_lag_native(&correlation);
println!("Peak lag: {}, value: {}", lag, value);

// Spectral analysis
let signal = vec![1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0];
let fft_data = EchoEngine::compute_fft_native(&signal);
let centroid = EchoEngine::spectral_centroid_native(&fft_data, 44100.0);
let rolloff = EchoEngine::spectral_rolloff_native(&fft_data, 44100.0);
println!("Spectral centroid: {} Hz", centroid);
println!("Spectral rolloff: {} Hz", rolloff);
```

### JavaScript

```javascript
import {
  initEcho,
  measureToF,
  analyze,
  generateChirp,
  crossCorrelationFFT,
  findPeakLag,
  computeSpectralCentroid,
  computeSpectralFlux,
  computeSpectralRolloff
} from '@aegis-lens/echo-js';

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

// Generate chirp signal
const chirp = generateChirp(1000.0, 8000.0, 0.1, 44100.0);
console.log('Generated chirp with', chirp.samples.length, 'samples');

// FFT cross-correlation
const signal1 = new Float32Array([1.0, 2.0, 3.0, 4.0, 5.0]);
const signal2 = new Float32Array([1.0, 2.0, 3.0, 4.0, 5.0]);
const correlation = crossCorrelationFFT(signal1, signal2);
const peak = findPeakLag(correlation);
console.log('Peak lag:', peak.lag, 'value:', peak.value);

// Spectral analysis
const signal = new Float32Array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]);
const centroid = computeSpectralCentroid(signal, 44100.0);
const flux = computeSpectralFlux(signal, signal);
const rolloff = computeSpectralRolloff(signal, 44100.0);
console.log('Spectral centroid:', centroid, 'Hz');
console.log('Spectral flux:', flux);
console.log('Spectral rolloff:', rolloff, 'Hz');
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

  // Generate chirp
  const chirp = window.Echo.generateChirp(1000.0, 8000.0, 0.1, 44100.0);

  // Cross-correlation
  const correlation = window.Echo.crossCorrelationFFT(signal1, signal2);
  const peak = window.Echo.findPeakLag(correlation);

  // Spectral analysis
  const centroid = window.Echo.computeSpectralCentroid(signal, 44100.0);
  const flux = window.Echo.computeSpectralFlux(signalCurrent, signalPrevious);
  const rolloff = window.Echo.computeSpectralRolloff(signal, 44100.0);
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

#### `generate_chirp_native(config: &ChirpConfig) -> ChirpSignal`
Generates a linear chirp signal with specified frequency sweep.

#### `generate_chirp(start_freq, end_freq, duration, sample_rate) -> JsValue`
WASM-compatible version of `generate_chirp_native()`.

#### `cross_correlation_fft_native(signal1: &[f32], signal2: &[f32]) -> Vec<f32>`
Computes FFT-based cross-correlation between two signals.

#### `cross_correlation_fft(signal1: &[f32], signal2: &[f32]) -> Vec<f32>`
WASM-compatible version of `cross_correlation_fft_native()`.

#### `find_peak_lag_native(correlation: &[f32]) -> (usize, f32)`
Finds the lag with maximum correlation value.

#### `find_peak_lag(correlation: &[f32]) -> JsValue`
WASM-compatible version of `find_peak_lag_native()`.

#### `compute_fft_native(signal: &[f32]) -> Vec<Complex<f64>>`
Computes FFT of a signal (native only).

#### `spectral_centroid_native(fft_data: &[Complex<f64>], sample_rate: f64) -> f64`
Computes spectral centroid from FFT magnitude spectrum.

#### `compute_spectral_centroid(signal: &[f32], sample_rate: f64) -> f64`
WASM-compatible version that computes FFT internally.

#### `spectral_flux_native(fft_current: &[Complex<f64>], fft_previous: &[Complex<f64>]) -> f64`
Computes spectral flux between two FFT frames.

#### `compute_spectral_flux(signal_current: &[f32], signal_previous: &[f32]) -> f64`
WASM-compatible version that computes FFT internally.

#### `spectral_rolloff_native(fft_data: &[Complex<f64>], sample_rate: f64) -> f64`
Computes spectral rolloff (85% energy threshold frequency).

#### `compute_spectral_rolloff(signal: &[f32], sample_rate: f64) -> f64`
WASM-compatible version that computes FFT internally.

### EchoResult

```rust
pub struct EchoResult {
    pub score: f64,              // 0.0 to 1.0, higher is better
    pub status: String,          // "CLEAR", "SUSPECT", "ANOMALY", "INSUFFICIENT_DATA"
    pub mean_tof: f64,           // Mean time-of-flight in milliseconds
    pub std_tof: f64,            // Standard deviation
    pub spectral_centroid: f64,  // Spectral centroid in Hz
    pub zero_crossing_rate: f64, // Zero crossing rate
    pub spectral_flux: f64,      // Spectral flux value
    pub spectral_rolloff: f64,   // Spectral rolloff frequency in Hz
    pub sample_count: usize,     // Number of samples analyzed
}
```

### ChirpConfig

```rust
pub struct ChirpConfig {
    pub start_frequency: f64,  // Starting frequency in Hz
    pub end_frequency: f64,    // Ending frequency in Hz
    pub duration: f64,         // Duration in seconds
    pub sample_rate: f64,      // Sample rate in Hz
}
```

### ChirpSignal

```rust
pub struct ChirpSignal {
    pub samples: Vec<f32>,     // Generated chirp samples
    pub config: ChirpConfig,   // Configuration used
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
3. **Spectral Centroid**: Frequency distribution center of mass (in Hz)
4. **Spectral Flux**: Measure of spectral change between consecutive frames
5. **Spectral Rolloff**: Frequency below which 85% of spectral energy is contained
6. **Zero Crossing Rate**: Signal frequency indicator

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
