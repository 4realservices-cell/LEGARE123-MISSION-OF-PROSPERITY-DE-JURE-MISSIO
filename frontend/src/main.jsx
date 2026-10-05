import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles.css';

function formatStatus(value) {
  return value?.toString().replace('_', ' ') || 'n/a';
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error('Request failed');
  return response.json();
}

function App() {
  const [agents, setAgents] = React.useState([]);
  const [claims, setClaims] = React.useState([]);
  const [evidence, setEvidence] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    Promise.all([
      fetchJson('/api/v1/agents'),
      fetchJson('/api/v1/claims'),
      fetchJson('/api/v1/evidence'),
    ])
      .then(([agentData, claimData, evidenceData]) => {
        setAgents(agentData);
        setClaims(claimData);
        setEvidence(evidenceData);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>LEGARE123 Mission of Prosperity</h1>
          <p>Proof Before Claim Control Center</p>
        </div>
      </header>

      <main className="container">
        <section className="stats-grid">
          <div className="stat-card">
            <span>Agents</span>
            <strong>{agents.length}</strong>
          </div>
          <div className="stat-card">
            <span>Claims</span>
            <strong>{claims.length}</strong>
          </div>
          <div className="stat-card">
            <span>Evidence</span>
            <strong>{evidence.length}</strong>
          </div>
        </section>

        <section className="panel">
          <h2>Agents</h2>
          {loading ? <p>Loading...</p> : (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {agents.map((agent) => (
                  <tr key={agent.agent_id}>
                    <td>{agent.agent_id}</td>
                    <td>{agent.name}</td>
                    <td>{agent.role}</td>
                    <td>{formatStatus(agent.status)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        <section className="panel">
          <h2>Claims</h2>
          <table>
            <thead>
              <tr>
                <th>Claim</th>
                <th>Status</th>
                <th>Approved</th>
              </tr>
            </thead>
            <tbody>
              {claims.map((claim) => (
                <tr key={claim.claim_id}>
                  <td>{claim.statement}</td>
                  <td>{claim.status}</td>
                  <td>{claim.approved ? 'Yes' : 'No'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
