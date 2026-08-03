import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { VideoFeed } from '../VideoFeed';

describe('VideoFeed', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders placeholder when no stream is provided', () => {
    render(<VideoFeed stream={null} />);
    expect(screen.getByText('No video signal')).toBeInTheDocument();
  });

  it('renders with custom placeholder text', () => {
    render(<VideoFeed stream={null} placeholder="Custom placeholder" />);
    expect(screen.getByText('Custom placeholder')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(<VideoFeed stream={null} className="custom-class" />);
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('renders video element when stream is provided', () => {
    const mockStream = new MediaStream();
    const { container } = render(<VideoFeed stream={mockStream} />);
    const video = container.querySelector('video');
    expect(video).toBeInTheDocument();
    expect(video).toHaveProperty('muted', false);
  });

  it('mutes video when muted prop is true', () => {
    const mockStream = new MediaStream();
    const { container } = render(<VideoFeed stream={mockStream} muted={true} />);
    const video = container.querySelector('video');
    expect(video).toHaveProperty('muted', true);
  });
});
