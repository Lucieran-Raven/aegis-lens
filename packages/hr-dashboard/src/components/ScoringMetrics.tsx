import { useDashboardStore } from '../store/useDashboardStore';
import { Award, TrendingUp, Target, Zap } from 'lucide-react';

export function ScoringMetrics() {
  const { scoringMetrics } = useDashboardStore();

  const metrics = scoringMetrics.length > 0 ? scoringMetrics : [
    {
      category: 'Technical Knowledge',
      score: 85,
      weight: 0.3,
      details: ['Strong understanding of core concepts', 'Good problem-solving skills', 'Knowledge of best practices'],
    },
    {
      category: 'Communication Skills',
      score: 78,
      weight: 0.25,
      details: ['Clear articulation', 'Active listening', 'Professional demeanor'],
    },
    {
      category: 'Cultural Fit',
      score: 82,
      weight: 0.2,
      details: ['Team alignment', 'Values match', 'Collaborative attitude'],
    },
    {
      category: 'Experience Relevance',
      score: 75,
      weight: 0.15,
      details: ['Relevant project experience', 'Industry knowledge', 'Role-specific skills'],
    },
    {
      category: 'Problem Solving',
      score: 88,
      weight: 0.1,
      details: ['Analytical thinking', 'Creative solutions', 'Technical approach'],
    },
  ];

  const weightedScore = metrics.reduce((total, metric) => {
    return total + (metric.score * metric.weight);
  }, 0);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-success-600';
    if (score >= 60) return 'text-warning-600';
    return 'text-danger-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-success-500';
    if (score >= 60) return 'bg-warning-500';
    return 'bg-danger-500';
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Award className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Scoring Metrics</h3>
        </div>
      </div>

      {/* Overall Score */}
      <div className="mb-6 p-4 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">Overall Weighted Score</p>
            <p className={`text-4xl font-bold ${getScoreColor(weightedScore)}`}>
              {Math.round(weightedScore)}%
            </p>
          </div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-8 h-8 text-primary-600" />
          </div>
        </div>
      </div>

      {/* Individual Metrics */}
      <div className="space-y-4">
        {metrics.map((metric, index) => (
          <div key={index} className="p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-gray-500" />
                <span className="font-medium text-gray-900">{metric.category}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-lg font-bold ${getScoreColor(metric.score)}`}>
                  {metric.score}%
                </span>
                <span className="text-xs text-gray-500">({Math.round(metric.weight * 100)}%)</span>
              </div>
            </div>

            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div
                className={`${getScoreBg(metric.score)} h-2 rounded-full transition-all`}
                style={{ width: `${metric.score}%` }}
              />
            </div>

            <div className="flex flex-wrap gap-1">
              {metric.details.map((detail, i) => (
                <span key={i} className="badge badge-info text-xs">
                  {detail}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Score Breakdown */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center gap-2 mb-3">
          <Zap className="w-4 h-4 text-primary-600" />
          <span className="font-medium text-gray-900">Score Breakdown</span>
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Technical Knowledge</span>
            <span className="font-medium text-gray-900">85% × 30% = 25.5</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Communication Skills</span>
            <span className="font-medium text-gray-900">78% × 25% = 19.5</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Cultural Fit</span>
            <span className="font-medium text-gray-900">82% × 20% = 16.4</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Experience Relevance</span>
            <span className="font-medium text-gray-900">75% × 15% = 11.25</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Problem Solving</span>
            <span className="font-medium text-gray-900">88% × 10% = 8.8</span>
          </div>
          <div className="border-t border-gray-200 pt-2 mt-2 flex justify-between font-semibold">
            <span className="text-gray-900">Total</span>
            <span className="text-primary-600">{Math.round(weightedScore)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
