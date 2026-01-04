import { useState, useEffect } from 'react';
import { fetchTasks } from '../api/client';
import TaskModal from '../components/TaskModal';
import UploadModal from '../components/UploadModal';

const STEP_COLORS = [
  { bg: 'from-red-900 to-red-950', wheel: '/images/wheel1.png' },
  { bg: 'from-green-900 to-green-950', wheel: '/images/wheel2.png' },
  { bg: 'from-blue-900 to-blue-950', wheel: '/images/wheel3.png' },
  { bg: 'from-gray-700 to-gray-800', wheel: '/images/wheel4.png' },
];

export default function ChallengesPage({ onRefreshLeaderboard }) {
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [uploadTaskId, setUploadTaskId] = useState(null);

  useEffect(() => {
    fetchTasks()
      .then(setTasks)
      .catch(err => console.error('Error loading tasks:', err));
  }, []);

  const openTaskDetail = (taskId) => {
    const task = tasks.find(t => t.id === taskId);
    if (task) {
      setSelectedTask(task);
    }
  };

  const openUploadModal = (taskId) => {
    setSelectedTask(null);
    setUploadTaskId(taskId);
  };

  const handleUploadSuccess = () => {
    if (onRefreshLeaderboard) {
      onRefreshLeaderboard();
    }
  };

  return (
    <div 
      className="min-h-screen bg-cover bg-center"
      style={{ 
        backgroundImage: 'url(/images/background.png)',
        filter: 'brightness(1.2)',
      }}
    >
      <div className="max-w-5xl mx-auto py-8 px-4">
        {/* Steps */}
        {[0, 1, 2, 3].map((index) => {
          const isLeft = index % 2 === 0;
          const task = tasks.find(t => t.id === index);
          const stepLabels = [
            ['Understanding', '& Goal Setting'],
            ['Initial Research', '& Inspiration'],
            ['Brainstorming', '& Ideation'],
            ['Wireframing', '& Prototyping'],
          ];
          
          return (
            <div
              key={index}
              className={`flex items-center w-full h-36 ${isLeft ? '' : 'justify-end'}`}
            >
              {!isLeft && (
                <span className="text-9xl font-black text-white/15 mr-6">
                  0{index + 1}
                </span>
              )}
              
              <button
                onClick={() => openTaskDetail(index)}
                className={`w-1/2 h-24 rounded-lg relative flex items-center ${isLeft ? 'pr-10' : 'pl-10 justify-end'} bg-gradient-to-r ${STEP_COLORS[index].bg} transition-transform hover:scale-105 hover:brightness-125 cursor-pointer group`}
              >
                <p className={`text-white font-semibold text-lg leading-tight ${isLeft ? 'ml-6' : 'mr-6 text-right'}`}>
                  {stepLabels[index][0]}<br/>{stepLabels[index][1]}
                </p>
                <img
                  src={STEP_COLORS[index].wheel}
                  alt="Wheel"
                  className={`w-24 absolute top-1/2 -translate-y-1/2 transition-transform group-hover:rotate-90 ${isLeft ? '-right-12' : '-left-12'}`}
                />
              </button>
              
              {isLeft && (
                <span className="text-9xl font-black text-white/15 ml-6">
                  0{index + 1}
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Task Detail Modal */}
      {selectedTask && (
        <TaskModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
          onSubmit={openUploadModal}
        />
      )}

      {/* Upload Modal */}
      {uploadTaskId !== null && (
        <UploadModal
          taskId={uploadTaskId}
          onClose={() => setUploadTaskId(null)}
          onSuccess={handleUploadSuccess}
        />
      )}
    </div>
  );
}
