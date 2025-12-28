import React, { useState } from 'react';
import './App.css';
import CameraConfig from './CameraConfig';
import CricketGround from './CricketGround';

function App() {
  const [isConfigured, setIsConfigured] = useState(false);
  const [cameraConfig, setCameraConfig] = useState(null);

  const handleConfigSuccess = (config) => {
    setCameraConfig(config);
    setIsConfigured(true);
  };

  return (
    <div className="App">
      {!isConfigured ? (
        <CameraConfig onConfigSuccess={handleConfigSuccess} />
      ) : (
        <CricketGround cameraConfig={cameraConfig} />
      )}
    </div>
  );
}

export default App;
