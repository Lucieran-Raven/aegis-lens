import { Video, Mic, MicOff, VideoOff, PhoneOff, Monitor, MonitorOff, Settings } from 'lucide-react';

interface ControlsProps {
  isCameraEnabled: boolean;
  isMicrophoneEnabled: boolean;
  isScreenSharing: boolean;
  onToggleCamera: () => void;
  onToggleMicrophone: () => void;
  onToggleScreenShare: () => void;
  onEndCall: () => void;
  onOpenSettings?: () => void;
  className?: string;
}

export function Controls({
  isCameraEnabled,
  isMicrophoneEnabled,
  isScreenSharing,
  onToggleCamera,
  onToggleMicrophone,
  onToggleScreenShare,
  onEndCall,
  onOpenSettings,
  className = '',
}: ControlsProps) {
  return (
    <div className={`flex items-center justify-center gap-4 ${className}`}>
      <button
        onClick={onToggleMicrophone}
        className={`p-4 rounded-full transition-all ${
          isMicrophoneEnabled
            ? 'bg-gray-600 hover:bg-gray-700 text-white'
            : 'bg-error-600 hover:bg-error-700 text-white'
        }`}
        title={isMicrophoneEnabled ? 'Mute microphone' : 'Unmute microphone'}
      >
        {isMicrophoneEnabled ? <Mic className="w-6 h-6" /> : <MicOff className="w-6 h-6" />}
      </button>

      <button
        onClick={onToggleCamera}
        className={`p-4 rounded-full transition-all ${
          isCameraEnabled
            ? 'bg-gray-600 hover:bg-gray-700 text-white'
            : 'bg-error-600 hover:bg-error-700 text-white'
        }`}
        title={isCameraEnabled ? 'Turn off camera' : 'Turn on camera'}
      >
        {isCameraEnabled ? <Video className="w-6 h-6" /> : <VideoOff className="w-6 h-6" />}
      </button>

      <button
        onClick={onToggleScreenShare}
        className={`p-4 rounded-full transition-all ${
          isScreenSharing
            ? 'bg-primary-600 hover:bg-primary-700 text-white'
            : 'bg-gray-600 hover:bg-gray-700 text-white'
        }`}
        title={isScreenSharing ? 'Stop screen sharing' : 'Share screen'}
      >
        {isScreenSharing ? <Monitor className="w-6 h-6" /> : <MonitorOff className="w-6 h-6" />}
      </button>

      <button
        onClick={onEndCall}
        className="p-4 rounded-full bg-error-600 hover:bg-error-700 text-white transition-all"
        title="End call"
      >
        <PhoneOff className="w-6 h-6" />
      </button>

      {onOpenSettings && (
        <button
          onClick={onOpenSettings}
          className="p-4 rounded-full bg-gray-600 hover:bg-gray-700 text-white transition-all"
          title="Settings"
        >
          <Settings className="w-6 h-6" />
        </button>
      )}
    </div>
  );
}
