import React, { useState } from 'react';
import './styles/upload.css';
import Sidebar from './components/Sidebar';
import { FiPlus } from 'react-icons/fi';
import apiRequest from './components/Requests';
import Swal from 'sweetalert2';

const highlightHashtags = (text) => {
  if (!text) return '';
  return text.replace(/(#([\p{L}\p{N}_]+))/gu, '<span class="hashtag">$1</span>')

};


const PollCreator = () => {
  const [step, setStep] = useState(1);
  const [pollData, setPollData] = useState({
    title: '',
    description: '',
    options: ['', ''],
    startDateTime: '',
    endDateTime: '',
    visibility: 'public'
  });

  // Парсим datetime-local строку как локальную дату (без таймзонных сдвигов)
  const parseDateTimeLocal = (str) => {
    if (!str) return null;
    const [datePart, timePart] = str.split('T');
    const [year, month, day] = datePart.split('-').map(Number);
    const [hour, minute] = timePart.split(':').map(Number);
    return new Date(year, month - 1, day, hour, minute);
  };



  // Конвертируем локальное московское время (UTC+3) в UTC для отправки на сервер
  const toUTCFromMoscow = (localDateTimeStr) => {
    if (!localDateTimeStr) return '';
    const [datePart, timePart] = localDateTimeStr.split('T');
    const [year, month, day] = datePart.split('-').map(Number);
    const [hour, minute] = timePart.split(':').map(Number);

    const localDate = new Date(year, month - 1, day, hour, minute);
    const utcTimestamp = localDate.getTime() - 3 * 60 * 60 * 1000; // вычитаем 3 часа
    const utcDate = new Date(utcTimestamp);

    const pad = (num) => num.toString().padStart(2, '0');
    return (
      utcDate.getFullYear() +
      '-' +
      pad(utcDate.getMonth() + 1) +
      '-' +
      pad(utcDate.getDate()) +
      'T' +
      pad(utcDate.getHours()) +
      ':' +
      pad(utcDate.getMinutes())
    );
  };

  const nextStep = () => {
    if (step === 1) {
      const { title, description, startDateTime, endDateTime } = pollData;

      if (!title.trim() || !description.trim() || !startDateTime || !endDateTime) {
        Swal.fire({
          icon: 'warning',
          title: 'Incomplete Fields',
          text: 'Please fill in all fields before continuing.',
          confirmButtonColor: '#3085d6',
          background: '#fff',
          color: '#000',
        });
        return;
      }

      const startDate = parseDateTimeLocal(startDateTime);
      const endDate = parseDateTimeLocal(endDateTime);

      if (!startDate || !endDate || startDate >= endDate) {
        Swal.fire({
          icon: 'error',
          title: 'Invalid Dates',
          text: 'End date and time must be after start date and time.',
          confirmButtonColor: '#3085d6',
          background: '#fff',
          color: '#000',
        });
        return;
      }
    }

    if (step === 2) {
      const validOptions = pollData.options.filter(opt => opt.trim() !== '');
      if (validOptions.length < 2 || pollData.options.some(opt => !opt.trim())) {
        Swal.fire({
          icon: 'warning',
          title: 'Invalid Options',
          text: 'Each option must be filled. Minimum 2 options required.',
          confirmButtonColor: '#3085d6',
          background: '#fff',
          color: '#000',
        });
        return;
      }
    }

    setStep((prev) => Math.min(prev + 1, 3));
  };

  const prevStep = () => setStep((prev) => Math.max(prev - 1, 1));

  const updateField = (field, value) => {
    setPollData((prev) => ({ ...prev, [field]: value }));
  };

  const updateOption = (index, value) => {
    const newOptions = [...pollData.options];
    newOptions[index] = value;
    setPollData((prev) => ({ ...prev, options: newOptions }));
  };

  const addOption = () => {
    if (pollData.options.length >= 10) {
      Swal.fire({
        icon: 'warning',
        title: 'Maximum options reached',
        text: 'You can only add up to 10 answer options.',
        confirmButtonColor: '#3085d6',
        confirmButtonText: 'OK',
        background: '#fff',
        color: '#000',
      });
      return;
    }

    setPollData((prev) => ({
      ...prev,
      options: [...prev.options, ''],
    }));
  };

  const removeOption = (index) => {
    if (pollData.options.length <= 2) return;
    const newOptions = pollData.options.filter((_, i) => i !== index);
    setPollData((prev) => ({ ...prev, options: newOptions }));
  };

  const handleSubmit = async (asDraft = false) => {
    const payload = {
      name: pollData.title,
      description: pollData.description,
      start_date: toUTCFromMoscow(pollData.startDateTime),
      end_date: toUTCFromMoscow(pollData.endDateTime),
      options: pollData.options.filter(opt => opt.trim() !== ''),
      private: pollData.visibility === 'private'
    };

    try {
      const response = await apiRequest({
        url: 'https://api.vote.vickz.ru/api/v2/create-poll',
        method: 'POST',
        body: payload,
        auth: true,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to create poll: ${errorText}`);
      }

      alert(asDraft ? 'Poll saved as draft!' : 'Poll published successfully!');
      window.location.href = `/#/home`
    } catch (error) {
      console.error('Poll submission failed:', error);
      alert('Something went wrong while submitting the poll.');
    }

  };

  return (
    <div className='main-layout'>
      <Sidebar />
      <div className='poll-area'>
        <div className="poll-container">
          <h1 className="poll-title">Create New Poll</h1>

          {step === 1 && (
            <Step1
              title={pollData.title}
              description={pollData.description}
              startDateTime={pollData.startDateTime}
              endDateTime={pollData.endDateTime}
              onChange={updateField}
              visibility={pollData.visibility}
            />
          )}
          {step === 2 && (
            <Step2
              options={pollData.options}
              onChange={updateOption}
              addOption={addOption}
              removeOption={removeOption}
            />
          )}
          {step === 3 && (
            <Step3
              pollData={pollData}
              onSubmit={handleSubmit}
            />
          )}

          <div className="button-group">
            {step > 1 ? (
              <button className="cta-button secondary" onClick={prevStep}>Back</button>
            ) : <div />}
            {step < 3 && (
              <button className="cta-button primary" onClick={nextStep}>Next</button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const Step1 = ({ title, description, startDateTime, endDateTime, visibility, onChange }) => {
  const now = new Date().toISOString().slice(0, 16);

  return (
    <div className="step-content">
      <h2 className="step-title">Step 1: Title and Description</h2>

      <label className="label">Title:</label>
      <input
        type="text"
        value={title}
        onChange={(e) => onChange('title', e.target.value)}
        className="input"
        placeholder="Enter poll title"
      />

      <label className="label">Description:</label>
      <div className="textarea-wrapper">
        <div
          className="textarea-display"
          dangerouslySetInnerHTML={{ __html: highlightHashtags(description) + '\u200b' }}
        />
        <textarea
          value={description}
          onChange={(e) => onChange('description', e.target.value)}
          className="textarea-input"
          placeholder="Enter poll description"
        />
      </div>

      <label className="label">Start Date & Time:</label>
      <input
        type="datetime-local"
        className="input"
        value={startDateTime}
        min={now}
        onChange={(e) => onChange('startDateTime', e.target.value)}
      />

      <label className="label">End Date & Time:</label>
      <input
        type="datetime-local"
        className="input"
        value={endDateTime}
        min={startDateTime || now}
        onChange={(e) => onChange('endDateTime', e.target.value)}
      />

      <label className="label">Visibility:</label>
      <div className="visibility-options">
        <label>
          <input
            type="radio"
            name="visibility"
            value="public"
            checked={visibility === 'public'}
            onChange={(e) => onChange('visibility', e.target.value)}
          />
          Public
        </label>
        <label>
          <input
            type="radio"
            name="visibility"
            value="private"
            checked={visibility === 'private'}
            onChange={(e) => onChange('visibility', e.target.value)}
          />
          Private (access by link)
        </label>
      </div>
    </div>
  );
};


const Step2 = ({ options, onChange, addOption, removeOption }) => (
  <div className="step-content">
    <h2 className="step-title">Step 2: Answer Options</h2>
    {options.map((opt, idx) => (
      <div key={idx} className="option-row">
        <input
          type="text"
          value={opt}
          onChange={(e) => onChange(idx, e.target.value)}
          className="input option-input"
          placeholder={`Option ${idx + 1}`}
        />
        {options.length > 2 && (
          <button className="remove-btn" onClick={() => removeOption(idx)}>✕</button>
        )}
      </div>
    ))}
    <button className="btn add-btn" onClick={addOption}><FiPlus /> Add Option</button>
  </div>
);

const Step3 = ({ pollData, onSubmit }) => (
  <div className="step-content">
    <h2 className="step-title">Step 3: Preview</h2>
    <p><strong>Title:</strong> {pollData.title}</p>
    <p><strong>Description:</strong></p>
    <p className="preview-description" dangerouslySetInnerHTML={{ __html: highlightHashtags(pollData.description) }} />


    <p><strong>Start:</strong> {pollData.startDateTime || '—'}</p>
    <p><strong>End:</strong> {pollData.endDateTime || '—'}</p>

    <p><strong>Options:</strong></p>
    <ul className="option-list">
      {pollData.options.map((opt, idx) => (
        <li key={idx}>{opt}</li>
      ))}
    </ul>

    <div className="submit-group">
      <button className="cta-button primary publish" onClick={() => onSubmit(false)}>Publish</button>
    </div>
  </div>
);

export default PollCreator;
