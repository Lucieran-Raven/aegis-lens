import { useDashboardStore } from '../store/useDashboardStore';
import { Shield, TrendingUp, TrendingDown } from 'lucide-react';

export function TrustScore() {
  const { selectedCandidate } = useDashboardStore();

  if (!selectedCandidate) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Trust Score</h3>
        <p className="text-gray-500">No candidate selected</p>
      </div>
    );
  }

  const score = selectedCandidate.trustScore;
  const scoreColor = score >= 80 ? 'text-success-600' : score >= 60 ? 'text-warning-600' : 'text-danger-600';
  const scoreBg = score >= 80 ? 'bg-success-500' : score >= 60 ? 'bg-warning-500' : 'bg-danger-500';

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Trust Score</h3>
        <Shield className="w-5 h-5 text-primary-600" />
      </div>

      <div className="text-center mb-6">
        <div className={`text-5xl font-bold ${scoreColor} mb-2`}>{score}%</div>
        <p className="text-sm text-gray-500">
          {score >= 80 ? 'High Trust' : score >= 60 ? 'Medium Trust' : 'Low Trust'}
        </p>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-3 mb-6">
        <div
          className={`${scoreBg} h-3 rounded-full transition-all duration-500`}
          style={{ width: `${score}%` }}
        />
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Verbal Consistency</span>
          <div className="flex items-center gap-1">
            <TrendingUp className="w-4 h-4 text-success-600" />
            <span className="font-medium text-gray-900">85%</span>
          </div>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Non-verbal Cues</span>
          <div className="flex items-center gap-1">
            <TrendingUp className="w-4 h-4 text-success-600" />
            <span className="font-medium text-gray-900">78%</span>
          </div>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Fact Accuracy</span>
          <div className="flex items-center gap-1">
            <TrendingDown className="w-4 h-4 text-warning-600" />
            <span className="font-medium text-gray-900">72%</span>
          </div>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Emotional Stability</span>
          <div className="flex items-center gap-1">
            <TrendingUp className="w-4 h-4 text-success-600" />
            <span className="font-medium text-gray-900">90%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
