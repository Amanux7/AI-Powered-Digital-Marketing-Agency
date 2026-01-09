import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, PlusCircle, History, Settings as SettingsIcon, BrainCircuit } from 'lucide-react';
import ProjectList from './pages/ProjectList';
import CreateProject from './pages/CreateProject';
import RunDetail from './pages/RunDetail';

const Sidebar = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Overview', icon: <LayoutDashboard size={20} /> },
    { path: '/create', label: 'New Project', icon: <PlusCircle size={20} /> },
    { path: '/runs', label: 'Recent Runs', icon: <History size={20} /> },
    { path: '/settings', label: 'Settings', icon: <SettingsIcon size={20} /> },
  ];

  return (
    <div className="sidebar">
      <div className="logo">
        <BrainCircuit size={32} color="#6366f1" />
        <span>AgentCMO</span>
      </div>
      <nav className="nav-links">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          >
            {item.icon}
            {item.label}
          </Link>
        ))}
      </nav>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<ProjectList />} />
            <Route path="/create" element={<CreateProject />} />
            <Route path="/runs/:runId" element={<RunDetail />} />
            <Route path="/settings" element={<div>Settings Component</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
