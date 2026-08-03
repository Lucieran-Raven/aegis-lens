import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Controls } from '../Controls';

describe('Controls', () => {
  const mockHandlers = {
    onToggleCamera: vi.fn(),
    onToggleMicrophone: vi.fn(),
    onToggleScreenShare: vi.fn(),
    onEndCall: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all control buttons', () => {
    render(
      <Controls
        isCameraEnabled={true}
        isMicrophoneEnabled={true}
        isScreenSharing={false}
        {...mockHandlers}
      />
    );

    expect(screen.getByRole('button', { name: /mute/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /camera/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /screen/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /end/i })).toBeInTheDocument();
  });

  it('calls onToggleMicrophone when microphone button is clicked', () => {
    render(
      <Controls
        isCameraEnabled={true}
        isMicrophoneEnabled={true}
        isScreenSharing={false}
        {...mockHandlers}
      />
    );

    screen.getByRole('button', { name: /mute/i }).click();
    expect(mockHandlers.onToggleMicrophone).toHaveBeenCalledTimes(1);
  });

  it('calls onToggleCamera when camera button is clicked', () => {
    render(
      <Controls
        isCameraEnabled={true}
        isMicrophoneEnabled={true}
        isScreenSharing={false}
        {...mockHandlers}
      />
    );

    screen.getByRole('button', { name: /camera/i }).click();
    expect(mockHandlers.onToggleCamera).toHaveBeenCalledTimes(1);
  });

  it('calls onToggleScreenShare when screen share button is clicked', () => {
    render(
      <Controls
        isCameraEnabled={true}
        isMicrophoneEnabled={true}
        isScreenSharing={false}
        {...mockHandlers}
      />
    );

    screen.getByRole('button', { name: /screen/i }).click();
    expect(mockHandlers.onToggleScreenShare).toHaveBeenCalledTimes(1);
  });

  it('calls onEndCall when end call button is clicked', () => {
    render(
      <Controls
        isCameraEnabled={true}
        isMicrophoneEnabled={true}
        isScreenSharing={false}
        {...mockHandlers}
      />
    );

    screen.getByRole('button', { name: /end/i }).click();
    expect(mockHandlers.onEndCall).toHaveBeenCalledTimes(1);
  });

  it('does not render settings button when onOpenSettings is not provided', () => {
    render(
      <Controls
        isCameraEnabled={true}
        isMicrophoneEnabled={true}
        isScreenSharing={false}
        {...mockHandlers}
      />
    );

    expect(screen.queryByRole('button', { name: /settings/i })).not.toBeInTheDocument();
  });

  it('renders settings button when onOpenSettings is provided', () => {
    const mockOpenSettings = vi.fn();
    render(
      <Controls
        isCameraEnabled={true}
        isMicrophoneEnabled={true}
        isScreenSharing={false}
        onOpenSettings={mockOpenSettings}
        {...mockHandlers}
      />
    );

    expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
  });
});
