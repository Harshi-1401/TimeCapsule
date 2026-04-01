import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const CapsuleCard = ({ capsule, onDelete, showOwner = false }) => {
  const [timeLeft, setTimeLeft] = useState('');
  const MEDIA_URL = import.meta.env.VITE_MEDIA_URL || 'http://localhost:8000';

  useEffect(() => {
    if (!capsule.isUnlocked) {
      const timer = setInterval(() => {
        const now = new Date().getTime();
        const unlockTime = new Date(capsule.unlockDate).getTime();
        const distance = unlockTime - now;

        if (distance < 0) {
          setTimeLeft('Unlocking soon...');
          clearInterval(timer);
        } else {
          const days = Math.floor(distance / (1000 * 60 * 60 * 24));
          const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
          const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
          const seconds = Math.floor((distance % (1000 * 60)) / 1000);

          setTimeLeft(`${days}d ${hours}h ${minutes}m ${seconds}s`);
        }
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [capsule.isUnlocked, capsule.unlockDate]);

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`card ${capsule.isUnlocked ? 'border-2 border-green-400' : 'border-2 border-gray-200'}`}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-800 mb-2">{capsule.title}</h3>
          {showOwner && capsule.userId?.name && (
            <p className="text-sm text-gray-500 mb-2">By {capsule.userId.name}</p>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {capsule.isEncrypted && (
            <span className="text-2xl" title="Encrypted">🔒</span>
          )}
          {capsule.isPublic && (
            <span className="text-2xl" title="Public">🌍</span>
          )}
          {capsule.isUnlocked ? (
            <span className="text-2xl" title="Unlocked">✅</span>
          ) : (
            <span className="text-2xl" title="Locked">🔐</span>
          )}
        </div>
      </div>

      {capsule.isUnlocked ? (
        <div className="mb-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-3">
            <p className="text-green-700 font-semibold text-sm">🎉 Unlocked!</p>
          </div>
          {capsule.message && (
            <p className="text-gray-700 mb-3 line-clamp-3">{capsule.message}</p>
          )}
          {capsule.mediaUrl && (
            <div className="mb-3">
              {capsule.mediaType === 'image' && (
                <img 
                  src={`${MEDIA_URL}${capsule.mediaUrl}`} 
                  alt="Capsule media" 
                  className="w-full h-48 object-cover rounded-lg"
                />
              )}
              {capsule.mediaType === 'video' && (
                <video 
                  controls 
                  className="w-full h-48 rounded-lg"
                  src={`${MEDIA_URL}${capsule.mediaUrl}`}
                />
              )}
              {capsule.mediaType === 'audio' && (
                <audio 
                  controls 
                  className="w-full"
                  src={`${MEDIA_URL}${capsule.mediaUrl}`}
                />
              )}
              {capsule.mediaType === 'file' && (
                <a 
                  href={`${MEDIA_URL}${capsule.mediaUrl}`}
                  download
                  className="flex items-center justify-center space-x-2 bg-purple-50 border-2 border-purple-200 rounded-lg p-4 hover:bg-purple-100 transition"
                >
                  <span className="text-3xl">📄</span>
                  <span className="text-purple-700 font-semibold">Download File</span>
                </a>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="mb-4">
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-3">
            <p className="text-purple-700 font-semibold text-sm mb-2">⏳ Time Remaining:</p>
            <p className="text-2xl font-bold text-purple-900">{timeLeft}</p>
          </div>
          <p className="text-gray-600 text-sm">
            Unlocks on: <span className="font-semibold">{formatDate(capsule.unlockDate)}</span>
          </p>
        </div>
      )}

      <div className="flex justify-between items-center pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          Created: {formatDate(capsule.createdAt)}
        </p>
        <div className="flex space-x-2">
          <Link
            to={`/capsules/${capsule._id}`}
            className="text-purple-600 hover:text-purple-800 font-medium text-sm"
          >
            View Details
          </Link>
          {onDelete && (
            <button
              onClick={() => onDelete(capsule._id)}
              className="text-red-600 hover:text-red-800 font-medium text-sm"
            >
              Delete
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CapsuleCard;
