import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { Join } from '../../routes/Join';

describe('Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the join page', () => {
    render(<Join />);

    expect(screen.getByText('Aegis Lens')).toBeInTheDocument();
    expect(screen.getByText('Candidate Interview Portal')).toBeInTheDocument();
  });

  it('allows user to fill in name and session ID', async () => {
    render(<Join />);

    const nameInput = screen.getByLabelText(/your name/i);
    const sessionIdInput = screen.getByLabelText(/session id/i);

    expect(nameInput).toBeInTheDocument();
    expect(sessionIdInput).toBeInTheDocument();

    nameInput?.setAttribute('value', 'John Doe');
    sessionIdInput?.setAttribute('value', 'test-session-123');

    expect(nameInput).toHaveValue('John Doe');
    expect(sessionIdInput).toHaveValue('test-session-123');
  });

  it('disables join button when required fields are empty', () => {
    render(<Join />);

    const joinButton = screen.getByRole('button', { name: /join session/i });
    expect(joinButton).toBeDisabled();
  });

  it('enables join button when all required fields are filled and permissions granted', async () => {
    render(<Join />);

    const nameInput = screen.getByLabelText(/your name/i);
    const sessionIdInput = screen.getByLabelText(/session id/i);

    nameInput?.setAttribute('value', 'John Doe');
    sessionIdInput?.setAttribute('value', 'test-session-123');

    // Simulate permission grant
    const testButton = screen.getByRole('button', { name: /test camera/i });
    testButton.click();

    await waitFor(() => {
      const joinButton = screen.getByRole('button', { name: /join session/i });
      expect(joinButton).not.toBeDisabled();
    });
  });
});
