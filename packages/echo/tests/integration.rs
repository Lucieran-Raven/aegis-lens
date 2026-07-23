//! ECHO Integration Tests
//!
//! These tests verify the end-to-end integration of the ECHO engine,
//! including WASM bindings and JavaScript integration.

#[cfg(test)]
mod integration_tests {
    use echo::EchoEngine;
    use num_complex::Complex;

    #[test]
    fn test_full_analysis_pipeline() {
        let mut engine = EchoEngine::new_native();

        // Collect enough samples for analysis
        for _ in 0..100 {
            engine.measure_native();
        }

        // Perform full analysis
        let result = engine.analyze_native();

        // Verify all fields are populated
        assert!(result.score >= 0.0 && result.score <= 1.0);
        assert!(!result.status.is_empty());
        assert!(result.mean_tof >= 0.0);
        assert!(result.std_tof >= 0.0);
        assert!(result.spectral_centroid >= 0.0);
        assert!(result.zero_crossing_rate >= 0.0);
        assert!(result.spectral_flux >= 0.0);
        assert!(result.spectral_rolloff >= 0.0);
        assert_eq!(result.sample_count, 100);
    }

    #[test]
    fn test_chirp_generation_and_analysis() {
        let engine = EchoEngine::new_native();

        let config = echo::ChirpConfig {
            start_frequency: 1000.0,
            end_frequency: 8000.0,
            duration: 0.1,
            sample_rate: 44100.0,
        };

        let chirp = engine.generate_chirp_native(&config);

        // Verify chirp structure
        assert!(!chirp.samples.is_empty());
        assert_eq!(chirp.config.start_frequency, 1000.0);
        assert_eq!(chirp.config.end_frequency, 8000.0);
        assert_eq!(chirp.config.duration, 0.1);
        assert_eq!(chirp.config.sample_rate, 44100.0);

        // Verify sample count matches duration * sample_rate
        let expected_samples = (config.duration * config.sample_rate) as usize;
        assert_eq!(chirp.samples.len(), expected_samples);
    }

    #[test]
    fn test_cross_correlation_pipeline() {
        // Create test signals
        let signal1 = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let signal2 = vec![1.0, 2.0, 3.0, 4.0, 5.0];

        // Compute cross-correlation
        let correlation = EchoEngine::cross_correlation_fft_native(&signal1, &signal2);

        // Verify correlation result
        assert!(!correlation.is_empty());
        assert_eq!(correlation.len(), signal1.len() + signal2.len() - 1);

        // Find peak lag
        let (lag, value) = EchoEngine::find_peak_lag_native(&correlation);

        // Verify peak detection
        assert!(lag < correlation.len());
        assert!(value > 0.0);
    }

    #[test]
    fn test_spectral_analysis_pipeline() {
        let signal = vec![1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0];

        // Compute FFT
        let fft_data = EchoEngine::compute_fft_native(&signal);
        assert!(!fft_data.is_empty());

        // Compute spectral centroid
        let centroid = EchoEngine::spectral_centroid_native(&fft_data, 44100.0);
        assert!(centroid >= 0.0);

        // Compute spectral flux (with zero previous frame)
        let empty_fft = vec![Complex::new(0.0, 0.0); fft_data.len()];
        let flux = EchoEngine::spectral_flux_native(&fft_data, &empty_fft);
        assert!(flux >= 0.0);

        // Compute spectral rolloff
        let rolloff = EchoEngine::spectral_rolloff_native(&fft_data, 44100.0);
        assert!(rolloff >= 0.0 && rolloff <= 22050.0);
    }

    #[test]
    fn test_window_capacity_management() {
        let mut engine = EchoEngine::new_native();

        // Add samples beyond window size
        for _ in 0..1500 {
            engine.measure_native();
        }

        // Verify window size is maintained
        assert_eq!(engine.sample_count(), 1000);

        // Analysis should still work
        let result = engine.analyze_native();
        assert!(result.sample_count == 1000);
    }

    #[test]
    fn test_clear_and_reanalyze() {
        let mut engine = EchoEngine::new_native();

        // Add samples
        for _ in 0..100 {
            engine.measure_native();
        }

        // Verify samples exist
        assert_eq!(engine.sample_count(), 100);

        // Clear samples
        engine.clear();

        // Verify samples are cleared
        assert_eq!(engine.sample_count(), 0);

        // Re-add samples
        for _ in 0..50 {
            engine.measure_native();
        }

        // Verify new samples
        assert_eq!(engine.sample_count(), 50);

        // Analysis should work with new samples
        let result = engine.analyze_native();
        assert!(result.sample_count == 50);
    }

    #[test]
    fn test_chirp_frequency_sweep() {
        let engine = EchoEngine::new_native();

        let config = echo::ChirpConfig {
            start_frequency: 1000.0,
            end_frequency: 10000.0,
            duration: 0.05,
            sample_rate: 44100.0,
        };

        let chirp = engine.generate_chirp_native(&config);

        // Verify frequency sweep by checking signal properties
        let mut min_val = f32::MAX;
        let mut max_val = f32::MIN;

        for &sample in &chirp.samples {
            min_val = min_val.min(sample);
            max_val = max_val.max(sample);
        }

        // Chirp should have variation (frequency sweep)
        assert!(max_val > min_val);
    }

    #[test]
    fn test_status_transitions() {
        let mut engine = EchoEngine::new_native();

        // Initially should be INSUFFICIENT_DATA
        let result = engine.analyze_native();
        assert_eq!(result.status, "INSUFFICIENT_DATA");

        // Add samples
        for _ in 0..100 {
            engine.measure_native();
        }

        // After adding samples, status should change
        let result = engine.analyze_native();
        assert_ne!(result.status, "INSUFFICIENT_DATA");
        assert!(result.score > 0.0);
    }

    #[test]
    fn test_empty_signal_handling() {
        let empty_signal: Vec<f32> = vec![];

        // Cross-correlation with empty signals
        let correlation = EchoEngine::cross_correlation_fft_native(&empty_signal, &empty_signal);
        assert!(correlation.is_empty());

        // FFT of empty signal
        let fft_data = EchoEngine::compute_fft_native(&empty_signal);
        assert!(fft_data.is_empty());

        // Peak lag of empty correlation
        let (lag, value) = EchoEngine::find_peak_lag_native(&empty_signal);
        assert_eq!(lag, 0);
        assert_eq!(value, 0.0);
    }

    #[test]
    fn test_single_sample_handling() {
        let single_signal = vec![1.0];

        // Cross-correlation with single sample
        let correlation = EchoEngine::cross_correlation_fft_native(&single_signal, &single_signal);
        assert!(!correlation.is_empty());

        // FFT of single sample
        let fft_data = EchoEngine::compute_fft_native(&single_signal);
        assert!(!fft_data.is_empty());

        // Peak lag should work
        let (lag, value) = EchoEngine::find_peak_lag_native(&correlation);
        assert!(lag < correlation.len());
        assert!(value > 0.0);
    }
}
