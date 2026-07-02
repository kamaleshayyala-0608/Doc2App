import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function Architecture() {
  const [architecture, setArchitecture] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const generateArchitecture = async () => {
    setLoading(true);
    try {
      const res = await api.post("/generate-architecture");
      setArchitecture(res.data.architecture);
    } catch (err) {
      console.error(err);
      alert("Generation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card">
      <h2>Step 3: Generate Architecture Blueprint</h2>
      <p className="subtitle">The AI will design the folder structure, schemas, and APIs.</p>
      
      {!architecture ? (
        <div style={{ textAlign: 'center', marginTop: '3rem' }}>
          <button className="btn" onClick={generateArchitecture} disabled={loading}>
            {loading ? <><div className="loader" /> Designing...</> : 'Generate Architecture'}
          </button>
        </div>
      ) : (
        <div style={{ marginTop: '2rem', animation: 'fadeUp 0.5s' }}>
          <pre>{architecture}</pre>
          <div style={{ textAlign: 'right', marginTop: '1.5rem' }}>
            <button className="btn" onClick={() => navigate('/project')}>
              Next: Generate App ➡️
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
