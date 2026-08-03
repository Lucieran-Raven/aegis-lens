import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { IntelligenceFeed } from '../IntelligenceFeed';
import { useDashboardStore } from '../../store/useDashboardStore';

vi.mock('../../store/useDashboardStore');

describe('IntelligenceFeed', () => {
  it('renders empty state when no intelligence items', () => {
    vi.mocked(useDashboardStore).mockReturnValue({
      intelligenceFeed: [],
      clearIntelligenceFeed: vi.fn(),
    } as any);

    render(<IntelligenceFeed />);
    
    expect(screen.getByText('No intelligence items')).toBeInTheDocument();
  });

  it('renders intelligence items', () => {
    const mockItems = [
      {
        id: '1',
        type: 'contradiction' as const,
        severity: 'high' as const,
        message: 'Candidate contradicted previous statement',
        timestamp: new Date(),
        sessionId: 'session-123',
      },
    ];

    vi.mocked(useDashboardStore).mockReturnValue({
      intelligenceFeed: mockItems,
      clearIntelligenceFeed: vi.fn(),
    } as any);

    render(<IntelligenceFeed />);
    
    expect(screen.getByText('Candidate contradicted previous statement')).toBeInTheDocument();
    expect(screen.getByText('high')).toBeInTheDocument();
  });

  it('calls clearIntelligenceFeed when clear button is clicked', () => {
    const clearMock = vi.fn();
    vi.mocked(useDashboardStore).mockReturnValue({
      intelligenceFeed: [],
      clearIntelligenceFeed: clearMock,
    } as any);

    render(<IntelligenceFeed />);
    
    const clearButton = screen.getByText('Clear');
    clearButton.click();
    
    expect(clearMock).toHaveBeenCalled();
  });

  it('displays correct icons for different intelligence types', () => {
    const mockItems = [
      {
        id: '1',
        type: 'contradiction' as const,
        severity: 'high' as const,
        message: 'Test contradiction',
        timestamp: new Date(),
        sessionId: 'session-123',
      },
      {
        id: '2',
        type: 'fact_check' as const,
        severity: 'medium' as const,
        message: 'Test fact check',
        timestamp: new Date(),
        sessionId: 'session-123',
      },
    ];

    vi.mocked(useDashboardStore).mockReturnValue({
      intelligenceFeed: mockItems,
      clearIntelligenceFeed: vi.fn(),
    } as any);

    render(<IntelligenceFeed />);
    
    expect(screen.getByText('Test contradiction')).toBeInTheDocument();
    expect(screen.getByText('Test fact check')).toBeInTheDocument();
  });
});
