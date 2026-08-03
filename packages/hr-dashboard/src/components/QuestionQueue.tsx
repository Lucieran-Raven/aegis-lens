import { useDashboardStore } from '../store/useDashboardStore';
import { List, Clock, CheckCircle, Circle, ArrowUp, ArrowDown, Trash2 } from 'lucide-react';

export function QuestionQueue() {
  const { questionQueue, updateQuestion } = useDashboardStore();

  const handleMoveUp = (index: number) => {
    if (index > 0) {
      const newQueue = [...questionQueue];
      [newQueue[index], newQueue[index - 1]] = [newQueue[index - 1], newQueue[index]];
      // Update store with new order
      newQueue.forEach((q) => updateQuestion(q.id, { ...q }));
    }
  };

  const handleMoveDown = (index: number) => {
    if (index < questionQueue.length - 1) {
      const newQueue = [...questionQueue];
      [newQueue[index], newQueue[index + 1]] = [newQueue[index + 1], newQueue[index]];
      // Update store with new order
      newQueue.forEach((q) => updateQuestion(q.id, { ...q }));
    }
  };

  const handleRemove = (id: string) => {
    // In a real implementation, you'd have a removeQuestion action in the store
    console.log('Remove question:', id);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'asked':
        return <CheckCircle className="w-4 h-4 text-success-600" />;
      case 'answered':
        return <CheckCircle className="w-4 h-4 text-primary-600" />;
      default:
        return <Circle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'asked':
        return 'text-success-600';
      case 'answered':
        return 'text-primary-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <List className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Question Queue</h3>
        </div>
        <span className="badge badge-info">{questionQueue.length} Questions</span>
      </div>

      <div className="space-y-2 max-h-80 overflow-y-auto">
        {questionQueue.length === 0 ? (
          <p className="text-center text-gray-500 py-8">No questions in queue</p>
        ) : (
          questionQueue.map((question, index) => (
            <div
              key={question.id}
              className={`p-3 rounded-lg border ${
                question.status === 'pending'
                  ? 'bg-white border-gray-200 hover:border-gray-300'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="flex flex-col items-center gap-1 mt-1">
                  <button
                    onClick={() => handleMoveUp(index)}
                    disabled={index === 0}
                    className="p-1 hover:bg-gray-100 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                  >
                    <ArrowUp className="w-4 h-4 text-gray-500" />
                  </button>
                  <span className="text-xs font-medium text-gray-500">{index + 1}</span>
                  <button
                    onClick={() => handleMoveDown(index)}
                    disabled={index === questionQueue.length - 1}
                    className="p-1 hover:bg-gray-100 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                  >
                    <ArrowDown className="w-4 h-4 text-gray-500" />
                  </button>
                </div>

                <div className="flex-1">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(question.status)}
                      <span className={`text-xs font-medium ${getStatusColor(question.status)}`}>
                        {question.status}
                      </span>
                    </div>
                    <button
                      onClick={() => handleRemove(question.id)}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      <Trash2 className="w-4 h-4 text-gray-400 hover:text-danger-600" />
                    </button>
                  </div>

                  <p className="text-sm text-gray-900 mt-2">{question.text}</p>

                  <div className="flex items-center gap-2 mt-2">
                    <Clock className="w-3 h-3 text-gray-400" />
                    <span className="text-xs text-gray-500">
                      {question.timestamp.toLocaleTimeString()}
                    </span>
                    {question.suggestedBy && (
                      <>
                        <span className="text-gray-300">•</span>
                        <span className="text-xs text-gray-500">
                          Suggested by: {question.suggestedBy}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
