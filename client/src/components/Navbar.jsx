import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ProfileDropdown from './ProfileDropdown';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const closeMobileMenu = () => setMobileMenuOpen(false);

  const handleMobileLogout = () => {
    logout();
    navigate('/login');
    setMobileMenuOpen(false);
  };

  return (
    <nav className="bg-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2" onClick={closeMobileMenu}>
            <span className="text-3xl">🕰️</span>
            <span className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
              TimeCapsule
            </span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-6">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="text-gray-700 hover:text-purple-600 font-medium transition">
                  Dashboard
                </Link>
                <Link to="/create" className="text-gray-700 hover:text-purple-600 font-medium transition">
                  Create
                </Link>
                <Link to="/public" className="text-gray-700 hover:text-purple-600 font-medium transition">
                  Public
                </Link>
                {user?.role === 'admin' && (
                  <Link to="/admin" className="text-gray-700 hover:text-purple-600 font-medium transition">
                    Admin
                  </Link>
                )}
                <ProfileDropdown />
              </>
            ) : (
              <>
                <Link to="/public" className="text-gray-700 hover:text-purple-600 font-medium transition">
                  Public
                </Link>
                <Link to="/login" className="text-gray-700 hover:text-purple-600 font-medium transition">
                  Login
                </Link>
                <Link to="/register" className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition">
                  Get Started
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden text-gray-700 hover:text-purple-600 focus:outline-none"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden pb-4 border-t border-gray-200 mt-2">
            {isAuthenticated ? (
              <div className="flex flex-col space-y-3 pt-4">
                <div className="px-4 py-2 text-gray-600 font-medium border-b border-gray-100">
                  Hi, {user?.name}
                </div>
                <Link
                  to="/profile"
                  className="px-4 py-2 text-gray-700 hover:bg-purple-50 hover:text-purple-600 transition rounded"
                  onClick={closeMobileMenu}
                >
                  My Profile
                </Link>
                <Link
                  to="/dashboard"
                  className="px-4 py-2 text-gray-700 hover:bg-purple-50 hover:text-purple-600 transition rounded"
                  onClick={closeMobileMenu}
                >
                  Dashboard
                </Link>
                <Link
                  to="/create"
                  className="px-4 py-2 text-gray-700 hover:bg-purple-50 hover:text-purple-600 transition rounded"
                  onClick={closeMobileMenu}
                >
                  Create Capsule
                </Link>
                <Link
                  to="/public"
                  className="px-4 py-2 text-gray-700 hover:bg-purple-50 hover:text-purple-600 transition rounded"
                  onClick={closeMobileMenu}
                >
                  Public Capsules
                </Link>
                {user?.role === 'admin' && (
                  <Link
                    to="/admin"
                    className="px-4 py-2 text-gray-700 hover:bg-purple-50 hover:text-purple-600 transition rounded"
                    onClick={closeMobileMenu}
                  >
                    Admin Panel
                  </Link>
                )}
                <button
                  onClick={handleMobileLogout}
                  className="mx-4 mt-2 bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex flex-col space-y-3 pt-4">
                <Link
                  to="/public"
                  className="px-4 py-2 text-gray-700 hover:bg-purple-50 hover:text-purple-600 transition rounded"
                  onClick={closeMobileMenu}
                >
                  Public Capsules
                </Link>
                <Link
                  to="/login"
                  className="px-4 py-2 text-gray-700 hover:bg-purple-50 hover:text-purple-600 transition rounded"
                  onClick={closeMobileMenu}
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="mx-4 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition text-center"
                  onClick={closeMobileMenu}
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
