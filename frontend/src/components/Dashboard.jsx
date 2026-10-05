import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export const Dashboard = () => {
  const { user, logout } = useAuth();
  const [agents, setAgents] = useState([]);
  const [claims, setClaims] = useState([]);
  const [evidence, setEvidence] = useState([]);
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  React.useEffect(() => {
    if (!user) return;

    const fetchData = async () => {
      try {
        const headers = { Authorization: `Bearer ${localStorage.getItem('access_token')}` };
        const [agentRes, claimRes, evidenceRes] = await Promise.all([
          fetch('/api/v1/agents', { headers }),
          fetch('/api/v1/claims', { headers }),
          fetch('/api/v1/evidence', { headers }),
        ]);

        setAgents(await agentRes.json());
        setClaims(await claimRes.json());
        setEvidence(await evidenceRes.json());
      } catch (err) {
        console.error('Failed to load data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  const fetchClaimTimeline = async (claimId) => {
    try {
      const headers = { Authorization: `Bearer ${localStorage.getItem('access_token')}` };
      const res = await fetch(`/api/v1/claims/${claimId}/timeline`, { headers });
      const data = await res.json();
      setTimeline(data);
      setSelectedClaim(claimId);
    } catch (err) {
      console.error('Failed to load timeline:', err);
    }
  };

  const canManage = ['admin', 'operator'].includes(user?.role);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div>
            <h1>LEGARE123 Control Center</h1>
            <p>Proof Before Claim</p>
          </div>
          <div className="user-menu">
            <span>{user?.username}</span>
            <span className="badge">{user?.role}</span>
            <button onClick={logout} className="btn-logout">Logout</button>
          </div>
        </div>
      </header>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'agents' ? 'active' : ''}`}
          onClick={() => setActiveTab('agents')}
        >
          Agents
        </button>
        <button
          className={`tab ${activeTab === 'claims' ? 'active' : ''}`}
          onClick={() => setActiveTab('claims')}
        >
          Claims
        </button>
        <button
          className={`tab ${activeTab === 'evidence' ? 'active' : ''}`}
          onClick={() => setActiveTab('evidence')}
        >
          Evidence
        </button>
        {canManage && (
          <button
            className={`tab ${activeTab === 'permissions' ? 'active' : ''}`}
            onClick={() => setActiveTab('permissions')}
          >
            Permissions
          </button>
        )}
      </div>

      <main className="dashboard-content">
        {loading ? (
          <div className="loading">Loading...</div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <section className="panel">
                <h2>System Overview</h2>
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-value">{agents.length}</div>
                    <div className="stat-label">Active Agents</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{claims.length}</div>
                    <div className="stat-label">Claims</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{evidence.length}</div>
                    <div className="stat-label">Evidence Items</div>
                  </div>
                </div>
              </section>
            )}

            {activeTab === 'agents' && (
              <section className="panel">
                <h2>Agents</h2>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Role</th>
                      <th>Status</th>
                      <th>Capabilities</th>
                    </tr>
                  </thead>
                  <tbody>
                    {agents.map((agent) => (
                      <tr key={agent.agent_id}>
                        <td>{agent.agent_id}</td>
                        <td>{agent.name}</td>
                        <td>{agent.role}</td>
                        <td><span className={`status-badge status-${agent.status}`}>{agent.status}</span></td>
                        <td>{(agent.capabilities || []).join(', ')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </section>
            )}

            {activeTab === 'claims' && (
              <section className="panel">
                <h2>Claims</h2>
                <div className="claims-container">
                  <div className="claims-list">
                    {claims.map((claim) => (
                      <div
                        key={claim.claim_id}
                        className={`claim-card ${selectedClaim === claim.claim_id ? 'selected' : ''}`}
                        onClick={() => fetchClaimTimeline(claim.claim_id)}
                      >
                        <div className="claim-header">
                          <strong>{claim.claim_id}</strong>
                          <span className={`status-badge status-${claim.status}`}>{claim.status}</span>
                        </div>
                        <p className="claim-statement">{claim.statement}</p>
                        <div className="claim-meta">
                          <span>Approved: {claim.approved ? 'Yes' : 'No'}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                  {selectedClaim && timeline.length > 0 && (
                    <div className="timeline-panel">
                      <h3>Claim Timeline</h3>
                      <div className="timeline">
                        {timeline.map((event, idx) => (
                          <div key={idx} className="timeline-event">
                            <div className="event-time">{new Date(event.created_at).toLocaleString()}</div>
                            <div className="event-action">{event.action}</div>
                            <div className="event-actor">by {event.actor}</div>
                            {event.details && <div className="event-details">{event.details}</div>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </section>
            )}

            {activeTab === 'evidence' && (
              <section className="panel">
                <h2>Evidence</h2>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Source</th>
                      <th>Status</th>
                      <th>Verified By</th>
                      <th>Tags</th>
                    </tr>
                  </thead>
                  <tbody>
                    {evidence.map((item) => (
                      <tr key={item.evidence_id}>
                        <td>{item.evidence_id}</td>
                        <td>{item.source}</td>
                        <td><span className={`status-badge status-${item.status}`}>{item.status}</span></td>
                        <td>{item.verified_by || 'N/A'}</td>
                        <td>{(item.tags || []).join(', ')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </section>
            )}

            {activeTab === 'permissions' && canManage && (
              <section className="panel">
                <h2>User Permissions & Roles</h2>
                <p>Role-based access control management:</p>
                <ul>
                  <li><strong>admin</strong> - Full system access, user management, policy configuration</li>
                  <li><strong>operator</strong> - Register agents, verify evidence, evaluate claims</li>
                  <li><strong>viewer</strong> - Read-only access to agents, claims, and evidence</li>
                </ul>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
};
