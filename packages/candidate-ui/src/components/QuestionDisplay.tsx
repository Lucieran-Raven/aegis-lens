import { Clock, MessageSquare } from 'lucide-react';

interface QuestionDisplayProps {
  question: string;
  questionNumber: number;
  totalQuestions: number;
  timeRemaining?: number;
  className?: string;
}

export function QuestionDisplay({
  question,
  questionNumber,
  totalQuestions,
  timeRemaining,
  className = '',
}: QuestionDisplayProps) {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimeColor = (seconds: number) => {
    if (seconds > 60) return 'text-success-400';
    if (seconds > 30) return 'text-warning-400';
    return 'text-error-400';
  };

  return (
    <div className={`card bg-gray-700 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-primary-400" />
          <h3 className="text-white font-semibold">Question {questionNumber} of {totalQuestions}</h3>
        </div>
        {timeRemaining !== undefined && (
          <div className={`flex items-center gap-2 ${getTimeColor(timeRemaining)}`}>
            <Clock className="w-4 h-4" />
            <span className="font-mono font-semibold">{formatTime(timeRemaining)}</span>
          </div>
        )}
      </div>

      <div className="bg-gray-800 rounded-lg p-4">
        <p className="text-gray-200 text-lg leading-relaxed">{question}</p>
      </div>

      <div className="mt-4 flex items-center justify-between text-sm text-gray-400">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-primary-500" />
          <span>Live</span>
        </div>
        <div className="flex items-center gap-4">
          <span>Answer clearly and concisely</span>
          <span>•</span>
          <span>Take your time</span>
        </div>
      </div>
    </div>
  );
}
