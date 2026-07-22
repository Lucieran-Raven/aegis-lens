import { useState } from 'react';

interface Candidate {
  id: string;
  name: string;
  role: string;
  status: string;
  score: number;
}

export function App() {
  const [candidates, setCandidates] = useState<Candidate[]>([
    { id: '1', name: 'John Doe', role: 'Developer', status: 'Pending', score: 85 },
    { id: '2', name: 'Jane Smith', role: 'Designer', status: 'Interviewing', score: 92 },
  ]);

  return (
    <div className="dashboard">
      <h1>Aegis Lens - HR Dashboard</h1>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Role</th>
            <th>Status</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {candidates.map((candidate) => (
            <tr key={candidate.id}>
              <td>{candidate.name}</td>
              <td>{candidate.role}</td>
              <td>{candidate.status}</td>
              <td>{candidate.score}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
