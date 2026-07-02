import { useState } from 'react';
import api from '../services/api';

export default function Project() {
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const generateProject = async () => {
    setLoading(true);
    try {
      await api.post("/build-project", null, { timeout: 600000 }); // 10 minute timeout
      setDone(true);
    } catch (err) {
      console.error(err);
      alert("Code generation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card" style={{ textAlign: 'center' }}>
      <h2>Step 4: Generate Codebase</h2>
      <p className="subtitle">The AI will now write all the backend, frontend, and database code.</p>
      
      <div style={{ marginTop: '4rem', marginBottom: '2rem' }}>
        {!done ? (
          <div>
            <button className="btn" onClick={generateProject} disabled={loading} style={{ padding: '20px 40px', fontSize: '1.3rem' }}>
              {loading ? <><div className="loader" /> Building AI Agents...</> : '🚀 Build My App'}
            </button>
            {loading && <p style={{marginTop: '1rem', color: 'var(--text-secondary)'}}>This advanced file-by-file build process will take several minutes to complete. Check your FastAPI terminal to watch the agents work!</p>}
          </div>
        ) : (
          <div style={{ animation: 'fadeUp 0.5s' }}>
            <h2 style={{ color: 'var(--text-primary)', marginBottom: '2rem', fontSize: '2.5rem' }}>🎉 Application Generated!</h2>
            <a 
              href="http://localhost:8000/download-project" 
              download="generated_project.zip" 
              className="btn" 
              style={{ display: 'inline-block', background: 'linear-gradient(to right, #10b981, #059669)', fontSize: '1.2rem', textDecoration: 'none' }}
            >
              ⬇️ Download Source Code (ZIP)
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
