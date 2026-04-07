import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { capsuleAPI } from '../services/api';
import CapsuleCard from '../components/CapsuleCard';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [capsules, setCapsules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchCapsules();
  }, []);

  const fetchCapsules = async () => {
    try {
      const response = await capsuleAPI.getAll();
      setCapsules(response.data);
    } catch (error) {
      toast.error('Failed to load capsules');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this capsule? This action cannot be undone.')) {
      try {
        await capsuleAPI.delete(id);
        setCapsules(capsules.filter(c => c._id !== id));
        toast.success('Capsule deleted successfully');
      } catch (error) {
        toast.error(error.response?.data?.message || 'Failed to delete capsule');
      }
    }
  };

  const handleDeleteAll = async () => {
    if (filteredCapsules.length === 0) {
      toast.error('No capsules to delete');
      return;
    }

    const confirmMessage = `Are you sure you want to delete ${filteredCapsules.length} capsule(s)? This action cannot be undone.`;
    if (window.confirm(confirmMessage)) {
      try {
        const deletePromises = filteredCapsules.map(capsule => capsuleAPI.delete(capsule._id));
        await Promise.all(deletePromises);
        
        const deletedIds = filteredCapsules.map(c => c._id);
        setCapsules(capsules.filter(c => !deletedIds.includes(c._id)));
        
        toast.success(`${filteredCapsules.length} capsule(s) deleted successfully`);
      } catch (error) {
        toast.error('Failed to delete some capsules');
      }
    }
  };

  const filteredCapsules = capsules.filter(capsule => {
    if (filter === 'locked') return !capsule.isUnlocked;
    if (filter === 'unlocked') return capsule.isUnlocked;
    return true;
  });

  const stats = {
    total: capsules.length,
    locked: capsules.filter(c => !c.isUnlocked).length,
    unlocked: capsules.filter(c => c.isUnlocked).length
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">My Time Capsules</h1>
            <div className="flex space-x-3">
              <Link to="/create" className="btn-primary inline-block">
                + Create New Capsule
              </Link>
              {filteredCapsules.length > 0 && (
                <button
                  onClick={handleDeleteAll}
                  className="bg-red-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-600 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  🗑️ Delete All ({filteredCapsules.length})
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">Total Capsules</p>
                <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <div className="text-4xl">📦</div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">Locked</p>
                <p className="text-3xl font-bold text-purple-600">{stats.locked}</p>
              </div>
              <div className="text-4xl">🔐</div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">Unlocked</p>
                <p className="text-3xl font-bold text-green-600">{stats.unlocked}</p>
              </div>
              <div className="text-4xl">✅</div>
            </div>
          </div>
        </div>

        {/* Filter */}
        <div className="mb-6 flex space-x-4">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              filter === 'all'
                ? 'bg-purple-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            All ({stats.total})
          </button>
          <button
            onClick={() => setFilter('locked')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              filter === 'locked'
                ? 'bg-purple-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Locked ({stats.locked})
          </button>
          <button
            onClick={() => setFilter('unlocked')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              filter === 'unlocked'
                ? 'bg-purple-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Unlocked ({stats.unlocked})
          </button>
        </div>

        {/* Capsules Grid */}
        {filteredCapsules.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-2xl font-bold text-gray-700 mb-2">No capsules found</h3>
            <p className="text-gray-600 mb-6">Create your first time capsule to get started!</p>
            <Link to="/create" className="btn-primary inline-block">
              Create Capsule
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCapsules.map(capsule => (
              <CapsuleCard
                key={capsule._id}
                capsule={capsule}
                onDelete={handleDelete}
                onUnlocked={fetchCapsules}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
