import json
import time
import requests
import kone_api_decompile as res
import sqlite3
import random
import freq_detection
import logging
logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")

# makes a destination call for a elevator and logs the action
def destcall_elevator(from_floor, to_floor, people_queue, reset_queue):
  call_object_url = res.post_elevator_call(9990000508, str(from_floor), str(to_floor))
  logging.info("Call object location: %s" % call_object_url)
  time.sleep(3)
  call_state = res.get_call_object(call_object_url)
  logging.info(call_state)
  call_id = call_object_url[50:]
  logging.info('Using elevator: '+ str(call_state["assignedlift"]))
  i = 0
  while True:
    if(call_state["passengerGuidance"] == "enter_car"):
      while not people_queue.empty():
        clean = people_queue.get()
      reset_queue.put(1)
    if(i>300):
      logging.info('Error: too many loops, program quit')
      return False
    call_state = res.get_call_object(call_object_url)
    if(call_state["callState"] == "served"):
      logging.info('Job finished')
      write_log(call_id, from_floor, to_floor)
      return True    
    if(call_state["callState"] == "cancelled"):
      logging.info('Error: Job cancelled')
      if(str(call_state['passengerGuidance'])=='take_stairs'):
        if(from_floor<1 or from_floor>2):
          logging.info('Invalid from floor!')
        elif(to_floor<1 or to_floor>2):
          logging.info('Invalid to_floor!')
      return False
    time.sleep(3)
    i=i+1
    
# makes a landing call for a elevator and logs the action
def landingcall_elevator(from_floor, direction):
  call_object_url = res.post_elevator_call_landing(9990000508, str(from_floor), direction)
  #print("Call object location: %s" % call_object_url)
  time.sleep(2)
  call_state = res.get_call_object(call_object_url)
  call_id = call_object_url[50:]
  write_log(call_id, from_floor, 0)
  logging.info('Using elevator: '+ str(call_state["assignedlift"]))
      
# logs the movement of an elevator    
def write_log(call_id, from_floor, to_floor):
  conn = sqlite3.connect('elevator.db')
  c = conn.cursor()
  c.execute('INSERT INTO call_log (callID, from_floor, to_floor) VALUES (%s, %s, %s);'%(str(call_id), str(from_floor), str(to_floor)))
  conn.commit()
  conn.close()
  
  
def elevators_init(people_queue, reset_queue):
  #Test that our credentials are ok.
    response = res.get_building(res.building_id)
    logging.info("Trying %s responded with code %s" % (res.building_id, response.status_code))
    if response.status_code != 200:
        exit(1)
    while True:
      persons_in_new = 0
      while not people_queue.empty():
        persons_in_new = people_queue.get()

      logging.info('Person in new '+str(persons_in_new))
      #set starting floor
      fromf = 2
      #set random destination and check that it is not the same like start
      tof = random.randrange(1, 20)
      while(fromf==tof):
        tof = random.randrange(1, 20)
      #check if there are new persons
      if(0 < persons_in_new and persons_in_new<16):
        #call the elevator
        logging.info('NEW CALL: From %s, To %s'%(str(fromf),str(tof)))
        destcall_elevator(fromf, tof, people_queue, reset_queue)
        #make a output 
      #are there more than 16 persons? Call two elevators
      elif(persons_in_new>=16):
        logging.info('Two elevators have been called.')
        landingcall_elevator(2, 'up')
        landingcall_elevator(2, 'down')
      #wait 5 seconds
      time.sleep(5)
      # run statistics
      freq_detection.freq_detector_muted()
