import { CheckCircle, XCircle, AlertCircle, Clock } from 'lucide-react';

interface FactCheck {
  id: string;
  claim: string;
  verification: 'verified' | 'unverified' | 'inconclusive';
  confidence: number;
  sources: string[];
  timestamp: Date;
  details: string;
}

export function RealTimeFactCheck() {
  const factChecks: FactCheck[] = [
    {
      id: '1',
      claim: 'I worked at Google for 3 years',
      verification: 'verified',
      confidence: 0.95,
      sources: ['LinkedIn Profile', 'Company Records'],
      timestamp: new Date(Date.now() - 300000),
      details: 'Employment verified through official records and social media profiles.',
    },
    {
      id: '2',
      claim: 'I have a Masters degree in Computer Science',
      verification: 'unverified',
      confidence: 0.30,
      sources: ['No official records found'],
      timestamp: new Date(Date.now() - 240000),
      details: 'Could not verify degree through university databases or official transcripts.',
    },
    {
      id: '3',
      claim: 'I contributed to React open source',
      verification: 'inconclusive',
      confidence: 0.55,
      sources: ['GitHub activity', 'Commit history'],
      timestamp: new Date(Date.now() - 180000),
      details: 'Found some GitHub activity but cannot confirm direct contributions to React core.',
    },
  ];

  const getVerificationIcon = (verification: string) => {
    switch (verification) {
      case 'verified':
        return <CheckCircle className="w-5 h-5 text-success-600" />;
      case 'unverified':
        return <XCircle className="w-5 h-5 text-danger-600" />;
      default:
        return <AlertCircle className="w-5 h-5 text-warning-600" />;
    }
  };

  const getVerificationColor = (verification: string) => {
    switch (verification) {
      case 'verified':
        return 'border-success-500 bg-success-50';
      case 'unverified':
        return 'border-danger-500 bg-danger-50';
      default:
        return 'border-warning-500 bg-warning-50';
    }
  };

  const getVerificationBadge = (verification: string) => {
    switch (verification) {
      case 'verified':
        return 'badge-success';
      case 'unverified':
        return 'badge-danger';
      default:
        return 'badge-warning';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Real-time Fact Check</h3>
        </div>
        <span className="badge badge-info">{factChecks.length} Checked</span>
      </div>

      <div className="space-y-4 max-h-80 overflow-y-auto">
        {factChecks.map((factCheck) => (
          <div
            key={factCheck.id}
            className={`p-4 rounded-lg border-l-4 ${getVerificationColor(factCheck.verification)}`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                {getVerificationIcon(factCheck.verification)}
                <span className={`badge ${getVerificationBadge(factCheck.verification)}`}>
                  {factCheck.verification}
                </span>
              </div>
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Clock className="w-3 h-3" />
                {factCheck.timestamp.toLocaleTimeString()}
              </div>
            </div>

            <div className="mb-3">
              <p className="text-sm font-medium text-gray-900 mb-1">Claim:</p>
              <p className="text-sm text-gray-700 italic">"{factCheck.claim}"</p>
            </div>

            <div className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-gray-600">Confidence:</span>
                <span className="text-xs font-medium text-gray-900">
                  {Math.round(factCheck.confidence * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${
                    factCheck.confidence >= 0.7
                      ? 'bg-success-500'
                      : factCheck.confidence >= 0.4
                      ? 'bg-warning-500'
                      : 'bg-danger-500'
                  }`}
                  style={{ width: `${factCheck.confidence * 100}%` }}
                />
              </div>
            </div>

            <div className="mb-3">
              <p className="text-xs font-medium text-gray-600 mb-1">Sources:</p>
              <div className="flex flex-wrap gap-1">
                {factCheck.sources.map((source, index) => (
                  <span key={index} className="badge badge-info text-xs">
                    {source}
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-600">{factCheck.details}</p>
            </div>
          </div>
        ))}
      </div>

      {factChecks.length === 0 && (
        <p className="text-center text-gray-500 py-8">No fact checks performed yet</p>
      )}
    </div>
  );
}
