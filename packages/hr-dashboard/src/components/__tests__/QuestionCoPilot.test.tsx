import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QuestionCoPilot } from '../QuestionCoPilot';
import { useDashboardStore } from '../../store/useDashboardStore';

vi.mock('../../store/useDashboardStore');

describe('QuestionCoPilot', () => {
  it('renders empty state when no questions', () => {
    vi.mocked(useDashboardStore).mockReturnValue({
      questionQueue: [],
      addQuestion: vi.fn(),
      updateQuestion: vi.fn(),
    } as any);

    render(<QuestionCoPilot />);
    
    expect(screen.getByText('No questions in queue')).toBeInTheDocument();
  });

  it('renders questions in queue', () => {
    const mockQuestions = [
      {
        id: '1',
        text: 'What is your experience with React?',
        suggestedBy: 'HR',
        status: 'pending' as const,
        timestamp: new Date(),
      },
    ];

    vi.mocked(useDashboardStore).mockReturnValue({
      questionQueue: mockQuestions,
      addQuestion: vi.fn(),
      updateQuestion: vi.fn(),
    } as any);

    render(<QuestionCoPilot />);
    
    expect(screen.getByText('What is your experience with React?')).toBeInTheDocument();
    expect(screen.getByText('Suggested by: HR')).toBeInTheDocument();
  });

  it('adds question when suggest button is clicked', () => {
    const addMock = vi.fn();
    vi.mocked(useDashboardStore).mockReturnValue({
      questionQueue: [],
      addQuestion: addMock,
      updateQuestion: vi.fn(),
    } as any);

    render(<QuestionCoPilot />);
    
    const input = screen.getByPlaceholderText('Suggest a follow-up question...');
    fireEvent.change(input, { target: { value: 'Test question' } });
    
    const suggestButton = screen.getByText('Suggest');
    fireEvent.click(suggestButton);
    
    expect(addMock).toHaveBeenCalledWith({
      id: expect.any(String),
      text: 'Test question',
      suggestedBy: 'HR',
      status: 'pending',
      timestamp: expect.any(Date),
    });
  });

  it('updates question status when ask button is clicked', () => {
    const updateMock = vi.fn();
    const mockQuestions = [
      {
        id: '1',
        text: 'Test question',
        suggestedBy: 'HR',
        status: 'pending' as const,
        timestamp: new Date(),
      },
    ];

    vi.mocked(useDashboardStore).mockReturnValue({
      questionQueue: mockQuestions,
      addQuestion: vi.fn(),
      updateQuestion: updateMock,
    } as any);

    render(<QuestionCoPilot />);
    
    const askButton = screen.getByText('Ask');
    fireEvent.click(askButton);
    
    expect(updateMock).toHaveBeenCalledWith('1', { status: 'asked' });
  });

  it('displays correct badges for different question statuses', () => {
    const mockQuestions = [
      {
        id: '1',
        text: 'Pending question',
        suggestedBy: 'HR',
        status: 'pending' as const,
        timestamp: new Date(),
      },
      {
        id: '2',
        text: 'Asked question',
        suggestedBy: 'HR',
        status: 'asked' as const,
        timestamp: new Date(),
      },
      {
        id: '3',
        text: 'Answered question',
        suggestedBy: 'HR',
        status: 'answered' as const,
        timestamp: new Date(),
      },
    ];

    vi.mocked(useDashboardStore).mockReturnValue({
      questionQueue: mockQuestions,
      addQuestion: vi.fn(),
      updateQuestion: vi.fn(),
    } as any);

    render(<QuestionCoPilot />);
    
    expect(screen.getByText('Ask')).toBeInTheDocument();
    expect(screen.getByText('Asked')).toBeInTheDocument();
    expect(screen.getByText('Answered')).toBeInTheDocument();
  });
});
