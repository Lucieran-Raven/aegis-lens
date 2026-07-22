import { useState } from 'react';

interface CandidateProfile {
  id: string;
  name: string;
  email: string;
  skills: string[];
}

export function App() {
  const [profile, setProfile] = useState<CandidateProfile | null>(null);

  const loadProfile = () => {
    setProfile({
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      skills: ['JavaScript', 'React', 'TypeScript'],
    });
  };

  return (
    <div className="app">
      <h1>Aegis Lens - Candidate Portal</h1>
      {profile ? (
        <div className="profile">
          <h2>{profile.name}</h2>
          <p>{profile.email}</p>
          <ul>
            {profile.skills.map((skill) => (
              <li key={skill}>{skill}</li>
            ))}
          </ul>
        </div>
      ) : (
        <button onClick={loadProfile}>Load Profile</button>
      )}
    </div>
  );
}
