import { useDashboardStore } from '../store/useDashboardStore';
import { Cpu, Activity, AlertCircle, CheckCircle } from 'lucide-react';

export function AgentStatus() {
  const { agentStatuses } = useDashboardStore();

  const agents = [
    { name: 'Chronos', description: 'Video Analysis' },
    { name: 'Echo', description: 'Voice Analysis' },
    { name: 'Iris', description: 'Lip Sync Detection' },
    { name: 'Lipsync', description: 'Audio-Video Sync' },
    { name: 'Oracle', description: 'Fact Checking' },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <CheckCircle className="w-5 h-5 text-success-600" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-danger-600" />;
      default:
        return <Activity className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-success-100 text-success-800';
      case 'error':
        return 'bg-danger-100 text-danger-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Agent Status</h3>
        <Cpu className="w-5 h-5 text-primary-600" />
      </div>

      <div className="space-y-3">
        {agents.map((agent) => {
          const status = agentStatuses[agent.name] || { status: 'idle', lastUpdate: new Date() };
          
          return (
            <div
              key={agent.name}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center gap-3">
                {getStatusIcon(status.status)}
                <div>
                  <h4 className="font-medium text-gray-900">{agent.name}</h4>
                  <p className="text-sm text-gray-500">{agent.description}</p>
                </div>
              </div>

              <div className="text-right">
                <span className={`badge ${getStatusColor(status.status)}`}>
                  {status.status}
                </span>
                {status.metrics && (
                  <div className="mt-1 text-xs text-gray-500">
                    {status.metrics.accuracy && `Acc: ${status.metrics.accuracy}%`}
                    {status.metrics.latency && ` | Lat: ${status.metrics.latency}ms`}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
