import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function Requirements() {
  const [requirements, setRequirements] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const generateRequirements = async () => {
    setLoading(true);
    try {
      const res = await api.post("/generate-requirements");
      setRequirements(res.data.requirements);
    } catch (err) {
      console.error(err);
      alert("Generation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card">
      <h2>Step 2: Generate Requirements</h2>
      <p className="subtitle">The AI will extract project requirements from your uploaded document.</p>
      
      {!requirements ? (
        <div style={{ textAlign: 'center', marginTop: '3rem' }}>
          <button className="btn" onClick={generateRequirements} disabled={loading}>
            {loading ? <><div className="loader" /> Extracting...</> : 'Generate Requirements'}
          </button>
        </div>
      ) : (
        <div style={{ marginTop: '2rem', animation: 'fadeUp 0.5s' }}>
          <pre>{requirements}</pre>
          <div style={{ textAlign: 'right', marginTop: '1.5rem' }}>
            <button className="btn" onClick={() => navigate('/architecture')}>
              Next: Architecture ➡️
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
