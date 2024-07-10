from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

import cv2
from cvzone.PoseModule import PoseDetector

import re
import base64
import numpy as np

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')
CORS(app)


cap = cv2.VideoCapture('video.mp4')

detector = PoseDetector()

@socketio.on('pose')
def handle_pose(data):
    data = re.sub("^data:image/.+;base64,", "", data)
    d = base64.b64decode(data)
    
    n = np.frombuffer(d, np.uint8)
    im = cv2.imdecode(n, cv2.IMREAD_COLOR)
    
    im2 = detector.findPose(im)
    ll, bi = detector.findPosition(im2)
    
    if bi:
        r, b = cv2.imencode('.jpeg', im2)
        b64 = base64.b64encode(b).decode('utf-8')
        socketio.emit('pose', b64)
    else:
        r, b = cv2.imencode('.jpeg', im)
        b64 = base64.b64encode(b).decode('utf-8')
        socketio.emit('pose', b64)
    

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True)