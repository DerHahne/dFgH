import json
import time
import requests
import kone_api_decompile as res
import sys
import os
import subprocess
import landCall
import destCall
import kone_logger
import freq_detection
import WebcamVideoStream as vs
import elevator_functions as elev_func
import Queue
from threading import Thread
import logging
logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")

people_queue = Queue.Queue()
reset_queue = Queue.Queue(1)

if __name__ == "__main__":

    logging.info('***********NEW RUN****************')
    # Test that our credentials are ok.
    response = res.get_building(res.building_id)
    if response.status_code != 200:
        exit(1)
    else:
        print ("Connection with building #%s established" % (res.building_id))

    camera = Thread(target=lambda:vs.detection_init(people_queue, reset_queue))
    camera.setDaemon(True)
    camera.start()

    elevators = Thread(target=lambda:elev_func.elevators_init(people_queue, reset_queue))
    elevators.setDaemon(True)
    elevators.start()

    while True:
        os.system('clear')
        print("\n\n###########  ############  ############  ###########\n###########  ############  ############  ###########\n#   ##   ##  ##        ##  ##  ####  ##  ##       ##\n#   #   ###  #   ####   #  ##    ##  ##  ##   ######\n#      ####  #   ####   #  ##        ##  ##       ##\n#   #   ###  ##   ##    #  ##  ##    ##  ##   ######\n#   ###   #  ####     ###  ##  ####  ##  ##       ##\n###########  ############  ############  ###########\n###########  ############  ############  ###########\n\n")
        print ("Welcome to KONE smart elevator control\n\nMain Menu:\n\n1. Elevator Watch\n2. Emergency Elevator Control\n3. Elevator Call (Landing)\n4. Elevator statistics\n5. Quit\n")
    # run camera shit
        inputcheck = True
        user_input = raw_input("Please enter your desired option: ")
        while inputcheck:
            if (user_input.isdigit() and 0 < int(user_input) < 6):
                inputcheck = False
            else:
                user_input = raw_input("Please enter a number between 1 and 5: ")
        if int(user_input) == 1:
            print subprocess.call(['python2.7','kivy/main.py'])
        elif int(user_input) == 2:
            destCall.elevator_call()
        elif int(user_input) == 3:
            landCall.elevator_landing_call()
        elif int(user_input) == 4:
            freq_detection.freq_detector()
        elif int(user_input) == 5 or user_input =='q':
            exit(1)
    exit(1)
