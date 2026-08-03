import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TrustScore } from '../TrustScore';
import { useDashboardStore } from '../../store/useDashboardStore';

vi.mock('../../store/useDashboardStore');

describe('TrustScore', () => {
  it('renders no candidate selected message', () => {
    vi.mocked(useDashboardStore).mockReturnValue({
      selectedCandidate: null,
    } as any);

    render(<TrustScore />);
    
    expect(screen.getByText('No candidate selected')).toBeInTheDocument();
  });

  it('renders trust score with candidate data', () => {
    const mockCandidate = {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      role: 'Developer',
      status: 'interviewing' as const,
      trustScore: 85,
      sessionId: 'session-123',
    };

    vi.mocked(useDashboardStore).mockReturnValue({
      selectedCandidate: mockCandidate,
    } as any);

    render(<TrustScore />);
    
    expect(screen.getByText('85%')).toBeInTheDocument();
    expect(screen.getByText('High Trust')).toBeInTheDocument();
  });

  it('displays High Trust for score >= 80', () => {
    const mockCandidate = {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      role: 'Developer',
      status: 'interviewing' as const,
      trustScore: 90,
      sessionId: 'session-123',
    };

    vi.mocked(useDashboardStore).mockReturnValue({
      selectedCandidate: mockCandidate,
    } as any);

    render(<TrustScore />);
    
    expect(screen.getByText('90%')).toBeInTheDocument();
    expect(screen.getByText('High Trust')).toBeInTheDocument();
  });

  it('displays Medium Trust for score >= 60', () => {
    const mockCandidate = {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      role: 'Developer',
      status: 'interviewing' as const,
      trustScore: 70,
      sessionId: 'session-123',
    };

    vi.mocked(useDashboardStore).mockReturnValue({
      selectedCandidate: mockCandidate,
    } as any);

    render(<TrustScore />);
    
    expect(screen.getByText('70%')).toBeInTheDocument();
    expect(screen.getByText('Medium Trust')).toBeInTheDocument();
  });

  it('displays Low Trust for score < 60', () => {
    const mockCandidate = {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      role: 'Developer',
      status: 'interviewing' as const,
      trustScore: 40,
      sessionId: 'session-123',
    };

    vi.mocked(useDashboardStore).mockReturnValue({
      selectedCandidate: mockCandidate,
    } as any);

    render(<TrustScore />);
    
    expect(screen.getByText('40%')).toBeInTheDocument();
    expect(screen.getByText('Low Trust')).toBeInTheDocument();
  });
});
