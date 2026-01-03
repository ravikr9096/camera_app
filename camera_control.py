import requests
from requests.auth import HTTPDigestAuth
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import cv2
import time

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# --- Dynamic Camera Configuration ---
# Initialize with default values
camera_config = {
    "camera_ip": "192.168.0.111",
    "username": "admin",
    "password": "Admin@1508",
    "channel": 1,
    "rtsp_port": 554  # Default RTSP port
}

# Note: Each client connection creates its own video capture object

def goto_preset(preset_id):
    """
    Sends a command to the Hikvision ISAPI to go to a specific preset.
    Uses the current camera configuration.
    Returns a dictionary with success status and message.
    """
    url = f"http://{camera_config['camera_ip']}/ISAPI/PTZCtrl/channels/{camera_config['channel']}/presets/{preset_id}/goto"

    try:
        # Hikvision uses Digest Authentication for security
        response = requests.put(
            url, 
            auth=HTTPDigestAuth(camera_config['username'], camera_config['password']), 
            timeout=5
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": f"Successfully moved to Preset {preset_id}",
                "preset_id": preset_id,
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "message": f"Error: Received status code {response.status_code}",
                "preset_id": preset_id,
                "status_code": response.status_code,
                "error_details": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection failed: {str(e)}",
            "preset_id": preset_id,
            "error": str(e)
        }

@app.route('/goto_preset/<int:preset_id>', methods=['GET', 'POST'])
def api_goto_preset(preset_id):
    """
    API endpoint to move camera to a specific preset.
    
    Args:
        preset_id (int): The preset number (1-6, or any valid preset)
    
    Returns:
        JSON response with success status and message
    """
    result = goto_preset(preset_id)
    
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@app.route('/goto_preset', methods=['GET', 'POST'])
def api_goto_preset_query():
    """
    API endpoint to move camera to a specific preset using query parameter.
    
    Query Parameters:
        preset_id (int): The preset number (1-6, or any valid preset)
    
    Returns:
        JSON response with success status and message
    """
    preset_id = request.args.get('preset_id', type=int)
    
    if preset_id is None:
        return jsonify({
            "success": False,
            "message": "Missing required parameter: preset_id"
        }), 400
    
    result = goto_preset(preset_id)
    
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

def zoom_continuous(zoom_speed):
    """
    Sends a continuous zoom command to the Hikvision camera.
    
    Args:
        zoom_speed (int): Zoom speed (-1 to 1, positive for zoom in, negative for zoom out)
    
    Returns:
        Dictionary with success status and message
    """
    url = f"http://{camera_config['camera_ip']}/ISAPI/PTZCtrl/channels/{camera_config['channel']}/continuous"
    
    # XML body for continuous PTZ control
    xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<PTZData>
    <pan>0</pan>
    <tilt>0</tilt>
    <zoom>{zoom_speed}</zoom>
</PTZData>"""
    
    try:
        response = requests.put(
            url,
            data=xml_body,
            auth=HTTPDigestAuth(camera_config['username'], camera_config['password']),
            headers={'Content-Type': 'application/xml'},
            timeout=5
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": f"Zoom command sent successfully (speed: {zoom_speed})",
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "message": f"Error: Received status code {response.status_code}",
                "status_code": response.status_code,
                "error_details": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection failed: {str(e)}",
            "error": str(e)
        }

def zoom_stop():
    """
    Stops all PTZ movement including zoom.
    
    Returns:
        Dictionary with success status and message
    """
    url = f"http://{camera_config['camera_ip']}/ISAPI/PTZCtrl/channels/{camera_config['channel']}/continuous"
    
    # XML body to stop all movement (all zeros)
    xml_body = """<?xml version="1.0" encoding="UTF-8"?>
<PTZData>
    <pan>0</pan>
    <tilt>0</tilt>
    <zoom>0</zoom>
</PTZData>"""
    
    try:
        response = requests.put(
            url,
            data=xml_body,
            auth=HTTPDigestAuth(camera_config['username'], camera_config['password']),
            headers={'Content-Type': 'application/xml'},
            timeout=5
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "Zoom stopped",
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "message": f"Error: Received status code {response.status_code}",
                "status_code": response.status_code,
                "error_details": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection failed: {str(e)}",
            "error": str(e)
        }

def zoom_in_multiple(times=5, duration=0.5):
    """
    Performs zoom in operation multiple times.
    
    Args:
        times (int): Number of times to zoom in (default: 5)
        duration (float): Duration in seconds for each zoom operation (default: 0.5)
    
    Returns:
        Dictionary with success status and message
    """
    results = []
    all_success = True
    
    for i in range(times):
        # Start zoom in (speed = 1)
        result = zoom_continuous(1)
        if not result["success"]:
            all_success = False
            results.append(result)
            break
        
        # Wait for the zoom duration
        time.sleep(duration)
        
        # Stop zoom
        stop_result = zoom_stop()
        if not stop_result["success"]:
            all_success = False
            results.append(stop_result)
            break
        
        results.append(result)
        # Small delay between operations
        time.sleep(0.1)
    
    if all_success:
        return {
            "success": True,
            "message": f"Successfully zoomed in {times} times",
            "operations": times,
            "results": results
        }
    else:
        return {
            "success": False,
            "message": f"Zoom in operation failed after {len(results)} successful operations",
            "operations": len(results),
            "results": results
        }

def zoom_out_multiple(times=5, duration=0.5):
    """
    Performs zoom out operation multiple times.
    
    Args:
        times (int): Number of times to zoom out (default: 5)
        duration (float): Duration in seconds for each zoom operation (default: 0.5)
    
    Returns:
        Dictionary with success status and message
    """
    results = []
    all_success = True
    
    for i in range(times):
        # Start zoom out (speed = -1)
        result = zoom_continuous(-1)
        if not result["success"]:
            all_success = False
            results.append(result)
            break
        
        # Wait for the zoom duration
        time.sleep(duration)
        
        # Stop zoom
        stop_result = zoom_stop()
        if not stop_result["success"]:
            all_success = False
            results.append(stop_result)
            break
        
        results.append(result)
        # Small delay between operations
        time.sleep(0.1)
    
    if all_success:
        return {
            "success": True,
            "message": f"Successfully zoomed out {times} times",
            "operations": times,
            "results": results
        }
    else:
        return {
            "success": False,
            "message": f"Zoom out operation failed after {len(results)} successful operations",
            "operations": len(results),
            "results": results
        }

@app.route('/zoom_in', methods=['GET', 'POST'])
def api_zoom_in():
    """
    API endpoint to zoom in 5 times.
    
    Query Parameters (optional):
        times (int): Number of times to zoom in (default: 5)
        duration (float): Duration in seconds for each zoom operation (default: 0.5)
    
    Returns:
        JSON response with success status and message
    """
    times = request.args.get('times', type=int, default=5)
    duration = request.args.get('duration', type=float, default=0.5)
    
    result = zoom_in_multiple(times, duration)
    
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@app.route('/zoom_out', methods=['GET', 'POST'])
def api_zoom_out():
    """
    API endpoint to zoom out 5 times.
    
    Query Parameters (optional):
        times (int): Number of times to zoom out (default: 5)
        duration (float): Duration in seconds for each zoom operation (default: 0.5)
    
    Returns:
        JSON response with success status and message
    """
    times = request.args.get('times', type=int, default=5)
    duration = request.args.get('duration', type=float, default=0.5)
    
    result = zoom_out_multiple(times, duration)
    
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@app.route('/camera_config', methods=['POST'])
def set_camera_config():
    """
    API endpoint to set/get camera configuration.
    
    Accepts JSON body with optional parameters:
        - camera_ip (str): Camera IP address
        - username (str): Camera username
        - password (str): Camera password
        - channel (int): Camera channel (usually 1)
        - rtsp_port (int): RTSP port (default: 554)
    
    If parameters are provided, updates the configuration.
    Always returns the current configuration.
    
    Returns:
        JSON response with current camera_ip, username, password, and channel
    """
    global camera_config
    
    if request.is_json:
        data = request.get_json()
        
        # Update configuration with provided values
        if 'camera_ip' in data:
            camera_config['camera_ip'] = data['camera_ip']
        if 'username' in data:
            camera_config['username'] = data['username']
        if 'password' in data:
            camera_config['password'] = data['password']
        if 'channel' in data:
            camera_config['channel'] = int(data['channel'])
        if 'rtsp_port' in data:
            camera_config['rtsp_port'] = int(data['rtsp_port'])
    
    # Return current configuration
    return jsonify({
        "camera_ip": camera_config['camera_ip'],
        "username": camera_config['username'],
        "password": camera_config['password'],
        "channel": camera_config['channel'],
        "rtsp_port": camera_config['rtsp_port']
    }), 200

def generate_frames():
    """
    Generator function that captures frames from the RTSP stream and yields them as JPEG.
    Creates a new video capture for each client connection.
    """
    rtsp_url = f"rtsp://{camera_config['username']}:{camera_config['password']}@{camera_config['camera_ip']}:{camera_config['rtsp_port']}/Streaming/Channels/101/"
    
    # Create a new video capture for this client connection
    video_capture = cv2.VideoCapture(rtsp_url)
    
    if not video_capture.isOpened():
        print(f"Error: Could not open RTSP stream: {rtsp_url}")
        video_capture.release()
        return
    
    try:
        while True:
            ret, frame = video_capture.read()
            
            if not ret:
                print("Error: Failed to read frame from RTSP stream")
                break
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            
            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        # Clean up: release the video capture when done
        video_capture.release()

@app.route('/video_feed')
def video_feed():
    """
    API endpoint to stream video feed from the camera via RTSP.
    
    Returns:
        MJPEG video stream (multipart/x-mixed-replace)
    """
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "camera_ip": camera_config['camera_ip'],
        "channel": camera_config['channel']
    }), 200

if __name__ == "__main__":
    print(f"Starting Flask API for Hikvision camera...")
    print(f"Default camera IP: {camera_config['camera_ip']}")
    print("API Endpoints:")
    print("  GET/POST /goto_preset/<preset_id> - Move to preset by path parameter")
    print("  GET/POST /goto_preset?preset_id=<id> - Move to preset by query parameter")
    print("  GET/POST /zoom_in?times=5&duration=0.5 - Zoom in multiple times (default: 5 times)")
    print("  GET/POST /zoom_out?times=5&duration=0.5 - Zoom out multiple times (default: 5 times)")
    print("  POST /camera_config - Set/Get camera configuration (IP, username, password, channel, rtsp_port)")
    print("  GET /video_feed - Stream video feed from camera (MJPEG)")
    print("  GET /health - Health check")
    app.run(host='0.0.0.0', port=5000, debug=True)