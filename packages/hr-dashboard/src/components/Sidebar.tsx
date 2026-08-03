import { useDashboardStore } from '../store/useDashboardStore';
import { User, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export function Sidebar() {
  const { candidates, selectedCandidate, setSelectedCandidate } = useDashboardStore();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'interviewing':
        return <Clock className="w-4 h-4 text-primary-600" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-success-600" />;
      case 'rejected':
        return <XCircle className="w-4 h-4 text-danger-600" />;
      default:
        return <AlertCircle className="w-4 h-4 text-warning-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'interviewing':
        return 'bg-primary-100 text-primary-800';
      case 'completed':
        return 'bg-success-100 text-success-800';
      case 'rejected':
        return 'bg-danger-100 text-danger-800';
      default:
        return 'bg-warning-100 text-warning-800';
    }
  };

  return (
    <aside className="w-80 bg-white border-r border-gray-200 h-[calc(100vh-73px)] overflow-y-auto">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Candidates</h2>
        <p className="text-sm text-gray-500">{candidates.length} total</p>
      </div>

      <div className="p-4 space-y-3">
        {candidates.map((candidate) => (
          <button
            key={candidate.id}
            onClick={() => setSelectedCandidate(candidate)}
            className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
              selectedCandidate?.id === candidate.id
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                <User className="w-5 h-5 text-gray-600" />
              </div>
              
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-gray-900 truncate">{candidate.name}</h3>
                <p className="text-sm text-gray-500 truncate">{candidate.role}</p>
                
                <div className="flex items-center gap-2 mt-2">
                  <span className={`badge ${getStatusColor(candidate.status)}`}>
                    {candidate.status}
                  </span>
                  <span className="text-sm font-semibold text-gray-900">
                    {candidate.trustScore}%
                  </span>
                </div>
              </div>

              {getStatusIcon(candidate.status)}
            </div>
          </button>
        ))}
      </div>
    </aside>
  );
}
