import { useState, useEffect } from 'react';
import { fetchLeaderboard } from '../api/client';

export default function LeaderboardPage() {
  const [leaderboardData, setLeaderboardData] = useState({ submissions: [], by_task: {} });
  const [filter, setFilter] = useState('all');

  const loadLeaderboard = async () => {
    try {
      const data = await fetchLeaderboard();
      setLeaderboardData(data);
    } catch (err) {
      console.error('Error loading leaderboard:', err);
    }
  };

  useEffect(() => {
    loadLeaderboard();
    // Refresh every 5 seconds
    const interval = setInterval(loadLeaderboard, 5000);
    return () => clearInterval(interval);
  }, []);

  // Calculate submission counts
  const participantSubmissionCount = {};
  const perTaskSubmissionCount = {};
  
  leaderboardData.submissions.forEach(sub => {
    const participantId = sub.submission_id.split('_')[0];
    participantSubmissionCount[participantId] = (participantSubmissionCount[participantId] || 0) + 1;
    
    const key = `${participantId}-${sub.task_id}`;
    perTaskSubmissionCount[key] = (perTaskSubmissionCount[key] || 0) + 1;
  });

  // Filter submissions
  let displaySubmissions = leaderboardData.submissions;
  if (filter !== 'all') {
    displaySubmissions = displaySubmissions.filter(s => s.task_id === filter);
  }
  displaySubmissions = displaySubmissions
    .sort((a, b) => b.score - a.score)
    .slice(0, 100);

  return (
    <div className="min-h-screen bg-bg-light">
      {/* Header */}
      <header className="bg-gradient-to-r from-secondary to-bg-dark text-white py-10 text-center">
        <h1 className="text-4xl font-bold mb-2">Global Leaderboard</h1>
        <p className="opacity-90">Top performers across all questions</p>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <section className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-bold mb-5 pb-3 border-b-4 border-primary">Rankings</h2>

          {/* Filters */}
          <div className="flex flex-wrap gap-3 mb-6">
            {['all', 0, 1, 2, 3].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-5 py-2 font-semibold rounded border-2 transition-colors ${
                  filter === f
                    ? 'bg-primary text-white border-primary'
                    : 'bg-white text-gray-800 border-gray-300 hover:border-primary'
                }`}
              >
                {f === 'all' ? 'All Questions' : `Question ${f + 1}`}
              </button>
            ))}
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead className="bg-secondary text-white">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold">Rank</th>
                  <th className="px-4 py-3 text-left font-semibold">Question</th>
                  <th className="px-4 py-3 text-left font-semibold">Participant ID</th>
                  <th className="px-4 py-3 text-left font-semibold">Score</th>
                  <th className="px-4 py-3 text-left font-semibold">Task Submissions</th>
                  <th className="px-4 py-3 text-left font-semibold">Total Submissions</th>
                  <th className="px-4 py-3 text-left font-semibold">Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {displaySubmissions.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="text-center py-8 text-gray-500">
                      No submissions yet
                    </td>
                  </tr>
                ) : (
                  displaySubmissions.map((sub, idx) => {
                    const participantId = sub.submission_id.split('_')[0];
                    const totalSubmissions = participantSubmissionCount[participantId] || 0;
                    const perTaskCount = perTaskSubmissionCount[`${participantId}-${sub.task_id}`] || 0;
                    
                    return (
                      <tr key={sub.submission_id} className="border-b border-gray-200 hover:bg-gray-50">
                        <td className="px-4 py-3">{idx + 1}</td>
                        <td className="px-4 py-3 font-bold">Q{sub.task_id}</td>
                        <td className="px-4 py-3">{participantId}</td>
                        <td className="px-4 py-3 font-bold">{sub.score?.toFixed(4)}</td>
                        <td className="px-4 py-3">{perTaskCount}</td>
                        <td className="px-4 py-3">{totalSubmissions}</td>
                        <td className="px-4 py-3">{new Date(sub.timestamp).toLocaleString()}</td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}
