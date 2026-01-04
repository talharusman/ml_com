import { useState } from 'react';

export default function Navbar({ currentPage, onNavigate, user, onLogout }) {
  return (
    <nav className="bg-gradient-to-r from-secondary to-bg-dark text-white py-4 sticky top-0 z-50 shadow-md">
      <div className="max-w-6xl mx-auto px-5 flex justify-between items-center">
        <div className="text-xl font-bold tracking-wide">🏁 F1-Score</div>
        <div className="flex items-center gap-4">
          {currentPage !== 'home' && (
            <button 
              onClick={() => onNavigate('home')}
              className="text-white font-semibold hover:text-primary transition-colors"
            >
              ← Back to Home
            </button>
          )}
          {user ? (
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-300">Welcome, {user.username}</span>
              <button
                onClick={onLogout}
                className="text-sm px-3 py-1 border border-white rounded hover:bg-white hover:text-primary transition-colors"
              >
                Logout
              </button>
            </div>
          ) : (
            <button
              onClick={() => onNavigate('auth')}
              className="text-sm px-3 py-1 border border-white rounded hover:bg-white hover:text-primary transition-colors"
            >
              Login
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
