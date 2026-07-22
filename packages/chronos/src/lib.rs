//! Chronos - Time-based scheduling and event management
//!
//! This module provides utilities for scheduling events, managing time-based operations,
//! and handling temporal data structures.

use chrono::{DateTime, Utc};

/// A scheduled event with a specific time
#[derive(Debug, Clone)]
pub struct ScheduledEvent {
    pub id: String,
    pub scheduled_time: DateTime<Utc>,
    pub payload: String,
}

impl ScheduledEvent {
    /// Create a new scheduled event
    pub fn new(id: String, scheduled_time: DateTime<Utc>, payload: String) -> Self {
        Self {
            id,
            scheduled_time,
            payload,
        }
    }

    /// Check if the event is due
    pub fn is_due(&self) -> bool {
        Utc::now() >= self.scheduled_time
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_scheduled_event_creation() {
        let event = ScheduledEvent::new(
            "test".to_string(),
            Utc::now() + chrono::Duration::hours(1),
            "payload".to_string(),
        );
        assert_eq!(event.id, "test");
        assert!(!event.is_due());
    }

    #[test]
    fn test_scheduled_event_due() {
        let event = ScheduledEvent::new(
            "test".to_string(),
            Utc::now() - chrono::Duration::hours(1),
            "payload".to_string(),
        );
        assert!(event.is_due());
    }
}
