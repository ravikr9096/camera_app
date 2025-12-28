import React, { useState } from 'react';
import './CameraConfig.css';

function CameraConfig({ onConfigSuccess }) {
  const [cameraIp, setCameraIp] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [port, setPort] = useState('554');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://192.168.0.86:5000/camera_config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          camera_ip: cameraIp,
          username: username,
          password: password,
          channel: 1,
          port: port
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Config response:', data);
      
      // Pass camera credentials to the success callback
      onConfigSuccess({
        camera_ip: cameraIp,
        username: username,
        password: password,
        port: port
      });
    } catch (error) {
      console.error('Error calling API:', error);
      setError('Failed to configure camera. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="camera-config-container">
      <div className="camera-config-card">
        <h1 className="config-title">Camera Configuration</h1>
        <form onSubmit={handleSubmit} className="config-form">
          <div className="form-group">
            <label htmlFor="camera_ip">Camera IP</label>
            <input
              type="text"
              id="camera_ip"
              value={cameraIp}
              onChange={(e) => setCameraIp(e.target.value)}
              placeholder="Enter camera IP address"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="port">Port</label>
            <input
              type="text"
              id="port"
              value={port}
              onChange={(e) => setPort(e.target.value)}
              placeholder="Enter port (default: 554)"
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? 'Configuring...' : 'Configure Camera'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default CameraConfig;
