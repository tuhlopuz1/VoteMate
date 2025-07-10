import { useState } from 'react';
import { FiX, FiFilter } from 'react-icons/fi';
import '../styles/filters.css';

const Filters = ({ onApply }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState([]);
  const [votedFilter, setVotedFilter] = useState('all');
  const [sortBy, setSortBy] = useState('popularity_desc');
  const [statusFilter, setStatusFilter] = useState('all'); // 🆕 Open/Closed filter

  const toggleFilters = () => setIsOpen(!isOpen);

  const addTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const removeTag = (tag) => {
    setTags(tags.filter((t) => t !== tag));
  };

  const applyFilters = () => {
    onApply({
      startDate,
      endDate,
      tags,
      voted: votedFilter,
      sortBy,
      status: statusFilter, // 🆕 Include status in payload
    });
    setIsOpen(false);
  };

  return (
    <>
      <div className="mobile-menu-button">
        <button onClick={toggleFilters} className="filters-toggle">
          {!isOpen && <FiFilter size={25} />}
        </button>
      </div>

      {isOpen && <div className="filters-backdrop" onClick={toggleFilters} />}

      <aside className={`filters ${isOpen ? 'open' : ''}`}>
        <div className="filters-content">
          <div className="filters-header">
            <button onClick={toggleFilters} className="close-button">
              <FiX size={25} />
            </button>
            <h2>Filters</h2>
          </div>

          

          {/* Tags */}
          <label>Tags:</label>
          <div className="tags-input">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addTag()}
              placeholder="Add tag"
            />
            <button type="button" onClick={addTag}>+</button>
          </div>
          <div className="tags-list">
            {tags.map((tag, index) => (
              <span key={index} className="tag">
                {tag}
                <button onClick={() => removeTag(tag)}>×</button>
              </span>
            ))}
          </div>

          {/* Voted Filter */}
          <label>Voting Status:</label>
          <select value={votedFilter} onChange={(e) => setVotedFilter(e.target.value)}>
            <option value="all">All</option>
            <option value="voted">Where I voted</option>
            <option value="not_voted">Where I didn't vote</option>
          </select>

          {/* Status Filter (Open/Closed) */}
          <label>Poll Status:</label>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="all">All</option>
            <option value="open">Open</option>
            <option value="closed">Closed</option>
          </select>

          {/* Sort Options */}
          <label>Sort by:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="popularity_desc">Popularity ↓</option>
            <option value="popularity_asc">Popularity ↑</option>
          </select>

          {/* Apply Button */}
          <button className="apply-button" onClick={applyFilters}>
            Apply
          </button>
        </div>
      </aside>
    </>
  );
};

export default Filters;
