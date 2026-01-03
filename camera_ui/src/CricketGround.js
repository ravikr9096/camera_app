import React from 'react';
import './CricketGround.css';
import { API_ENDPOINTS } from './constants';

function CricketGround({ cameraConfig }) {
  const areas = [
    { id: 1, name: '', position: 'top-left' },
    { id: 2, name: '', position: 'top-center' },
    { id: 3, name: '', position: 'top-right' },
    { id: 4, name: '', position: 'middle-left' },
    { id: 5, name: '', position: 'center' },
    { id: 6, name: '', position: 'middle-right' },
    { id: 7, name: '', position: 'bottom-left' },
    { id: 8, name: '', position: 'bottom-center' },
    { id: 9, name: '', position: 'bottom-right' },
  ];

  const handleAreaClick = async (areaId) => {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.GOTO_PRESET}?preset_id=${areaId}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('API response:', data);
    } catch (error) {
      console.error('Error calling API:', error);
    }
  };

  // Construct RTSP URL (for reference, backend should handle this)
  const rtspUrl = cameraConfig 
    ? `rtsp://${cameraConfig.username}:${cameraConfig.password}@${cameraConfig.camera_ip}:${cameraConfig.port}/Streaming/Channels/101/`
    : '';

  // Backend should proxy RTSP to web-compatible format
  // The backend endpoint should handle the RTSP stream conversion
  const videoFeedUrl = API_ENDPOINTS.VIDEO_FEED;

  return (
    <div className="cricket-ground-container">
      <h1 className="cricket-ground-title">The OvalCricket Ground</h1>
      
      <div className="live-feed-container">
        <div className="live-feed-wrapper">
          <img 
            src={videoFeedUrl}
            alt="Live Camera Feed"
            className="live-feed"
          />
        </div>
      </div>

      <div className="cricket-ground">
        {areas.map((area) => (
          <div
            key={area.id}
            className={`cricket-area ${area.position}`}
            data-area-id={area.id}
            onClick={() => handleAreaClick(area.id)}
          >
            <div className="area-label">{area.name}</div>
            <div className="area-number">{area.id}</div>
          </div>
        ))}
      </div>
             <p>^</p>
        <p>Camera This Side</p>
        <p>Powered by: The Oval</p>
    </div>
  );
}

export default CricketGround;
