import { AlertTriangle, Clock, FileText } from 'lucide-react';

interface Contradiction {
  id: string;
  statement1: string;
  statement2: string;
  timestamp1: Date;
  timestamp2: Date;
  severity: 'low' | 'medium' | 'high';
  context: string;
}

export function ContradictionAlerts() {
  const contradictions: Contradiction[] = [
    {
      id: '1',
      statement1: 'I have 5 years of experience with Python',
      statement2: 'I started learning Python 2 years ago',
      timestamp1: new Date(Date.now() - 600000),
      timestamp2: new Date(Date.now() - 300000),
      severity: 'high',
      context: 'Technical skills discussion',
    },
    {
      id: '2',
      statement1: 'I led a team of 10 developers',
      statement2: 'I have never managed a team before',
      timestamp1: new Date(Date.now() - 480000),
      timestamp2: new Date(Date.now() - 240000),
      severity: 'high',
      context: 'Leadership experience',
    },
    {
      id: '3',
      statement1: 'I am proficient in cloud technologies',
      statement2: 'I have only used cloud services for personal projects',
      timestamp1: new Date(Date.now() - 360000),
      timestamp2: new Date(Date.now() - 180000),
      severity: 'medium',
      context: 'Cloud experience',
    },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'border-danger-500 bg-danger-50';
      case 'medium':
        return 'border-warning-500 bg-warning-50';
      default:
        return 'border-primary-500 bg-primary-50';
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'badge-danger';
      case 'medium':
        return 'badge-warning';
      default:
        return 'badge-info';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-danger-600" />
          <h3 className="text-lg font-semibold text-gray-900">Contradiction Alerts</h3>
        </div>
        <span className="badge badge-danger">{contradictions.length} Found</span>
      </div>

      <div className="space-y-4 max-h-80 overflow-y-auto">
        {contradictions.map((contradiction) => (
          <div
            key={contradiction.id}
            className={`p-4 rounded-lg border-l-4 ${getSeverityColor(contradiction.severity)}`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className={`badge ${getSeverityBadge(contradiction.severity)}`}>
                  {contradiction.severity}
                </span>
                <span className="text-xs text-gray-500">{contradiction.context}</span>
              </div>
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Clock className="w-3 h-3" />
                {contradiction.timestamp2.toLocaleTimeString()}
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-xs font-medium text-gray-600">
                  1
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{contradiction.statement1}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {contradiction.timestamp1.toLocaleTimeString()}
                  </p>
                </div>
              </div>

              <div className="flex gap-3">
                <div className="flex-shrink-0 w-6 h-6 bg-danger-200 rounded-full flex items-center justify-center text-xs font-medium text-danger-600">
                  2
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{contradiction.statement2}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {contradiction.timestamp2.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-3 pt-3 border-t border-gray-200">
              <button className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1">
                <FileText className="w-4 h-4" />
                View full context
              </button>
            </div>
          </div>
        ))}
      </div>

      {contradictions.length === 0 && (
        <p className="text-center text-gray-500 py-8">No contradictions detected</p>
      )}
    </div>
  );
}
