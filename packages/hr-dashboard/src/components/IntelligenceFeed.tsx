import { useDashboardStore } from '../store/useDashboardStore';
import { Brain, AlertTriangle, CheckCircle, Info } from 'lucide-react';

export function IntelligenceFeed() {
  const { intelligenceFeed, clearIntelligenceFeed } = useDashboardStore();

  const getIcon = (type: string) => {
    switch (type) {
      case 'contradiction':
        return <AlertTriangle className="w-5 h-5 text-danger-600" />;
      case 'fact_check':
        return <CheckCircle className="w-5 h-5 text-success-600" />;
      case 'emotion':
        return <Info className="w-5 h-5 text-primary-600" />;
      default:
        return <Brain className="w-5 h-5 text-secondary-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'border-l-danger-500 bg-danger-50';
      case 'medium':
        return 'border-l-warning-500 bg-warning-50';
      default:
        return 'border-l-primary-500 bg-primary-50';
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
        <h3 className="text-lg font-semibold text-gray-900">Intelligence Feed</h3>
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-primary-600" />
          <button
            onClick={clearIntelligenceFeed}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="space-y-3 max-h-80 overflow-y-auto">
        {intelligenceFeed.length === 0 ? (
          <p className="text-center text-gray-500 py-8">No intelligence items</p>
        ) : (
          intelligenceFeed.map((item) => (
            <div
              key={item.id}
              className={`p-3 rounded border-l-4 ${getSeverityColor(item.severity)} animate-fade-in`}
            >
              <div className="flex items-start gap-3">
                {getIcon(item.type)}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`badge ${getSeverityBadge(item.severity)}`}>
                      {item.severity}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-900">{item.message}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
