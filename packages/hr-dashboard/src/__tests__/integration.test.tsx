import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';

vi.mock('../hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    connectionStatus: 'connected',
    lastMessage: null,
  }),
}));

describe('Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the dashboard page', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText('HR Dashboard')).toBeInTheDocument();
  });

  it('navigates to dashboard route', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText('Candidates')).toBeInTheDocument();
  });

  it('displays all dashboard components', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText('Trust Score')).toBeInTheDocument();
    expect(screen.getByText('Agent Status')).toBeInTheDocument();
    expect(screen.getByText('Intelligence Feed')).toBeInTheDocument();
    expect(screen.getByText('Question CoPilot')).toBeInTheDocument();
    expect(screen.getByText('Candidate Analytics')).toBeInTheDocument();
    expect(screen.getByText('Video Feed')).toBeInTheDocument();
    expect(screen.getByText('Live Transcript')).toBeInTheDocument();
    expect(screen.getByText('Emotional Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Contradiction Alerts')).toBeInTheDocument();
    expect(screen.getByText('Real-time Fact Check')).toBeInTheDocument();
    expect(screen.getByText('Question Queue')).toBeInTheDocument();
    expect(screen.getByText('Scoring Metrics')).toBeInTheDocument();
    expect(screen.getByText('Session Controls')).toBeInTheDocument();
  });

  it('shows connection status indicator', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText(/Connection/i)).toBeInTheDocument();
  });

  it('handles candidate selection in sidebar', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );

    const candidateButtons = screen.getAllByRole('button');
    expect(candidateButtons.length).toBeGreaterThan(0);
  });

  it('displays header with session and alert counts', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText('Active Sessions')).toBeInTheDocument();
    expect(screen.getByText('High Severity Alerts')).toBeInTheDocument();
  });
});
