import React, { useState } from 'react';
import './styles/search.css';
import Sidebar from './components/Sidebar.js';
import apiRequest from './components/Requests.js';
import Filters from './components/Filters.js';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [activeTab, setActiveTab] = useState('videos');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [filters, setFilters] = useState({
    tags: [],
    voted: 'all', // 'voted', 'not_voted', 'all'
    sortBy: 'popularity_desc',
    status: 'all', // 'open', 'closed', 'all'
  });

  const buildRequestBody = () => {
    const body = {};

    if (query.trim()) body.poll_name = query.trim();

    if (filters.tags.length > 0) body.tags = filters.tags;

    if (filters.status !== 'all') body.poll_status = filters.status;

    if (filters.voted !== 'all') body.voting_status = filters.voted;

    if (filters.sortBy) body.sort_by = filters.sortBy;

    return body;
  };

  const handleSearch = async () => {
    if (!query.trim() && filters.tags.length === 0 && filters.status === 'all' && filters.voted === 'all') {
      setResults([]);
      setHasSearched(true);
      return;
    }

    setIsLoading(true);
    setHasSearched(true);

    try {
      let response;

      if (activeTab === 'videos') {
        const body = buildRequestBody();

        response = await apiRequest({
          url: `https://api.vote.vickz.ru/api/v2/search-polls`,
          method: 'POST',
          auth: true,
          body,
        });

      } else {
        // Поиск по пользователю (GET)
        response = await apiRequest({
          url: `https://api.vote.vickz.ru/api/v2/find-user-by-username`,
          method: 'GET',
          params: { username: query },
          auth: true,
        });
      }

      if (!response.ok) throw new Error('Request failed');

      const data = await response.json();
      setResults(Array.isArray(data) ? data : [data]);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTabSwitch = (tab) => {
    if (tab === activeTab) return;
    setActiveTab(tab);
    setResults([]);
    setHasSearched(false);
  };

  return (
    <div className="search-page">
      <Sidebar />
      <div className="search-container">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Enter query..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch}>Search</button>
        </div>

        <div className="tabs">
          <button
            className={activeTab === 'videos' ? 'active' : ''}
            onClick={() => handleTabSwitch('videos')}
          >
            Polls
          </button>
          <button
            className={activeTab === 'users' ? 'active' : ''}
            onClick={() => handleTabSwitch('users')}
          >
            People
          </button>
        </div>

        {isLoading && <div className="loader"></div>}

        {!isLoading && results.length > 0 && (
          <>
            {activeTab === 'videos' && (
              <div className="videos-grid">
                {results.map((poll, index) => {
                  const handleCardClick = () => {
                    const username = localStorage.getItem("username");
                    const url = poll.user_username === username
                      ? `/#/poll-view-creator/${poll.id}`
                      : `/#/poll/${poll.id}`;
                    window.location.href = url;
                  };

                  return (
                    <div
                      key={index}
                      className="vote-card"
                      style={{ cursor: 'pointer' }}
                      onClick={handleCardClick}
                    >
                      <div className="vote-header">
                        <img
                          className="vote-avatar"
                          src={`https://blockchain-pfps.s3.regru.cloud/${poll.user_username}/avatar_${poll.user_id}.png?nocache=${Date.now()}`}
                          alt="Avatar"
                        />
                        <span className={`vote-status ${poll.closed ? 'closed' : 'open'}`}>
                          {poll.closed ? 'Closed' : 'Open'}
                        </span>
                      </div>
                      <div className="vote-body">
                        <h3>{poll.name}</h3>
                        <p>{poll.description || 'No description'}</p>
                        <p className="poll-dates">
                          <span>Start: {new Date(poll.start_date).toLocaleDateString()}</span><br />
                          <span>End: {new Date(poll.end_date).toLocaleDateString()}</span>
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {activeTab === 'users' && (
              <div className="users-list">
                {results.map((user, index) => (
                  <div key={index} className="user-card" onClick={() => {window.location.href = '/#/user/' + user.username}}>
                    <img
                      src={`https://blockchain-pfps.s3.regru.cloud/${user.username}/avatar_${user.id}.png?nocache=${Date.now()}`}
                      alt={user.username}
                    />
                    <span>{user.username}</span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {!isLoading && results.length === 0 && hasSearched && (
          <div className="no-results">No results found</div>
        )}
      </div>

      {/* Передаём handleSearch как onApply */}
{/* Показывать фильтры только на вкладке "Polls" */}
{activeTab === 'videos' && (
  <Filters
    filters={filters}
    setFilters={setFilters}
    onApply={(newFilters) => {
      setFilters(newFilters);
      handleSearch();
    }}
  />
)}

    </div>
  );
};

export default SearchPage;
