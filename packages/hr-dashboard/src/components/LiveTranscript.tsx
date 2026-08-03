import { useState, useEffect, useRef } from 'react';
import { MessageSquare, Search, Download, Clock } from 'lucide-react';

interface TranscriptEntry {
  id: string;
  speaker: 'candidate' | 'interviewer';
  text: string;
  timestamp: Date;
  confidence?: number;
}

export function LiveTranscript() {
  const [transcript] = useState<TranscriptEntry[]>([
    {
      id: '1',
      speaker: 'interviewer',
      text: 'Can you tell me about your experience with React?',
      timestamp: new Date(Date.now() - 300000),
    },
    {
      id: '2',
      speaker: 'candidate',
      text: 'I have been working with React for the past three years, building several production applications.',
      timestamp: new Date(Date.now() - 250000),
      confidence: 0.95,
    },
    {
      id: '3',
      speaker: 'interviewer',
      text: 'What challenges did you face while working with state management?',
      timestamp: new Date(Date.now() - 180000),
    },
    {
      id: '4',
      speaker: 'candidate',
      text: 'The main challenge was managing complex state across multiple components. I solved this by implementing Redux and later moved to Zustand for simpler use cases.',
      timestamp: new Date(Date.now() - 120000),
      confidence: 0.92,
    },
  ]);
  const [searchQuery, setSearchQuery] = useState('');
  const transcriptEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript]);

  const filteredTranscript = transcript.filter((entry) =>
    entry.text.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDownload = () => {
    const text = transcript
      .map(
        (entry) =>
          `[${entry.timestamp.toLocaleTimeString()}] ${entry.speaker.toUpperCase()}: ${entry.text}`
      )
      .join('\n');
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'transcript.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Live Transcript</h3>
        </div>
        <button
          onClick={handleDownload}
          className="btn-secondary flex items-center gap-2 text-sm"
        >
          <Download className="w-4 h-4" />
          Download
        </button>
      </div>

      {/* Search Bar */}
      <div className="mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search transcript..."
            className="input-field pl-10"
          />
        </div>
      </div>

      {/* Transcript Content */}
      <div className="space-y-3 max-h-80 overflow-y-auto">
        {filteredTranscript.map((entry) => (
          <div
            key={entry.id}
            className={`p-3 rounded-lg ${
              entry.speaker === 'candidate'
                ? 'bg-primary-50 border-l-4 border-primary-500'
                : 'bg-gray-50 border-l-4 border-gray-400'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span
                className={`text-xs font-medium ${
                  entry.speaker === 'candidate'
                    ? 'text-primary-700'
                    : 'text-gray-700'
                }`}
              >
                {entry.speaker === 'candidate' ? 'Candidate' : 'Interviewer'}
              </span>
              <div className="flex items-center gap-2">
                <Clock className="w-3 h-3 text-gray-400" />
                <span className="text-xs text-gray-500">
                  {entry.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </div>
            <p className="text-sm text-gray-900">{entry.text}</p>
            {entry.confidence !== undefined && (
              <div className="mt-1">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Confidence</span>
                  <span>{Math.round(entry.confidence * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                  <div
                    className="bg-primary-500 h-1 rounded-full"
                    style={{ width: `${entry.confidence * 100}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        ))}
        <div ref={transcriptEndRef} />
      </div>

      {filteredTranscript.length === 0 && (
        <p className="text-center text-gray-500 py-8">No matching transcript entries</p>
      )}
    </div>
  );
}
