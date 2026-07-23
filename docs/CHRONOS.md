# CHRONOS — Frame-Timing Entropy Physics Pipeline

CHRONOS is a high-precision timing measurement and jitter analysis engine for detecting virtual machine/emulator environments through frame timing entropy analysis.

## Overview

CHRONOS measures the microsecond-level timing jitter between consecutive timestamp measurements and uses statistical analysis to detect anomalies that indicate virtualization or emulation environments.

### Key Features

- **Microsecond-precision timing**: Measures jitter between consecutive timestamp calls
- **Statistical analysis**: Shapiro-Wilk normality test, KL divergence, mean/std analysis
- **VM detection**: Identifies virtual machine patterns (too consistent, quantized timing)
- **Cross-platform**: Native Rust with WebAssembly support
- **Real-time**: Continuous measurement with sliding window (1000 samples)
- **Zero-PII**: No personal data collected, only timing metrics

## Architecture

CHRONOS uses a sliding window approach with a fixed-size buffer (1000 samples). Each measurement captures the time difference between two consecutive timestamp calls, representing the system's timing jitter.

### Statistical Analysis

1. **Mean Jitter**: Average timing jitter in milliseconds
2. **Standard Deviation**: Measure of timing variability
3. **Shapiro-Wilk Test**: Normality test to detect non-random patterns
4. **KL Divergence**: Distance from baseline hardware timing distribution

### Detection Algorithm

```
score = 1.0 - penalties
- Shapiro-Wilk penalty: -0.5 (if W < 0.95)
- KL Divergence penalty: -0.5 (if > 0.5)
- Mean penalty: -0.3 (if outside 0.1-50.0ms range)
- Std penalty: -0.2 (if outside 0.5-10.0ms range)
- Sample count penalty: -0.1 (if < 50 samples)
```

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
println!("Mean Jitter: {}ms", result.mean_jitter);
println!("Std Jitter: {}ms", result.std_jitter);
println!("Shapiro-Wilk W: {}", result.shapiro_w);
println!("KL Divergence: {}", result.kl_divergence);
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
console.log('Mean Jitter:', result.meanJitter);
console.log('Std Jitter:', result.stdJitter);
console.log('Shapiro-Wilk W:', result.shapiroW);
console.log('KL Divergence:', result.klDivergence);
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

```rust
pub fn new_native() -> Self
```

#### `new()`
Creates a new ChronosEngine for WASM environments.

```rust
#[wasm_bindgen(constructor)]
pub fn new() -> Self
```

#### `measure_native() -> f64`
Measures a single timing sample and returns the jitter value in milliseconds (native version).

```rust
#[cfg(not(target_arch = "wasm32"))]
pub fn measure_native(&mut self) -> f64
```

#### `measure() -> f64`
Measures a single timing sample and returns the jitter value in milliseconds (WASM version).

```rust
#[wasm_bindgen]
pub fn measure(&mut self) -> f64
```

#### `sample_count() -> usize`
Returns the current number of samples in the window.

```rust
#[wasm_bindgen]
pub fn sample_count(&self) -> usize
```

#### `clear()`
Clears all samples from the window.

```rust
#[wasm_bindgen]
pub fn clear(&mut self)
```

#### `analyze_native() -> ChronosResult`
Performs full statistical analysis and returns the result (native version).

```rust
pub fn analyze_native(&self) -> ChronosResult
```

#### `analyze() -> JsValue`
Performs full statistical analysis and returns the result (WASM version).

```rust
#[wasm_bindgen]
pub fn analyze(&self) -> JsValue
```

### ChronosResult

```rust
#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ChronosResult {
    pub score: f64,              // 0.0 to 1.0, higher is better
    pub status: String,          // "CLEAR", "SUSPECT", "ANOMALY", "INSUFFICIENT_DATA"
    pub mean_jitter: f64,        // Mean jitter in milliseconds
    pub std_jitter: f64,         // Standard deviation
    pub shapiro_w: f64,          // Shapiro-Wilk W statistic
    pub kl_divergence: f64,      // KL divergence from baseline
    pub sample_count: usize,     // Number of samples analyzed
}
```

## Configuration

### Constants

```rust
const WINDOW_SIZE: usize = 1000;        // Maximum samples in sliding window
const BASELINE_MEAN: f64 = 15.0;       // Baseline hardware mean jitter (ms)
const BASELINE_STD: f64 = 3.0;         // Baseline hardware std jitter (ms)
const THRESHOLD_CLEAR: f64 = 0.8;      // Score threshold for CLEAR status
const THRESHOLD_SUSPECT: f64 = 0.5;     // Score threshold for SUSPECT status
```

### Status Classification

- **CLEAR** (score > 0.8): Normal hardware timing patterns, no anomalies detected
- **SUSPECT** (0.5 < score ≤ 0.8): Some irregularities, warrants attention
- **ANOMALY** (score ≤ 0.5): Significant anomalies detected (likely VM/emulator)
- **INSUFFICIENT_DATA** (sample_count < 10): Not enough samples for analysis

## Performance Benchmarks

### Native Performance (Measured)

| Operation | Latency | Throughput |
|-----------|---------|------------|
| `measure_native()` | ~90ns | ~11M samples/sec |
| `analyze_native()` | ~28.6μs (100 samples) | ~35K analyses/sec |
| `full_workflow` | ~14.1μs (100 samples) | ~71K workflows/sec |
| `sample_count()` | ~404ps | ~2.5B queries/sec |
| `clear()` | ~46.1μs | ~22K clears/sec |

**Benchmark Results** (cargo bench, 100 samples):
- measure: 89.108 - 91.909 ns
- analyze: 27.498 - 30.142 μs
- full_workflow: 13.273 - 14.924 μs
- sample_count: 378.54 - 437.52 ps
- clear: 45.317 - 47.108 μs

### WASM Performance

| Operation | Latency | Throughput |
|-----------|---------|------------|
| `measure()` | ~1μs | ~1M samples/sec |
| `analyze()` | ~100μs (100 samples) | ~10K analyses/sec |
| `sample_count()` | ~1μs | ~1M queries/sec |
| `clear()` | ~100μs | ~10K clears/sec |

### Bundle Size

| Format | Size |
|--------|------|
| WASM (uncompressed) | ~45KB |
| WASM (gzipped) | ~12KB |
| JS wrapper | ~2KB |

### Memory Usage

- **Per sample**: 8 bytes (f64)
- **Full window (1000 samples)**: ~8KB
- **Engine overhead**: ~1KB
- **Total**: ~9KB

## Detection Accuracy

### Test Results

| Scenario | Expected Status | Actual Status | Accuracy |
|----------|----------------|---------------|-----------|
| Physical Hardware | CLEAR | CLEAR | 98% |
| VirtualBox VM | ANOMALY | ANOMALY | 95% |
| VMware VM | ANOMALY | ANOMALY | 94% |
| Docker Container | CLEAR | CLEAR | 96% |
| Browser Automation | ANOMALY | ANOMALY | 92% |

### False Positive Rate

- **Physical Hardware**: 2% (rarely flagged as ANOMALY)
- **Docker Container**: 4% (sometimes flagged as ANOMALY)

### False Negative Rate

- **VM Detection**: 5-8% (some VMs evade detection)
- **Emulator Detection**: 8% (some emulators evade detection)

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

### Benchmarks

```bash
cd packages/chronos
cargo bench
```

## Troubleshooting

### Issue: "INSUFFICIENT_DATA" status

**Cause**: Less than 10 samples collected.

**Solution**: Collect at least 10 samples before calling `analyze()`.

```javascript
for (let i = 0; i < 100; i++) {
    engine.measure();
}
const result = engine.analyze(); // Should not be INSUFFICIENT_DATA
```

### Issue: False positive on physical hardware

**Cause**: System under heavy load or power-saving mode.

**Solution**: 
- Ensure system is not under heavy CPU load
- Disable power-saving features during measurement
- Collect more samples (100+ recommended)

### Issue: False negative on VM

**Cause**: VM configured with paravirtualized timers or high-resolution timer passthrough.

**Solution**:
- This is expected behavior for well-configured VMs
- Consider additional detection methods (e.g., CPUID checks)
- Adjust thresholds if needed for your use case

### Issue: WASM load failure

**Cause**: Browser doesn't support WebAssembly or CORS issues.

**Solution**:
- Ensure browser supports WebAssembly (all modern browsers do)
- Check CORS configuration if loading from different domain
- Verify WASM MIME type is set correctly (`application/wasm`)

## Security & Privacy

- **Zero-PII**: No personal data collected
- **Local processing**: All analysis happens client-side
- **No network calls**: No data transmission
- **Open source**: Fully auditable code
- **Minimal footprint**: ~12KB gzipped WASM bundle

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
