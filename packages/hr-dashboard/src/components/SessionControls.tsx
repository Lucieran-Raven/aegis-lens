import { useState } from 'react';
import { useDashboardStore } from '../store/useDashboardStore';
import { Play, Pause, Square, RotateCcw, Download, FileText, AlertCircle } from 'lucide-react';

export function SessionControls() {
  const { selectedCandidate, updateCandidate } = useDashboardStore();
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  const handleStartRecording = () => {
    setIsRecording(true);
    setIsPaused(false);
  };

  const handlePauseRecording = () => {
    setIsPaused(!isPaused);
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    setIsPaused(false);
  };

  const handleResetSession = () => {
    if (confirm('Are you sure you want to reset the session? This will clear all data.')) {
      // Reset logic here
      console.log('Reset session');
    }
  };

  const handleExportReport = () => {
    if (selectedCandidate) {
      const report = {
        candidate: selectedCandidate,
        timestamp: new Date().toISOString(),
        // Add more report data here
      };
      
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `session-report-${selectedCandidate.sessionId}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const handleEndSession = () => {
    if (selectedCandidate && confirm('Are you sure you want to end this session?')) {
      updateCandidate(selectedCandidate.id, {
        status: 'completed',
        endTime: new Date(),
      });
    }
  };

  if (!selectedCandidate) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Session Controls</h3>
        <p className="text-gray-500">No candidate selected</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Session Controls</h3>
        <div className="flex items-center gap-2">
          {isRecording && !isPaused && (
            <span className="flex items-center gap-1 text-sm text-danger-600">
              <span className="w-2 h-2 bg-danger-500 rounded-full animate-pulse" />
              Recording
            </span>
          )}
          {isRecording && isPaused && (
            <span className="flex items-center gap-1 text-sm text-warning-600">
              <span className="w-2 h-2 bg-warning-500 rounded-full" />
              Paused
            </span>
          )}
        </div>
      </div>

      {/* Session Info */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-gray-500 mb-1">Session ID</p>
            <p className="text-sm font-medium text-gray-900">{selectedCandidate.sessionId}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Status</p>
            <span className={`badge ${
              selectedCandidate.status === 'interviewing' ? 'badge-success' :
              selectedCandidate.status === 'completed' ? 'badge-info' :
              selectedCandidate.status === 'rejected' ? 'badge-danger' :
              'badge-warning'
            }`}>
              {selectedCandidate.status}
            </span>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Start Time</p>
            <p className="text-sm font-medium text-gray-900">
              {selectedCandidate.startTime?.toLocaleTimeString() || 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Duration</p>
            <p className="text-sm font-medium text-gray-900">
              {selectedCandidate.startTime
                ? `${Math.round((Date.now() - selectedCandidate.startTime.getTime()) / 60000)} min`
                : 'N/A'}
            </p>
          </div>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {!isRecording ? (
          <button
            onClick={handleStartRecording}
            className="btn-success flex items-center justify-center gap-2"
          >
            <Play className="w-4 h-4" />
            Start
          </button>
        ) : (
          <button
            onClick={handlePauseRecording}
            className="btn-warning flex items-center justify-center gap-2"
          >
            <Pause className="w-4 h-4" />
            {isPaused ? 'Resume' : 'Pause'}
          </button>
        )}

        <button
          onClick={handleStopRecording}
          disabled={!isRecording}
          className="btn-danger flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Square className="w-4 h-4" />
          Stop
        </button>

        <button
          onClick={handleResetSession}
          className="btn-secondary flex items-center justify-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          Reset
        </button>

        <button
          onClick={handleExportReport}
          className="btn-primary flex items-center justify-center gap-2"
        >
          <Download className="w-4 h-4" />
          Export
        </button>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <button
          onClick={handleEndSession}
          className="flex items-center justify-center gap-2 p-3 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <FileText className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">End Session</span>
        </button>

        <button
          className="flex items-center justify-center gap-2 p-3 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <AlertCircle className="w-4 h-4 text-warning-600" />
          <span className="text-sm font-medium text-gray-700">Flag for Review</span>
        </button>
      </div>

      {/* Session Notes */}
      <div className="mt-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Session Notes
        </label>
        <textarea
          className="input-field h-24 resize-none"
          placeholder="Add notes about this session..."
        />
      </div>
    </div>
  );
}
