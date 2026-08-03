import { useRef, useState } from 'react';
import { Video, VideoOff, Maximize2, Minimize2, X } from 'lucide-react';
import { VideoFeed } from './VideoFeed';

interface SelfViewProps {
  stream: MediaStream | null;
  className?: string;
}

export function SelfView({ stream, className = '' }: SelfViewProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (isExpanded) return;
    setIsDragging(true);
    setDragStart({
      x: e.clientX - position.x,
      y: e.clientY - position.y,
    });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPosition({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
    if (!isExpanded) {
      setPosition({ x: 0, y: 0 });
    }
  };

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  if (isExpanded) {
    return (
      <div className={`fixed inset-0 bg-black/90 z-50 flex items-center justify-center ${className}`}>
        <div className="relative w-full h-full max-w-4xl max-h-4xl">
          <VideoFeed stream={stream} muted className="w-full h-full rounded-lg" />
          
          <div className="absolute top-4 right-4 flex gap-2">
            <button
              onClick={toggleExpand}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded-full text-white transition-colors"
            >
              <Minimize2 className="w-5 h-5" />
            </button>
            <button
              onClick={toggleMinimize}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded-full text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (isMinimized) {
    return (
      <button
        onClick={toggleMinimize}
        className="fixed bottom-4 right-4 p-3 bg-primary-600 hover:bg-primary-700 rounded-full text-white shadow-lg z-40 transition-all hover:scale-110"
      >
        <Video className="w-6 h-6" />
      </button>
    );
  }

  return (
    <div
      ref={containerRef}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      className={`fixed bottom-4 right-4 w-48 h-36 bg-gray-800 rounded-lg overflow-hidden border-2 border-gray-600 shadow-lg z-40 cursor-move transition-all hover:border-primary-500 ${
        isDragging ? 'opacity-80' : ''
      } ${className}`}
      style={{
        transform: `translate(${position.x}px, ${position.y}px)`,
      }}
    >
      <VideoFeed stream={stream} muted className="w-full h-full" />
      
      <div className="absolute top-2 right-2 flex gap-1">
        <button
          onClick={(e) => {
            e.stopPropagation();
            toggleExpand();
          }}
          className="p-1 bg-gray-800/80 hover:bg-gray-700 rounded text-white transition-colors"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            toggleMinimize();
          }}
          className="p-1 bg-gray-800/80 hover:bg-gray-700 rounded text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="absolute bottom-2 left-2">
        <div className="flex items-center gap-1 bg-gray-800/80 px-2 py-1 rounded">
          {stream ? (
            <Video className="w-3 h-3 text-success-400" />
          ) : (
            <VideoOff className="w-3 h-3 text-error-400" />
          )}
          <span className="text-xs text-white">You</span>
        </div>
      </div>
    </div>
  );
}
