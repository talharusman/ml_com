import { useState, useEffect } from 'react';
import { getCurrentUser } from './api/client';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import ChallengesPage from './pages/ChallengesPage';
import LeaderboardPage from './pages/LeaderboardPage';
import AuthPage from './pages/AuthPage';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('token');
    if (token) {
      getCurrentUser()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('token');
        });
    }
  }, []);

  const handleNavigate = (page) => {
    setCurrentPage(page);
    window.scrollTo(0, 0);
  };

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage onNavigate={handleNavigate} />;
      case 'challenges':
        return <ChallengesPage onRefreshLeaderboard={() => {}} />;
      case 'leaderboard':
        return <LeaderboardPage />;
      case 'auth':
        return <AuthPage onLogin={handleLogin} onNavigate={handleNavigate} />;
      default:
        return <HomePage onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {currentPage !== 'home' && currentPage !== 'auth' && (
        <Navbar 
          currentPage={currentPage} 
          onNavigate={handleNavigate} 
          user={user}
          onLogout={handleLogout}
        />
      )}
      <main className="flex-1">
        {renderPage()}
      </main>
      {currentPage !== 'home' && <Footer />}
    </div>
  );
}

export default App;
