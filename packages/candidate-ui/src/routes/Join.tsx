import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Video, Mic, Monitor, AlertCircle, CheckCircle } from 'lucide-react';
import { useSessionStore, useMediaStore } from '../store/useSessionStore';

export function Join() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [permissions, setPermissions] = useState({
    camera: false,
    microphone: false,
    screen: false,
  });
  const [isCheckingPermissions, setIsCheckingPermissions] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setSessionIdStore = useSessionStore((state) => state.setSessionId);
  const setCandidateName = useSessionStore((state) => state.setCandidateName);
  const setCameraStream = useMediaStore((state) => state.setCameraStream);
  const setMicrophoneStream = useMediaStore((state) => state.setMicrophoneStream);

  const handleJoin = () => {
    if (name && sessionId && permissions.camera && permissions.microphone) {
      setSessionIdStore(sessionId);
      setCandidateName(name);
      navigate(`/session/${sessionId}`);
    } else {
      setError('Please complete all required fields and grant permissions');
    }
  };

  const requestPermissions = async () => {
    setIsCheckingPermissions(true);
    setError(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });

      setCameraStream(stream);
      setMicrophoneStream(stream);

      setPermissions({
        camera: true,
        microphone: true,
        screen: false,
      });

      // Stop the stream after checking permissions
      stream.getTracks().forEach(track => track.stop());
    } catch (error) {
      console.error('Permission denied:', error);
      setError('Camera and microphone permissions are required');
      setPermissions({
        camera: false,
        microphone: false,
        screen: false,
      });
    } finally {
      setIsCheckingPermissions(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center p-4">
      <div className="card max-w-md w-full animate-fade-in">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Aegis Lens</h1>
          <p className="text-gray-600">Candidate Interview Portal</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-error-50 border border-error-200 rounded-lg flex items-center gap-2 text-error-700">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        <div className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Your Name
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                setError(null);
              }}
              className="input-field"
              placeholder="Enter your full name"
            />
          </div>

          <div>
            <label htmlFor="sessionId" className="block text-sm font-medium text-gray-700 mb-2">
              Session ID
            </label>
            <input
              id="sessionId"
              type="text"
              value={sessionId}
              onChange={(e) => {
                setSessionId(e.target.value);
                setError(null);
              }}
              className="input-field"
              placeholder="Enter session ID"
            />
          </div>

          <div className="space-y-3">
            <button
              onClick={requestPermissions}
              disabled={isCheckingPermissions}
              className="w-full btn-secondary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isCheckingPermissions ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Checking Permissions...
                </>
              ) : (
                <>
                  <Video className="w-4 h-4" />
                  Test Camera & Microphone
                </>
              )}
            </button>

            <div className="flex gap-2">
              <div className={`flex-1 p-3 rounded-lg border-2 transition-colors ${
                permissions.camera ? 'border-success-500 bg-success-50' : 'border-gray-300 bg-gray-50'
              }`}>
                {permissions.camera ? (
                  <CheckCircle className="w-6 h-6 mx-auto text-success-600" />
                ) : (
                  <Video className="w-6 h-6 mx-auto text-gray-400" />
                )}
                <p className="text-xs text-center mt-1">Camera</p>
              </div>
              <div className={`flex-1 p-3 rounded-lg border-2 transition-colors ${
                permissions.microphone ? 'border-success-500 bg-success-50' : 'border-gray-300 bg-gray-50'
              }`}>
                {permissions.microphone ? (
                  <CheckCircle className="w-6 h-6 mx-auto text-success-600" />
                ) : (
                  <Mic className="w-6 h-6 mx-auto text-gray-400" />
                )}
                <p className="text-xs text-center mt-1">Microphone</p>
              </div>
              <div className={`flex-1 p-3 rounded-lg border-2 transition-colors ${
                permissions.screen ? 'border-success-500 bg-success-50' : 'border-gray-300 bg-gray-50'
              }`}>
                {permissions.screen ? (
                  <CheckCircle className="w-6 h-6 mx-auto text-success-600" />
                ) : (
                  <Monitor className="w-6 h-6 mx-auto text-gray-400" />
                )}
                <p className="text-xs text-center mt-1">Screen</p>
              </div>
            </div>
          </div>

          <button
            onClick={handleJoin}
            disabled={!name || !sessionId || !permissions.camera || !permissions.microphone}
            className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Join Session
          </button>
        </div>

        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Please ensure your camera and microphone are working before joining.</p>
        </div>
      </div>
    </div>
  );
}
