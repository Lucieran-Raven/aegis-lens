import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Join } from './routes/Join';
import { Session } from './routes/Session';

export function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Join />} />
        <Route path="/session/:sessionId" element={<Session />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
