import { useDashboardStore } from '../store/useDashboardStore';
import { Activity, Users, AlertTriangle } from 'lucide-react';

export function Header() {
  const { candidates, intelligenceFeed } = useDashboardStore();
  
  const activeCandidates = candidates.filter(c => c.status === 'interviewing').length;
  const highSeverityAlerts = intelligenceFeed.filter(i => i.severity === 'high').length;

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Aegis Lens</h1>
            <p className="text-sm text-gray-500">HR Dashboard</p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-primary-600" />
            <div className="text-sm">
              <span className="font-semibold text-gray-900">{activeCandidates}</span>
              <span className="text-gray-500"> Active Sessions</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-danger-600" />
            <div className="text-sm">
              <span className="font-semibold text-gray-900">{highSeverityAlerts}</span>
              <span className="text-gray-500"> High Alerts</span>
            </div>
          </div>

          <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
            <span className="text-sm font-medium text-gray-600">HR</span>
          </div>
        </div>
      </div>
    </header>
  );
}
