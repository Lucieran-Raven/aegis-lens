import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AgentStatus } from '../AgentStatus';
import { useDashboardStore } from '../../store/useDashboardStore';

vi.mock('../../store/useDashboardStore');

describe('AgentStatus', () => {
  it('renders agent status cards', () => {
    vi.mocked(useDashboardStore).mockReturnValue({
      agentStatuses: {
        Chronos: { name: 'Chronos', status: 'running', lastUpdate: new Date() },
        Echo: { name: 'Echo', status: 'idle', lastUpdate: new Date() },
      },
    } as any);

    render(<AgentStatus />);
    
    expect(screen.getByText('Chronos')).toBeInTheDocument();
    expect(screen.getByText('Echo')).toBeInTheDocument();
    expect(screen.getByText('Video Analysis')).toBeInTheDocument();
    expect(screen.getByText('Voice Analysis')).toBeInTheDocument();
  });

  it('displays correct status badges', () => {
    vi.mocked(useDashboardStore).mockReturnValue({
      agentStatuses: {
        Chronos: { name: 'Chronos', status: 'running', lastUpdate: new Date() },
        Echo: { name: 'Echo', status: 'error', lastUpdate: new Date() },
      },
    } as any);

    render(<AgentStatus />);
    
    expect(screen.getByText('running')).toBeInTheDocument();
    expect(screen.getByText('error')).toBeInTheDocument();
  });

  it('displays agent metrics when available', () => {
    vi.mocked(useDashboardStore).mockReturnValue({
      agentStatuses: {
        Chronos: {
          name: 'Chronos',
          status: 'running',
          lastUpdate: new Date(),
          metrics: { accuracy: 95, latency: 120 },
        },
      },
    } as any);

    render(<AgentStatus />);
    
    expect(screen.getByText('Acc: 95%')).toBeInTheDocument();
    expect(screen.getByText('Lat: 120ms')).toBeInTheDocument();
  });
});
