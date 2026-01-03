// Backend API configuration
export const BACKEND_HOST = '192.168.1.9';
export const BACKEND_PORT = '5000';

// Backend base URL
export const BACKEND_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}`;

// API endpoints
export const API_ENDPOINTS = {
  CAMERA_CONFIG: `${BACKEND_URL}/camera_config`,
  GOTO_PRESET: `${BACKEND_URL}/goto_preset`,
  VIDEO_FEED: `${BACKEND_URL}/video_feed`,
  ZOOM_IN: `${BACKEND_URL}/zoom_in`,
  ZOOM_OUT: `${BACKEND_URL}/zoom_out`,
};

