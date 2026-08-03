import { useState } from 'react';
import { useDashboardStore } from '../store/useDashboardStore';
import { MessageSquare, Send, Sparkles } from 'lucide-react';

export function QuestionCoPilot() {
  const { questionQueue, addQuestion, updateQuestion } = useDashboardStore();
  const [suggestedQuestion, setSuggestedQuestion] = useState('');

  const handleSuggestQuestion = () => {
    if (suggestedQuestion.trim()) {
      addQuestion({
        id: Date.now().toString(),
        text: suggestedQuestion,
        suggestedBy: 'HR',
        status: 'pending',
        timestamp: new Date(),
      });
      setSuggestedQuestion('');
    }
  };

  const handleAskQuestion = (id: string) => {
    updateQuestion(id, { status: 'asked' });
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Question CoPilot</h3>
        <Sparkles className="w-5 h-5 text-primary-600" />
      </div>

      {/* Suggest Question Input */}
      <div className="mb-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={suggestedQuestion}
            onChange={(e) => setSuggestedQuestion(e.target.value)}
            placeholder="Suggest a follow-up question..."
            className="input-field"
            onKeyPress={(e) => e.key === 'Enter' && handleSuggestQuestion()}
          />
          <button
            onClick={handleSuggestQuestion}
            className="btn-primary flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Suggest
          </button>
        </div>
      </div>

      {/* Question Queue */}
      <div className="space-y-3 max-h-60 overflow-y-auto">
        {questionQueue.length === 0 ? (
          <p className="text-center text-gray-500 py-8">No questions in queue</p>
        ) : (
          questionQueue.map((question) => (
            <div
              key={question.id}
              className="p-3 bg-gray-50 rounded-lg border border-gray-200"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-2 flex-1">
                  <MessageSquare className="w-4 h-4 text-primary-600 mt-1 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">{question.text}</p>
                    {question.suggestedBy && (
                      <p className="text-xs text-gray-500 mt-1">
                        Suggested by: {question.suggestedBy}
                      </p>
                    )}
                  </div>
                </div>
                
                {question.status === 'pending' && (
                  <button
                    onClick={() => handleAskQuestion(question.id)}
                    className="btn-sm btn-primary text-xs"
                  >
                    Ask
                  </button>
                )}
                
                {question.status === 'asked' && (
                  <span className="badge badge-success">Asked</span>
                )}
                
                {question.status === 'answered' && (
                  <span className="badge badge-info">Answered</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
