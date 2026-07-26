//! Logging
//!
//! This module provides structured logging for the unified physics engine
//! with multiple log levels and JSON output.

use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use wasm_bindgen::prelude::*;

/// Log levels
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum LogLevel {
    Error,
    Warn,
    Info,
    Debug,
    Trace,
}

impl LogLevel {
    pub fn as_str(&self) -> &'static str {
        match self {
            LogLevel::Error => "ERROR",
            LogLevel::Warn => "WARN",
            LogLevel::Info => "INFO",
            LogLevel::Debug => "DEBUG",
            LogLevel::Trace => "TRACE",
        }
    }
}

/// Log entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogEntry {
    pub level: String,
    pub message: String,
    pub timestamp: f64,
    pub pipeline: Option<String>,
    pub context: Option<serde_json::Value>,
}

impl LogEntry {
    pub fn new(level: LogLevel, message: &str, pipeline: Option<&str>) -> Self {
        Self {
            level: level.as_str().to_string(),
            message: message.to_string(),
            timestamp: 0.0, // Use 0.0 for non-WASM testing
            pipeline: pipeline.map(|s| s.to_string()),
            context: None,
        }
    }

    pub fn with_context(mut self, context: serde_json::Value) -> Self {
        self.context = Some(context);
        self
    }
}

/// Logger
pub struct Logger {
    entries: Mutex<Vec<LogEntry>>,
    max_entries: usize,
    min_level: LogLevel,
}

impl Logger {
    /// Create a new logger
    pub fn new(max_entries: usize, min_level: LogLevel) -> Self {
        Self {
            entries: Mutex::new(Vec::new()),
            max_entries,
            min_level,
        }
    }

    /// Log a message
    pub fn log(&self, level: LogLevel, message: &str, pipeline: Option<&str>) {
        if (level as u8) < (self.min_level as u8) {
            return;
        }

        let entry = LogEntry::new(level, message, pipeline);
        
        let mut entries = self.entries.lock().unwrap();
        entries.push(entry);
        
        if entries.len() > self.max_entries {
            entries.remove(0);
        }

        Self::log_to_console(level, message, pipeline);
    }

    /// Log error
    pub fn error(&self, message: &str, pipeline: Option<&str>) {
        self.log(LogLevel::Error, message, pipeline);
    }

    /// Log warning
    pub fn warn(&self, message: &str, pipeline: Option<&str>) {
        self.log(LogLevel::Warn, message, pipeline);
    }

    /// Log info
    pub fn info(&self, message: &str, pipeline: Option<&str>) {
        self.log(LogLevel::Info, message, pipeline);
    }

    /// Log debug
    pub fn debug(&self, message: &str, pipeline: Option<&str>) {
        self.log(LogLevel::Debug, message, pipeline);
    }

    /// Log trace
    pub fn trace(&self, message: &str, pipeline: Option<&str>) {
        self.log(LogLevel::Trace, message, pipeline);
    }

    /// Log with pipeline context
    pub fn log_pipeline(&self, level: LogLevel, message: &str, pipeline: &str) {
        self.log(level, message, Some(pipeline));
    }

    /// Get all log entries
    pub fn get_entries(&self) -> Vec<LogEntry> {
        self.entries.lock().unwrap().clone()
    }

    /// Clear all log entries
    pub fn clear(&self) {
        self.entries.lock().unwrap().clear();
    }

    /// Check if should log
    pub fn should_log(&self, level: LogLevel) -> bool {
        (level as u8) <= (self.min_level as u8)
    }

    /// Internal log method
    fn log_to_console(level: LogLevel, message: &str, pipeline: Option<&str>) {
        // In a real implementation, this would check the global logger
        // For now, we'll just use console.log for WASM
        let entry = LogEntry::new(level, message, pipeline);
        let json = serde_json::to_string(&entry).unwrap_or_else(|_| message.to_string());
        
        // Use web_sys console if available
        let _ = match level {
            LogLevel::Error => web_sys::console::error_1(&json.into()),
            LogLevel::Warn => web_sys::console::warn_1(&json.into()),
            LogLevel::Info => web_sys::console::log_1(&json.into()),
            LogLevel::Debug => web_sys::console::log_1(&json.into()),
            LogLevel::Trace => web_sys::console::log_1(&json.into()),
        };
    }
}

impl Default for Logger {
    fn default() -> Self {
        Self::new(1000, LogLevel::Info)
    }
}

/// WASM logger for JavaScript
#[wasm_bindgen]
pub struct JsLogger {
    inner: Logger,
}

#[wasm_bindgen]
impl JsLogger {
    /// Create a new WASM logger
    #[wasm_bindgen(constructor)]
    pub fn new(max_entries: usize, min_level: u8) -> Self {
        let level = match min_level {
            0 => LogLevel::Error,
            1 => LogLevel::Warn,
            2 => LogLevel::Info,
            3 => LogLevel::Debug,
            _ => LogLevel::Trace,
        };
        Self {
            inner: Logger::new(max_entries, level),
        }
    }

    /// Log a message
    #[wasm_bindgen]
    pub fn log(&self, level: u8, message: &str, pipeline: Option<String>) {
        let log_level = match level {
            0 => LogLevel::Error,
            1 => LogLevel::Warn,
            2 => LogLevel::Info,
            3 => LogLevel::Debug,
            _ => LogLevel::Trace,
        };
        self.inner.log(log_level, message, pipeline.as_deref());
    }

    /// Get all log entries as JSON
    #[wasm_bindgen]
    pub fn get_entries(&self) -> JsValue {
        serde_wasm_bindgen::to_value(&self.inner.get_entries()).unwrap_or(JsValue::NULL)
    }

    /// Clear all log entries
    #[wasm_bindgen]
    pub fn clear(&self) {
        self.inner.clear();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_log_level_as_str() {
        assert_eq!(LogLevel::Error.as_str(), "ERROR");
        assert_eq!(LogLevel::Warn.as_str(), "WARN");
        assert_eq!(LogLevel::Info.as_str(), "INFO");
    }

    #[test]
    fn test_logger_creation() {
        let logger = Logger::new(100, LogLevel::Info);
        assert!(logger.should_log(LogLevel::Info));
        assert!(!logger.should_log(LogLevel::Debug));
    }

    #[test]
    fn test_should_log() {
        let logger = Logger::new(100, LogLevel::Info);
        assert!(logger.should_log(LogLevel::Error));
        assert!(logger.should_log(LogLevel::Warn));
        assert!(logger.should_log(LogLevel::Info));
        assert!(!logger.should_log(LogLevel::Debug));
    }

    #[test]
    fn test_log_entry_creation() {
        let entry = LogEntry::new(LogLevel::Info, "test message", Some("chronos"));
        assert_eq!(entry.level, "INFO");
        assert_eq!(entry.message, "test message");
        assert_eq!(entry.pipeline, Some("chronos".to_string()));
    }
}
