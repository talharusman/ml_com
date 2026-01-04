export default function HomePage({ onNavigate }) {
  return (
    <div className="relative h-screen w-full overflow-hidden flex items-end justify-between bg-black">
      {/* Background Image */}
      <img 
        src="/images/homepage.jpg"
        alt="F1 Background"
        className="absolute inset-0 w-full h-full object-cover object-center z-0"
      />
      
      {/* Buttons Container */}
      <div className="absolute bottom-10 left-0 right-0 flex justify-between px-10 z-10">
        <button
          onClick={() => onNavigate('challenges')}
          className="px-12 py-5 text-lg font-bold text-white bg-gradient-to-r from-primary to-red-500 rounded-full shadow-lg hover:scale-110 hover:shadow-primary/60 transition-all tracking-wide"
        >
          Start Competition
        </button>
        <button
          onClick={() => onNavigate('leaderboard')}
          className="px-12 py-5 text-lg font-bold text-white bg-white/15 border-2 border-white rounded-full shadow-lg backdrop-blur hover:bg-white/25 hover:scale-110 transition-all tracking-wide"
        >
          Leaderboard
        </button>
      </div>
    </div>
  );
}
