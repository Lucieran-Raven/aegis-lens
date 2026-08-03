import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { App } from '../../App';

describe('Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the app and navigates to join page', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    expect(screen.getByText('Aegis Lens')).toBeInTheDocument();
    expect(screen.getByText('Candidate Interview Portal')).toBeInTheDocument();
  });

  it('allows user to fill in name and session ID', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

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
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    const joinButton = screen.getByRole('button', { name: /join session/i });
    expect(joinButton).toBeDisabled();
  });

  it('enables join button when all required fields are filled and permissions granted', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

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
