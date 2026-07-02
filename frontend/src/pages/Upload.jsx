import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function Upload() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post("/upload", formData);
      navigate("/requirements");
    } catch (err) {
      console.error(err);
      alert("Upload failed. Make sure FastAPI is running!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card">
      <h2>Step 1: Upload Documentation</h2>
      <p className="subtitle" style={{marginBottom: '2rem'}}>Upload your PDF, DOCX, TXT, or MD file to begin generating your app.</p>
      
      <label className="upload-area" style={{display: 'block'}}>
        <input type="file" onChange={handleUpload} disabled={loading} accept=".pdf,.docx,.txt,.md" />
        {loading ? (
          <div>
            <div className="loader"></div>
            <h3 style={{marginTop: '1rem'}}>Parsing document & creating embeddings...</h3>
          </div>
        ) : (
          <div>
            <h3>Drag & Drop or Click to Upload</h3>
            <p>Supports .pdf, .docx, .txt, .md</p>
          </div>
        )}
      </label>
    </div>
  );
}
