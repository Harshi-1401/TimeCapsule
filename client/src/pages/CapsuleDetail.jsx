import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { capsuleAPI } from '../services/api';
import toast from 'react-hot-toast';

const CapsuleDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [capsule, setCapsule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeLeft, setTimeLeft] = useState('');

  useEffect(() => {
    fetchCapsule();
  }, [id]);

  useEffect(() => {
    if (capsule && !capsule.isUnlocked) {
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
  }, [capsule]);

  const fetchCapsule = async () => {
    try {
      const response = await capsuleAPI.getOne(id);
      setCapsule(response.data);
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load capsule');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this capsule?')) {
      try {
        await capsuleAPI.delete(id);
        toast.success('Capsule deleted successfully');
        navigate('/dashboard');
      } catch (error) {
        toast.error(error.response?.data?.message || 'Failed to delete capsule');
      }
    }
  };

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-purple-600"></div>
      </div>
    );
  }

  if (!capsule) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <Link to="/dashboard" className="text-purple-600 hover:text-purple-800 font-medium mb-6 inline-block">
          ← Back to Dashboard
        </Link>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div className="flex-1">
              <h1 className="text-4xl font-bold text-gray-900 mb-2">{capsule.title}</h1>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span>Created: {formatDate(capsule.createdAt)}</span>
                {capsule.isEncrypted && <span className="flex items-center">🔒 Encrypted</span>}
                {capsule.isPublic && <span className="flex items-center">🌍 Public</span>}
              </div>
            </div>
            <div className="text-5xl">
              {capsule.isUnlocked ? '✅' : '🔐'}
            </div>
          </div>

          {/* Status */}
          {capsule.isUnlocked ? (
            <div className="bg-green-50 border-2 border-green-200 rounded-xl p-6 mb-6">
              <div className="flex items-center space-x-3">
                <span className="text-4xl">🎉</span>
                <div>
                  <h3 className="text-xl font-bold text-green-800">Capsule Unlocked!</h3>
                  <p className="text-green-700">Unlocked on {formatDate(capsule.unlockDate)}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-purple-50 border-2 border-purple-200 rounded-xl p-6 mb-6">
              <div className="text-center">
                <h3 className="text-xl font-bold text-purple-900 mb-2">⏳ Time Until Unlock</h3>
                <p className="text-4xl font-bold text-purple-600 mb-3">{timeLeft}</p>
                <p className="text-purple-700">
                  Unlocks on: <span className="font-semibold">{formatDate(capsule.unlockDate)}</span>
                </p>
              </div>
            </div>
          )}

          {/* Content */}
          {capsule.isUnlocked ? (
            <div className="space-y-6">
              {capsule.message && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Message:</h3>
                  <div className="bg-gray-50 rounded-lg p-6">
                    <p className="text-gray-800 whitespace-pre-wrap">{capsule.message}</p>
                  </div>
                </div>
              )}

              {capsule.mediaUrl && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Media:</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    {capsule.mediaType === 'image' && (
                      <img
                        src={capsule.mediaUrl}
                        alt="Capsule media"
                        className="w-full rounded-lg"
                      />
                    )}
                    {capsule.mediaType === 'video' && (
                      <video
                        controls
                        className="w-full rounded-lg"
                        src={capsule.mediaUrl}
                      />
                    )}
                    {capsule.mediaType === 'audio' && (
                      <audio
                        controls
                        className="w-full"
                        src={capsule.mediaUrl}
                      />
                    )}
                    {capsule.mediaType === 'file' && (
                      <a 
                        href={capsule.mediaUrl}
                        download={capsule.mediaFilename || 'download'}
                        className="flex items-center justify-center space-x-3 bg-purple-50 border-2 border-purple-200 rounded-lg p-6 hover:bg-purple-100 transition"
                      >
                        <span className="text-5xl">📄</span>
                        <div className="text-left">
                          <p className="text-purple-700 font-bold text-lg">Download Attached File</p>
                          <p className="text-purple-600 text-sm">Click to download</p>
                        </div>
                      </a>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🔒</div>
              <h3 className="text-2xl font-bold text-gray-700 mb-2">Content Locked</h3>
              <p className="text-gray-600">
                This capsule's content will be revealed when it unlocks.
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <button
              onClick={handleDelete}
              className="bg-red-500 text-white px-6 py-3 rounded-lg hover:bg-red-600 transition font-semibold"
            >
              🗑️ Delete Capsule
            </button>
            <p className="text-sm text-gray-500 mt-2">
              This action cannot be undone.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CapsuleDetail;
