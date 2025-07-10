import { useState } from 'react';
import { Link } from 'react-router-dom';
import { FiUser, FiTrendingUp, FiSearch, FiSettings, FiMenu, FiX, FiStar, FiPlus, FiHome } from 'react-icons/fi';
import '../styles/sidebar.css';

const Sidebar = () => {
  
  const [isOpen, setIsOpen] = useState(false);
  
  
  const menuItems = [
    { path: '/home', icon: <FiHome size={20} />, label: 'Home' },
    { path: '/trending', icon: <FiTrendingUp size={20} />, label: 'Trending' },
    { path: '/new-poll', icon: <FiPlus size={20} />, label: 'New poll' },
    { path: '/search', icon: <FiSearch size={20} />, label: 'Search' },
    { path: '/settings', icon: <FiSettings size={20} />, label: 'Settings' },
  ];

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const logOut = () => {
    localStorage.clear();
    window.location.href = ""
  }
  

  return (
    <>
      {/* Mobile menu button */}
      <div className="mobile-menu-button">
        <button
          onClick={toggleSidebar}
          className="menu-toggle"
        >
          {isOpen ? null : <FiMenu size={25} />}
        </button>
      </div>

      {/* Sidebar backdrop for mobile */}
      {isOpen && (
        <div 
          className="sidebar-backdrop"
          onClick={toggleSidebar}
        ></div>
      )}

      {/* Sidebar */}
      <aside 
        className={`sidebar ${isOpen ? 'open' : ''}`}
      >
        <div className="sidebar-content">
          
          <div className="sidebar-header">
            <button
              onClick={toggleSidebar}
              className="close-button"
              >
              <FiX size={25} />
            </button>
            


          </div>

              

          <nav className="sidebar-nav">
            <ul>
              {menuItems.map((item) => (
                <li key={item.path}>
                  <Link 
                    to={item.path}
                    className={`menu-item ${window.location.hash === '#'+item.path ? 'active' : ''}`}
                  >
                    <span className="menu-icon">{item.icon}</span>
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
          
          <div className="sidebar-footer">
            <Link 
              href="/"
              className="logout-button"
              onClick={logOut}
            >
              <span className="logout-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </span>
              Log out
            </Link>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;