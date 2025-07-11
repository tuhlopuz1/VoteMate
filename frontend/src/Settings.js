import React, { useEffect, useState } from 'react';
import './styles/settings.css';
import Sidebar from './components/Sidebar';
import apiRequest from './components/Requests';
import { FiTool } from 'react-icons/fi';
import { Link } from 'react-router-dom';
import Swal from 'sweetalert2';

const SettingsPage = () => {
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [description, setDescription] = useState('');
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarUrl, setAvatarUrl] = useState('');

  const userId = localStorage.getItem('id');

  useEffect(() => {
    setName(localStorage.getItem('name') || '');
    setUsername(localStorage.getItem('username') || '');
    setDescription(localStorage.getItem('description') || '');
    setAvatarUrl(`https://blockchain-pfps.s3.regru.cloud/${localStorage.getItem('username')}/avatar_${localStorage.getItem('id')}.png?nocache=${Date.now()}`);
  }, [userId]);

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    try {
      const response = await apiRequest({
        url: 'https://api.vote.vickz.ru/api/v2/update-profile',
        method: 'PUT',
        auth: true,
        body: {
          name,
          username,
          description,
        },
      });

      if (!response.ok) throw new Error('Failed to update profile');

      const updated = await response.json();

      localStorage.setItem('name', name);
      localStorage.setItem('username', username);
      localStorage.setItem('description', description);

      Swal.fire({
        icon: 'success',
        title: 'Profile Updated',
        text: 'Your profile information has been successfully saved.',
      });
    } catch (err) {
      console.error(err);
      Swal.fire({
        icon: 'error',
        title: 'Update Failed',
        text: 'There was a problem updating your profile.',
      });
    }
  };

  const handleAvatarChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setAvatarFile(file);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('https://api.vote.vickz.ru/api/v2/profile-picture', {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: formData,
      });

      if (!response.ok) throw new Error('Failed to upload avatar');

      setAvatarUrl(`https://blockchain-pfps.s3.regru.cloud/${localStorage.getItem('username')}/avatar_${localStorage.getItem('id')}.png?nocache=${Date.now()}`);

      Swal.fire({
        icon: 'success',
        title: 'Avatar Updated',
        text: 'Your profile picture has been successfully uploaded.',
      });
    } catch (err) {
      console.error(err);
      Swal.fire({
        icon: 'error',
        title: 'Upload Failed',
        text: 'There was a problem uploading your avatar.',
      });
    }
  };

  const handleChangePassword = async () => {
    const { value: formValues } = await Swal.fire({
      title: 'Change Password',
      html:
        '<input id="swal-old-password" type="password" class="swal2-input" placeholder="Old Password">' +
        '<input id="swal-new-password" type="password" class="swal2-input" placeholder="New Password">',
      focusConfirm: false,
      showCancelButton: true,
      confirmButtonText: 'Confirm',
      preConfirm: () => {
        const oldPassword = document.getElementById('swal-old-password').value;
        const newPassword = document.getElementById('swal-new-password').value;

        if (!oldPassword || !newPassword) {
          Swal.showValidationMessage('Both fields are required');
          return;
        }

        return { oldPassword, newPassword };
      },
    });

    if (!formValues) return;

    try {
      const response = await apiRequest({
        url: 'https://api.vote.vickz.ru/api/v2/change-password',
        method: 'PUT',
        auth: true,
        body: {
          old_password: formValues.oldPassword,
          new_password: formValues.newPassword,
        },
      });

      if (!response.ok) throw new Error('Password change failed');

      Swal.fire({
        icon: 'success',
        title: 'Password Changed',
        text: 'Your password has been updated successfully.',
      });
    } catch (error) {
      console.error(error);
      Swal.fire({
        icon: 'error',
        title: 'Change Failed',
        text: 'Could not change the password. Please try again.',
      });
    }
  };

  return (
    <div className="main-layout">
      <Sidebar />
      <Link to='/swagger' className='dev-tools'>
        <FiTool size={30} />
      </Link>

      <div className="settings-content">
        <h2>Profile Settings</h2>
        <form className="settings-form" onSubmit={handleProfileUpdate}>
          <div className="avatar-section">
            <img src={avatarUrl} alt="Avatar" className="settings-avatar" />
            <input
              type="file"
              accept="image/*"
              onChange={handleAvatarChange}
            />
          </div>

          <label>
            Name:
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </label>

          <label>
            Username:
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </label>

          <label>
            Description:
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
            />
          </label>

          <button type="submit">Save Changes</button>

          <button
            type="button"
            className="change-password-button"
            onClick={handleChangePassword}
          >
            Change Password
          </button>
        </form>
      </div>
    </div>
  );
};

export default SettingsPage;
