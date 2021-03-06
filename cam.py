#!/usr/bin/env python
from WebcamVideoStream import WebcamVideoStream
import cv2
import time
 
from flask import Flask, render_template, Response
 
app = Flask(__name__)
detection_queue = None
 
@app.route('/')
def index():
    return render_template('index.html')
 
def gen(vs):
    count = 1
    while True:
        frame = vs.readDetections()
        count = count+1
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        time.sleep(0.5)
 
@app.route('/video_feed')
def video_feed():
    return Response(gen(WebcamVideoStream().start(detection_queue)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def cam_start(people_queue):
    global detection_queue 
    detection_queue = people_queue
    app.run(host='0.0.0.0', debug=True)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True)


