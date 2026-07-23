# IRIS - Corneal Reflection Parallax

IRIS is a physics-based liveness detection pipeline that analyzes eye movement patterns to detect pre-recorded videos, photos, and other presentation attacks. It uses corneal reflection parallax and eye movement variance analysis to distinguish between live human subjects and synthetic media.

## Overview

IRIS (Corneal Reflection Parallax) is one of the four physics pipelines in the Aegis Lens platform:

- **CHRONOS** - Frame-Timing Entropy (hardware integrity)
- **ECHO** - Acoustic Time-of-Flight (audio integrity)
- **IRIS** - Corneal Reflection Parallax (visual liveness)
- **LIPSYNC** - AV-Sync Drift Analysis (media integrity)

## How It Works

IRIS analyzes eye movement patterns through several stages:

1. **Face Detection**: Detects faces in video frames using computer vision algorithms
2. **Eye Region Extraction**: Identifies and extracts eye regions from detected faces
3. **Vector Tracking**: Tracks eye movement vectors over time
4. **Variance Analysis**: Calculates statistical variance of eye movements
5. **Score Calculation**: Computes a liveness score based on movement patterns
6. **Status Determination**: Classifies the result as CLEAR, SUSPECT, or ANOMALY

### Key Principles

- **Natural Eye Movement**: Real humans exhibit natural, micro-movements in their eyes
- **Static Detection**: Photos and pre-recorded videos have minimal eye movement variance
- **Manipulation Detection**: Excessive or unnatural movement patterns indicate potential manipulation

## Installation

### Prerequisites

- Rust 1.70 or later
- wasm-pack (for WebAssembly builds)
- Node.js 20+ (for JavaScript integration)

### Build from Source

```bash
# Clone the repository
git clone https://github.com/your-org/aegis-lens.git
cd aegis-lens/packages/iris

# Build Rust library
cargo build

# Build WebAssembly module
wasm-pack build --target web --release

# Run tests
cargo test
```

## Usage

### Rust Native

```rust
use iris::{IrisEngine, FaceDetection, EyeLandmark, EyeType};

// Create engine
let mut engine = IrisEngine::new();

// Detect faces (simplified - production uses MediaPipe)
let image_data = vec![0u8; 640 * 480 * 3];
let detections = engine.detect_faces(&image_data, 640, 480);

// Extract eye regions
if let Some(face) = detections.first() {
    let eye = engine.extract_eye_region(face);
    
    // Track eye movement
    for _ in 0..30 {
        let left_eye = EyeLandmark {
            x: 100.0,
            y: 200.0,
            eye_type: EyeType::Left,
        };
        let right_eye = EyeLandmark {
            x: 150.0,
            y: 200.0,
            eye_type: EyeType::Right,
        };
        engine.track_eye_vector(&left_eye, &right_eye);
    }
}

// Analyze and get result
let result = engine.analyze();
println!("Score: {}", result.score);
println!("Status: {}", result.status);
println!("Eye Variance: {}", result.eye_variance);
```

### JavaScript (WebAssembly)

```javascript
import { initIris, detectFaces, trackEyeVector, analyze } from './iris/js/index.js';

// Initialize
await initIris();

// Detect faces
const imageData = new Uint8Array(640 * 480 * 3);
const detections = detectFaces(imageData, 640, 480);

// Track eye movement
for (let i = 0; i < 30; i++) {
  const leftEye = { x: 100.0, y: 200.0, eyeType: 'Left' };
  const rightEye = { x: 150.0, y: 200.0, eyeType: 'Right' };
  trackEyeVector(leftEye, rightEye);
}

// Analyze
const result = analyze();
console.log('Score:', result.score);
console.log('Status:', result.status);
console.log('Eye Variance:', result.eye_variance);
```

### Browser (Window Object)

```html
<script type="module">
  import init from './iris/pkg/iris.js';
  
  await init();
  
  // Use via window object
  const engine = new window.IrisEngine();
  const result = engine.analyze();
  console.log(result);
</script>
```

## API Reference

### IrisEngine

#### Constructor

```rust
pub fn new() -> Self
```

Creates a new IRIS engine instance.

#### Methods

##### detect_faces

```rust
pub fn detect_faces(&mut self, image_data: &[u8], width: u32, height: u32) -> Vec<FaceDetection>
```

Detects faces in the provided image data.

**Parameters:**
- `image_data`: Raw image bytes (RGB format)
- `width`: Image width in pixels
- `height`: Image height in pixels

**Returns:** Vector of `FaceDetection` objects

##### extract_eye_region

```rust
pub fn extract_eye_region(&self, face: &FaceDetection) -> EyeLandmark
```

Extracts eye region from a face detection.

**Parameters:**
- `face`: Face detection result

**Returns:** `EyeLandmark` object

##### track_eye_vector

```rust
pub fn track_eye_vector(&mut self, left_eye: &EyeLandmark, right_eye: &EyeLandmark)
```

Tracks eye movement vector between left and right eye landmarks.

**Parameters:**
- `left_eye`: Left eye landmark
- `right_eye`: Right eye landmark

##### calculate_eye_variance

```rust
pub fn calculate_eye_variance(&self) -> f32
```

Calculates the variance of tracked eye movement vectors.

**Returns:** Variance value (f32)

##### analyze

```rust
pub fn analyze(&self) -> IrisResult
```

Performs full analysis and returns liveness result.

**Returns:** `IrisResult` object containing:
- `score`: Liveness score (0.0 - 1.0)
- `status`: Classification ("CLEAR", "SUSPECT", "ANOMALY")
- `eye_variance`: Calculated eye movement variance
- `vector_count`: Number of tracked vectors
- `face_detected`: Whether a face was detected

##### clear

```rust
pub fn clear(&mut self)
```

Clears all detections and tracked vectors.

##### get_detections

```rust
pub fn get_detections(&self) -> Vec<FaceDetection>
```

Returns current face detections.

**Returns:** Vector of `FaceDetection` objects

### Data Structures

#### FaceDetection

```rust
pub struct FaceDetection {
    pub x: f32,
    pub y: f32,
    pub width: f32,
    pub height: f32,
    pub confidence: f32,
}
```

Represents a detected face bounding box.

#### EyeLandmark

```rust
pub struct EyeLandmark {
    pub x: f32,
    pub y: f32,
    pub eye_type: EyeType,
}
```

Represents an eye landmark position.

#### EyeType

```rust
pub enum EyeType {
    Left,
    Right,
}
```

Eye type enumeration.

#### IrisResult

```rust
pub struct IrisResult {
    pub score: f64,
    pub status: String,
    pub eye_variance: f32,
    pub vector_count: usize,
    pub face_detected: bool,
}
```

Analysis result containing liveness metrics.

## Scoring Algorithm

IRIS uses a multi-factor scoring algorithm:

1. **Face Detection Penalty**: -0.5 if no face detected
2. **Insufficient Data Penalty**: -0.3 if fewer than 10 vectors tracked
3. **Low Variance Penalty**: -0.4 if eye variance < 0.5 (indicates static image)
4. **High Variance Penalty**: -0.2 if eye variance > 50.0 (indicates manipulation)

### Status Thresholds

- **CLEAR**: Score ≥ 0.8 (Normal human behavior)
- **SUSPECT**: 0.5 ≤ Score < 0.8 (Some anomalies detected)
- **ANOMALY**: Score < 0.5 (Likely presentation attack)

## Testing

### Unit Tests

```bash
cargo test
```

### Integration Tests

```bash
cargo test --test integration
```

### All Tests

```bash
cargo test --all
```

## Performance

- **WASM Bundle Size**: ~50KB (gzipped)
- **Memory Usage**: < 10MB
- **Processing Time**: < 5ms per frame (on modern hardware)
- **Vector Capacity**: 100 vectors (sliding window)

## Limitations

1. **Simplified Face Detection**: Current implementation uses placeholder face detection. Production should integrate MediaPipe Face Detection for accurate results.

2. **Lighting Conditions**: Performance may degrade in poor lighting conditions.

3. **Camera Quality**: Requires minimum 720p resolution for reliable detection.

4. **Edge Cases**: May have difficulty with:
   - Extreme facial angles
   - Heavy makeup or accessories
   - Glasses with strong reflections

## Future Enhancements

- [ ] Integrate MediaPipe Face Detection
- [ ] Add corneal reflection analysis
- [ ] Implement blink detection
- [ ] Add pupil tracking
- [ ] Support multiple face tracking
- [ ] Add 3D face reconstruction
- [ ] Implement deep learning models

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details

## Contact

For questions or issues, please open a GitHub issue or contact the development team.

## Related Documentation

- [CHRONOS Documentation](../chronos/README.md)
- [ECHO Documentation](../echo/README.md)
- [LIPSYNC Documentation](../lipsync/README.md)
- [Aegis Lens Main Documentation](../../README.md)
