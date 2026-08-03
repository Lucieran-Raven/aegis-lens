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

  it('displays correct trust level for different scores', () => {
    const testCases = [
      { score: 90, level: 'High Trust' },
      { score: 70, level: 'Medium Trust' },
      { score: 40, level: 'Low Trust' },
    ];

    testCases.forEach(({ score, level }) => {
      const mockCandidate = {
        id: '1',
        name: 'John Doe',
        email: 'john@example.com',
        role: 'Developer',
        status: 'interviewing' as const,
        trustScore: score,
        sessionId: 'session-123',
      };

      vi.mocked(useDashboardStore).mockReturnValue({
        selectedCandidate: mockCandidate,
      } as any);

      const { unmount } = render(<TrustScore />);
      
      expect(screen.getByText(`${score}%`)).toBeInTheDocument();
      expect(screen.getByText(level)).toBeInTheDocument();
      
      unmount();
    });
  });
});
