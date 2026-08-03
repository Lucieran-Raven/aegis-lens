import { Wifi, WifiOff, Signal, Activity, Shield, ShieldAlert } from 'lucide-react';

interface StatusBarProps {
  isConnected: boolean;
  latency?: number;
  trustScore?: number;
  className?: string;
}

export function StatusBar({ isConnected, latency, trustScore, className = '' }: StatusBarProps) {
  const getLatencyColor = (ms: number) => {
    if (ms < 100) return 'text-success-400';
    if (ms < 200) return 'text-warning-400';
    return 'text-error-400';
  };

  const getTrustScoreColor = (score: number) => {
    if (score >= 80) return 'text-success-400';
    if (score >= 60) return 'text-warning-400';
    return 'text-error-400';
  };

  const getTrustScoreIcon = (score: number) => {
    if (score >= 80) return <Shield className="w-4 h-4" />;
    return <ShieldAlert className="w-4 h-4" />;
  };

  return (
    <div className={`bg-gray-800 border-t border-gray-700 px-6 py-2 ${className}`}>
      <div className="max-w-7xl mx-auto flex items-center justify-between text-sm">
        <div className="flex items-center gap-6">
          {/* Connection Status */}
          <div className="flex items-center gap-2">
            {isConnected ? (
              <Wifi className="w-4 h-4 text-success-400" />
            ) : (
              <WifiOff className="w-4 h-4 text-error-400" />
            )}
            <span className={isConnected ? 'text-success-400' : 'text-error-400'}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {/* Latency */}
          {latency !== undefined && (
            <div className="flex items-center gap-2">
              <Signal className="w-4 h-4" />
              <span className={getLatencyColor(latency)}>{latency}ms</span>
            </div>
          )}

          {/* Activity Indicator */}
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-primary-400 animate-pulse" />
            <span className="text-gray-400">Active</span>
          </div>
        </div>

        {/* Trust Score */}
        {trustScore !== undefined && (
          <div className="flex items-center gap-2">
            <span className={`flex items-center gap-1 ${getTrustScoreColor(trustScore)}`}>
              {getTrustScoreIcon(trustScore)}
              <span className="font-semibold">Trust: {trustScore}%</span>
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
