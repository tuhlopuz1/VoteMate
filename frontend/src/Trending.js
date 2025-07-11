import React, { useEffect, useState } from 'react';
import './styles/search.css';
import Sidebar from './components/Sidebar.js';
import apiRequest from './components/Requests.js';

const TrendingPage = () => {
  const [trendingPolls, setTrendingPolls] = useState([]);
  const [popularUsers, setPopularUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // Trending polls
        const pollsRes = await apiRequest({
          url: 'https://api.vote.vickz.ru/api/v2/trend-poll',
          method: 'GET',
          auth: true,
        });

        if (!pollsRes.ok) throw new Error('Failed to fetch trending polls');
        const pollsData = await pollsRes.json();
        setTrendingPolls(pollsData);

        // Popular users
        const usersRes = await apiRequest({
          url: 'https://api.vote.vickz.ru/api/v2/trend-user',
          method: 'GET',
          auth: true,
        });

        if (!usersRes.ok) throw new Error('Failed to fetch popular users');
        const usersData = await usersRes.json();
        setPopularUsers(usersData);
      } catch (error) {
        console.error('Error fetching data:', error);
        setTrendingPolls([]);
        setPopularUsers([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleUserClick = (username) => {
    window.location.href = `/#/user/${username}`;
  };

//   const avatarUrl = `https://blockchain-pfps.s3.regru.cloud/${poll.user_username}/avatar_${poll.user_id}.png`

  return (
    <div className="search-page">
      <Sidebar />
      <div className="search-container">
        <h2 style={{ marginBottom: '16px' }}>🔥 Trending Polls</h2>

        {isLoading && <div className="loader"></div>}

        {!isLoading && trendingPolls.length > 0 && (
          <div className="videos-grid">
            {trendingPolls.map((poll, index) => {
              const handleCardClick = () => {
                const username = localStorage.getItem("username");
                const url =
                  poll.user_username === username
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
                    <span className={`vote-status ${!poll.is_active ? 'closed' : 'open'}`}>
                      {!poll.is_active ? 'Closed' : 'Open'}
                    </span>
                  </div>
                  <div className="vote-body">
                    <h3>{poll.name}</h3>
                    <p>{poll.description || 'No description'}</p>
                    <p className="poll-dates">
                      <span>Start: {new Date(poll.start_date).toLocaleDateString()}</span><br />
                      <span>End: {new Date(poll.end_date).toLocaleDateString()}</span>
                    </p>
                    <p style={{ fontSize: '13px', color: '#6b7280' }}>
                      Votes: {poll.votes_count} • Comments: {poll.comments_count}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {!isLoading && trendingPolls.length === 0 && (
          <div className="no-results">No trending polls right now</div>
        )}

        <h2 style={{ marginTop: '40px', marginBottom: '16px' }}>👑 Popular Users</h2>

        {!isLoading && popularUsers.length > 0 && (
          <div className="users-grid">
            {popularUsers.map((user, index) => (
              <div
                key={index}
                className="user-card"
                onClick={() => handleUserClick(user.username)}
                style={{ cursor: 'pointer' }}
              >
                <img
                  className="user-avatar"
                  src={`https://blockchain-pfps.s3.regru.cloud/${user.username}/avatar_${user.id}.png?nocache=${Date.now()}`}
                  alt="Avatar"
                />
                <div className="user-info">
                  <strong>{user.username}</strong>
                  <p>{user.name || 'No name'}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {!isLoading && popularUsers.length === 0 && (
          <div className="no-results">No popular users found</div>
        )}
      </div>
    </div>
  );
};

export default TrendingPage;
