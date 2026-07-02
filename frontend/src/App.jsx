import { useState } from 'react'
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import Upload from './pages/Upload'
import Requirements from './pages/Requirements'
import Architecture from './pages/Architecture'
import Project from './pages/Project'

function Stepper() {
  const location = useLocation();
  const paths = ['/', '/requirements', '/architecture', '/project'];
  const currentIndex = paths.indexOf(location.pathname);

  return (
    <div className="stepper">
      {[1, 2, 3, 4].map((step, index) => (
        <div 
          key={step} 
          className={`step ${index === currentIndex ? 'active' : ''} ${index < currentIndex ? 'completed' : ''}`}
        >
          {index < currentIndex ? '✓' : step}
        </div>
      ))}
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <header>
          <h1>Doc2App Lite</h1>
          <p className="subtitle">From Documentation to Codebase</p>
        </header>
        
        <Stepper />

        <Routes>
          <Route path="/" element={<Upload />} />
          <Route path="/requirements" element={<Requirements />} />
          <Route path="/architecture" element={<Architecture />} />
          <Route path="/project" element={<Project />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
