import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Header } from '../Header';
import { useDashboardStore } from '../../store/useDashboardStore';

vi.mock('../../store/useDashboardStore');

describe('Header', () => {
  it('renders header with title', () => {
    vi.mocked(useDashboardStore).mockReturnValue({
      candidates: [],
      intelligenceFeed: [],
    } as any);

    render(<Header />);
    
    expect(screen.getByText('HR Dashboard')).toBeInTheDocument();
  });

  it('displays active session count', () => {
    vi.mocked(useDashboardStore).mockReturnValue({
      candidates: [
        { id: '1', name: 'John', email: 'john@example.com', role: 'Dev', status: 'interviewing' as const, trustScore: 85, sessionId: 's1' },
        { id: '2', name: 'Jane', email: 'jane@example.com', role: 'Dev', status: 'interviewing' as const, trustScore: 90, sessionId: 's2' },
      ],
      intelligenceFeed: [],
    } as any);

    render(<Header />);
    
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('displays high severity alert count', () => {
    vi.mocked(useDashboardStore).mockReturnValue({
      candidates: [],
      intelligenceFeed: [
        { id: '1', type: 'contradiction', severity: 'high', message: 'Test', timestamp: new Date(), sessionId: 's1' },
        { id: '2', type: 'fact_check', severity: 'high', message: 'Test', timestamp: new Date(), sessionId: 's1' },
        { id: '3', type: 'emotion', severity: 'medium', message: 'Test', timestamp: new Date(), sessionId: 's1' },
      ],
    } as any);

    render(<Header />);
    
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('displays zero when no active sessions', () => {
    vi.mocked(useDashboardStore).mockReturnValue({
      candidates: [],
      intelligenceFeed: [],
    } as any);

    render(<Header />);
    
    expect(screen.getByText('0')).toBeInTheDocument();
  });
});
