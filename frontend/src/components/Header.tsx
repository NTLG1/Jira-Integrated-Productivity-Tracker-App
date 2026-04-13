import React from 'react';

interface HeaderProps {
  currentUser: any;
  onLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({ currentUser, onLogout }) => {
  return (
    <header className="header">
      <div className="container">
        <h1>Productivity Tracker</h1>
        <div className="header-controls">
          <div className="header-user-info">
            {currentUser && (
              <span className="user-greeting">
                Welcome, {currentUser.username}!
              </span>
            )}
            {currentUser && (
              <button onClick={onLogout} className="logout-button">
                Logout
              </button>
            )}
          </div>
        </div>
        <nav className="nav">
          <a href="#tasks">Tasks</a>
          <a href="#analytics">Analytics</a>
          <a href="#achievements">Achievements</a>
        </nav>
      </div>
    </header>
  );
};

export default Header;
