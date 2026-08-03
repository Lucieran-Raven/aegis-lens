import { useD3TimeSeries, TimeSeriesData, createLineChart } from '../hooks/useD3Chart';
import { Heart, TrendingUp, Smile, Frown, Meh } from 'lucide-react';

export function EmotionalDashboard() {
  // Mock emotional data over time
  const emotionalData: TimeSeriesData[] = [
    { timestamp: new Date(Date.now() - 600000), value: 75 },
    { timestamp: new Date(Date.now() - 480000), value: 80 },
    { timestamp: new Date(Date.now() - 360000), value: 70 },
    { timestamp: new Date(Date.now() - 240000), value: 85 },
    { timestamp: new Date(Date.now() - 120000), value: 78 },
    { timestamp: new Date(), value: 82 },
  ];

  const chartRef = useD3TimeSeries(createLineChart, emotionalData);

  const emotions = [
    { name: 'Confidence', value: 85, icon: <TrendingUp className="w-4 h-4" />, color: 'text-success-600' },
    { name: 'Stress', value: 35, icon: <Frown className="w-4 h-4" />, color: 'text-warning-600' },
    { name: 'Engagement', value: 78, icon: <Smile className="w-4 h-4" />, color: 'text-primary-600' },
    { name: 'Neutrality', value: 45, icon: <Meh className="w-4 h-4" />, color: 'text-gray-600' },
  ];

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Heart className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Emotional Dashboard</h3>
        </div>
      </div>

      {/* Emotional Metrics */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        {emotions.map((emotion) => (
          <div key={emotion.name} className="p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className={emotion.color}>{emotion.icon}</span>
                <span className="text-sm font-medium text-gray-700">{emotion.name}</span>
              </div>
              <span className={`text-lg font-bold ${emotion.color}`}>{emotion.value}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  emotion.value >= 70
                    ? 'bg-success-500'
                    : emotion.value >= 40
                    ? 'bg-warning-500'
                    : 'bg-danger-500'
                }`}
                style={{ width: `${emotion.value}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Emotional Trend Chart */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-3">Emotional Trend</h4>
        <div className="flex justify-center bg-gray-50 rounded-lg p-4">
          <svg ref={chartRef} />
        </div>
      </div>

      {/* Emotional Insights */}
      <div className="mt-4 p-3 bg-primary-50 rounded-lg border border-primary-200">
        <p className="text-sm text-primary-800">
          <span className="font-semibold">Insight:</span> Candidate shows high confidence
          and engagement levels with manageable stress. Emotional stability is consistent
          throughout the interview.
        </p>
      </div>
    </div>
  );
}
