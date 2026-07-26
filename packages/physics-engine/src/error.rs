//! Error Handling
//!
//! This module provides comprehensive error handling for the physics engine
//! with graceful degradation and recovery mechanisms.

use serde::{Deserialize, Serialize};
use std::fmt;

/// Physics engine errors
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PhysicsError {
    ChronosError(String),
    EchoError(String),
    IrisError(String),
    LipsyncError(String),
    DataCollectionError(String),
    ProcessingError(String),
    AggregationError(String),
    InsufficientData,
    Timeout,
    InvalidInput(String),
    InitializationError(String),
}

impl fmt::Display for PhysicsError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            PhysicsError::ChronosError(msg) => write!(f, "CHRONOS error: {}", msg),
            PhysicsError::EchoError(msg) => write!(f, "ECHO error: {}", msg),
            PhysicsError::IrisError(msg) => write!(f, "IRIS error: {}", msg),
            PhysicsError::LipsyncError(msg) => write!(f, "LIPSYNC error: {}", msg),
            PhysicsError::DataCollectionError(msg) => write!(f, "Data collection error: {}", msg),
            PhysicsError::ProcessingError(msg) => write!(f, "Processing error: {}", msg),
            PhysicsError::AggregationError(msg) => write!(f, "Aggregation error: {}", msg),
            PhysicsError::InsufficientData => write!(f, "Insufficient data"),
            PhysicsError::Timeout => write!(f, "Operation timeout"),
            PhysicsError::InvalidInput(msg) => write!(f, "Invalid input: {}", msg),
            PhysicsError::InitializationError(msg) => write!(f, "Initialization error: {}", msg),
        }
    }
}

impl std::error::Error for PhysicsError {}

/// Result type for physics engine operations
pub type Result<T> = std::result::Result<T, PhysicsError>;

/// Recovery strategy for errors
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum RecoveryStrategy {
    Continue,
    Retry,
    Abort,
    Fallback,
}

/// Error context for logging
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ErrorContext {
    pub error_type: String,
    pub pipeline: String,
    pub message: String,
    pub timestamp: f64,
    pub recovery_strategy: String,
}

impl ErrorContext {
    pub fn new(error: &PhysicsError, pipeline: &str, strategy: RecoveryStrategy) -> Self {
        Self {
            error_type: format!("{:?}", std::mem::discriminant(error)),
            pipeline: pipeline.to_string(),
            message: error.to_string(),
            timestamp: 0.0, // Use 0.0 for non-WASM testing
            recovery_strategy: format!("{:?}", strategy),
        }
    }
}

/// Error handler with recovery mechanisms
pub struct ErrorHandler {
    error_count: u32,
    max_errors: u32,
    recovery_strategy: RecoveryStrategy,
    error_history: Vec<ErrorContext>,
}

impl ErrorHandler {
    /// Create a new error handler
    pub fn new(max_errors: u32, recovery_strategy: RecoveryStrategy) -> Self {
        Self {
            error_count: 0,
            max_errors,
            recovery_strategy,
            error_history: Vec::new(),
        }
    }

    /// Handle an error
    pub fn handle_error(&mut self, error: PhysicsError, pipeline: &str) -> Result<()> {
        self.error_count += 1;
        
        let context = ErrorContext::new(&error, pipeline, self.recovery_strategy);
        self.error_history.push(context);

        if self.error_count >= self.max_errors {
            return Err(PhysicsError::InitializationError(
                "Max errors exceeded".to_string()
            ));
        }

        match self.recovery_strategy {
            RecoveryStrategy::Continue => Ok(()),
            RecoveryStrategy::Retry => Ok(()),
            RecoveryStrategy::Abort => Err(error),
            RecoveryStrategy::Fallback => Ok(()),
        }
    }

    /// Get error count
    pub fn get_error_count(&self) -> u32 {
        self.error_count
    }

    /// Get error history
    pub fn get_error_history(&self) -> Vec<ErrorContext> {
        self.error_history.clone()
    }

    /// Reset error handler
    pub fn reset(&mut self) {
        self.error_count = 0;
        self.error_history.clear();
    }

    /// Set recovery strategy
    pub fn set_recovery_strategy(&mut self, strategy: RecoveryStrategy) {
        self.recovery_strategy = strategy;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let error = PhysicsError::ChronosError("test error".to_string());
        assert_eq!(error.to_string(), "CHRONOS error: test error");
    }

    #[test]
    fn test_error_handler_continue() {
        let mut handler = ErrorHandler::new(10, RecoveryStrategy::Continue);
        let _ = handler.handle_error(PhysicsError::ChronosError("test".to_string()), "chronos");
        assert_eq!(handler.get_error_count(), 1);
    }

    #[test]
    fn test_error_handler_abort() {
        let mut handler = ErrorHandler::new(10, RecoveryStrategy::Abort);
        let result = handler.handle_error(PhysicsError::ChronosError("test".to_string()), "chronos");
        assert!(result.is_err());
    }

    #[test]
    fn test_error_handler_reset() {
        let mut handler = ErrorHandler::new(10, RecoveryStrategy::Continue);
        handler.handle_error(PhysicsError::ChronosError("test".to_string()), "chronos");
        handler.reset();
        assert_eq!(handler.get_error_count(), 0);
    }
}
