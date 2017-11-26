from __future__ import print_function
from threading import Thread
import threading
import numpy as np
import cv2
import sys
import imutils
import datetime
import time
import Person
import math
import logging
logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")

personSize = 6000
persons = []
pid = 1
entered = 0
exited = 0
 
def draw_detections(img, rects, thickness = 2):
  for x, y, w, h in rects:
    pad_w, pad_h = int(0.15*w), int(0.05*h)
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), thickness)

def reset():
  global entered, exited
  entered = 0
  exited = 0
 
class WebcamVideoStream(object):
 def __init__(self):
  self.video = cv2.VideoCapture('http://192.168.43.128:3000/stream.mjpg')
  #self.video = cv2.VideoCapture('test.mp4')
  self.w = self.video.get(3) #CV_CAP_PROP_FRAME_WIDTH
  self.h = self.video.get(4) #CV_CAP_PROP_FRAME_HEIGHT

  self.rangeLeft = int(1*(self.w/6))
  self.rangeRight = int(5*(self.w/6))
  self.midLine = int(2.5*(self.w/6))
 
  _, self.rawImage = self.video.read()
  self.firstFrame = cv2.cvtColor(self.rawImage, cv2.COLOR_BGR2GRAY)
  ret, jpeg = cv2.imencode('.jpg', self.rawImage)
  self.frameDetections = jpeg.tobytes()
 
  self.contours= []
 
  # initialize the variable used to indicate if the thread should
  # be stopped
  self.stopped = False
 
 def __del__(self):
  self.video.release()
 
 def start(self, people_queue):
  # start the thread to read frames from the video stream
  t = Thread(target=self.update, args=())
  t.daemon = True
  t.start()
  t2 = Thread(target=lambda:self.updateContours(people_queue))
  t2.daemon = True
  t2.start()
  return self
 
 def update(self):
  # keep looping infinitely until the thread is stopped
  count = 1
  while True:
   tic = time.clock()
   # if the thread indicator variable is set, stop the thread
   if self.stopped:
    return
 
   # otherwise, read the next frame from the stream
   (self.grabbed, self.rawImage) = self.video.read()
   #self.rawImage = imutils.rotate(self.rawImage, 45)
   cv2.line(self.rawImage, (0,int(self.h*5/6)), (int(self.w), int(self.h*1/6)), (0,0,255), 5)
   img = self.rawImage.copy()
   #draw rectangles around the people
   draw_detections(img,self.contours)

   #visually show the counters
   cv2.putText(img, "Entered: " + str(entered) ,(10,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2,cv2.LINE_AA)
   cv2.putText(img, "Exited: " + str(exited) ,(10,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2,cv2.LINE_AA)
   ret, jpeg = cv2.imencode('.jpg', img)
   self.frameDetections = jpeg.tobytes()
   toc = time.clock()
   if(toc-tic < 0.5):
    time.sleep(0.5-toc+tic)

 
 def updateContours(self, people_queue):
  # keep looping infinitely until the thread is stopped
  global personSize
  while True:
   tic = time.clock()
   # if the thread indicator variable is set, stop the thread
   if self.stopped:
    return
 
   #get the current frame and look for people
   total = datetime.datetime.now()
   img = cv2.cvtColor(self.rawImage, cv2.COLOR_BGR2GRAY)
   total = datetime.datetime.now()
   frameDelta = cv2.absdiff(self.firstFrame, img)
   ret, thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)
   (_, allContours, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   personContours = []
   for c in allContours:
    # only look at contours larger than a certain size
    #logging.info("Width of rectangle: {} , heigth of rectange: {}".format(cv2.boundingRect(c)[2], cv2.boundingRect(c)[3]))
    temp = cv2.boundingRect(c)
    #if (cv2.contourArea(c) > personSize) and (cv2.boundingRect(c)[2] < self.w/2) and (cv2.boundingRect(c)[3] < 3*self.h/4):
    if (temp[2] > self.w/8) and (temp[3] > self.h/4) and (temp[2] < self.w/2) and (temp[3] < 3*self.h/4):
     personContours.append(cv2.boundingRect(c))
   self.contours = personContours
   # track the people in the frame
   self.people_tracking(self.contours, people_queue)
   toc = time.clock()
   if(toc-tic < 0.5):
    time.sleep(0.5-toc+tic)
 
 
 def readDetections(self):
  # return the frame with people detections
  return self.frameDetections
 
 def stop(self):
  # indicate that the thread should be stopped
  self.stopped = True
  
 def people_tracking(self, rects, people_queue):
  global pid
  global entered
  global exited
  for x, y, w, h in rects:
   new = True
   xCenter = x + w/2
   yCenter = y + h/2
   xChange = xCenter-self.w/2
   yChange = yCenter-self.h/2
   slope = self.h/self.w
   conditionAa = xChange in range(int(-self.w/3), 0)
   conditionAb = yChange in range(int(-slope*(xChange+self.w/3)), int(slope*(xChange+self.w/3)))
   conditionBa = (xChange in range(0, int(self.w/3)))
   conditionBb = yChange in range(int(slope*(xChange-self.w/3)), int(slope*(xChange-self.w/3)))
   inActiveZone= (conditionAa and conditionAb) or (conditionBa and conditionBb)
   #inActiveZone= xCenter in range(self.rangeLeft,self.rangeRight)
   for index, p in enumerate(persons):
    dist = math.sqrt((xCenter - p.getX())**2 + (yCenter - p.getY())**2)
    if dist <= 2*w and dist <= 2*h:
     #logging.info("Person coordinates before({}, {})".format(p.getX(), p.getY()))
     #logging.info("Person coordinates now({}, {})".format(xCenter, yCenter))
     if inActiveZone:
      # logging.info("In active zone!")
      new = False
      if(p.getY() != yCenter) and (p.getX() != xCenter):
        pass
        # logging.info("Data: \npersonCoordinates = ({}, {})\n currentCoordinates = ({}, {})\n firstCondition: {} > {} and {} < {}\n secondCondition {} > {} and {} < {}".format(p.getX(), p.getY(), xCenter, yCenter, p.getY(), (self.h/6)*(5-4*p.getX()/(self.w)), yCenter, self.h/6*(5-4*xCenter/(self.w)), p.getY(), (self.h/6)*(5-4*p.getX()/(self.w)), yCenter, self.h/6*(5-4*xCenter/(self.w))))
      if ((p.getY() > (self.h/6)*(5-4*p.getX()/(self.w))) and  (yCenter < self.h/6*(5-4*xCenter/(self.w)))):
       #  logging.info("[INFO] person going up left " + str(p.getId()))
       entered += 1
       logging.info('CAM: People entered -> '+str(entered))
       people_queue.put(entered)
      if ((p.getY() < (self.h/6)*(5-4*p.getX()/(self.w))) and  (yCenter > self.h/6*(5-4*xCenter/(self.w)))):
       #  logging.info("[INFO] person going right " + str(p.getId()))
       exited += 1
      p.updateCoords(xCenter,yCenter)
      break
     else:
      if(p.getTimesNotDetected() > 5):
        # logging.info("[INFO] person removed " + str(p.getId()))
        persons.pop(index)
      else:
        p.incrementTimesNotDetected()
   if new == True and inActiveZone:
    # logging.info("[INFO] new person " + str(pid))
    p = Person.Person(pid, xCenter, yCenter)
    persons.append(p)
    pid += 1

def detection_init(people_queue, reset_queue):

  vs = WebcamVideoStream().start(people_queue) 
  count = 1
  while True:
    frame = vs.readDetections()
    # f = open('images/photo'+str(count)+'.jpg','w')
    # f.write(frame)
    # f.close()
    count = count+1

    if not reset_queue.empty():
      a = reset_queue.get()
      reset()

    time.sleep(0.5)


if __name__ == '__main__':
  
  vs = WebcamVideoStream().start() 
  count = 1
  while True:
    frame = vs.readDetections()
    f = open('images/photo'+str(count)+'.jpg','w')
    f.write(frame)
    f.close()
    count = count+1
    time.sleep(0.5)
