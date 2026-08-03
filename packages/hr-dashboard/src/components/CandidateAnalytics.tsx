import { useDashboardStore } from '../store/useDashboardStore';
import { useD3Chart, ChartData, createBarChart, createPieChart } from '../hooks/useD3Chart';
import { BarChart3 } from 'lucide-react';

export function CandidateAnalytics() {
  const { selectedCandidate } = useDashboardStore();

  if (!selectedCandidate) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Candidate Analytics</h3>
        <p className="text-gray-500">No candidate selected</p>
      </div>
    );
  }

  // Mock data for skill distribution
  const skillData: ChartData[] = [
    { label: 'Technical', value: 85, color: '#0ea5e9' },
    { label: 'Communication', value: 78, color: '#a855f7' },
    { label: 'Problem Solving', value: 92, color: '#22c55e' },
    { label: 'Leadership', value: 70, color: '#f59e0b' },
    { label: 'Teamwork', value: 88, color: '#ef4444' },
  ];

  // Mock data for answer categories
  const answerData: ChartData[] = [
    { label: 'Accurate', value: 45, color: '#22c55e' },
    { label: 'Partially Accurate', value: 30, color: '#f59e0b' },
    { label: 'Inaccurate', value: 15, color: '#ef4444' },
    { label: 'Unsure', value: 10, color: '#6b7280' },
  ];

  const barChartRef = useD3Chart(createBarChart, skillData);
  const pieChartRef = useD3Chart(createPieChart, answerData);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Candidate Analytics</h3>
        <BarChart3 className="w-5 h-5 text-primary-600" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Skills Bar Chart */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Skill Assessment</h4>
          <div className="flex justify-center">
            <svg ref={barChartRef} />
          </div>
        </div>

        {/* Answer Distribution Pie Chart */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Answer Distribution</h4>
          <div className="flex justify-center">
            <svg ref={pieChartRef} />
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500">Questions Answered</p>
          <p className="text-2xl font-bold text-gray-900">24</p>
        </div>
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500">Average Response Time</p>
          <p className="text-2xl font-bold text-gray-900">12s</p>
        </div>
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500">Contradictions Found</p>
          <p className="text-2xl font-bold text-danger-600">3</p>
        </div>
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500">Fact Check Accuracy</p>
          <p className="text-2xl font-bold text-success-600">87%</p>
        </div>
      </div>
    </div>
  );
}
