import json
import time
import requests
import kone_api_decompile as res
import sys
import os
import kone_logger

def elevator_landing_call():
    os.system('clear')
    print("\n\n###########  ############  ############  ###########\n###########  ############  ############  ###########\n#   ##   ##  ##        ##  ##  ####  ##  ##       ##\n#   #   ###  #   ####   #  ##    ##  ##  ##   ######\n#      ####  #   ####   #  ##        ##  ##       ##\n#   #   ###  ##   ##    #  ##  ##    ##  ##   ######\n#   ###   #  ####     ###  ##  ####  ##  ##       ##\n###########  ############  ############  ###########\n###########  ############  ############  ###########\n\n")
    # Test that our credentials are ok.
    response = res.get_building(res.building_id)
    if response.status_code != 200:
        exit(1)
    inputcheck = True
    # Read building floors
    floors_list = res.get_building_floors(res.building_id)

    from_floor = raw_input("Please enter the floor you're on: ")
    while inputcheck:
        if from_floor.isdigit() and 0 < int(from_floor) < 21:
            inputcheck = False
        else:
            from_floor = raw_input("Please enter a number between 1 and 20: ")
    direction = raw_input("Do you want to go up or down? ")
    inputcheck = True
    while inputcheck:
        if (direction == 'up') or (direction == 'down'):
            inputcheck = False
        else:
            direction = raw_input("Please enter 'up' or 'down': ")

    people = raw_input("How many persons are you? ")
    inputcheck = True
    while inputcheck:
        if people.isdigit():
            inputcheck = False
        else:
            people = raw_input("Please enter a number greater than 0: ")


    # Make an elevator call
    if int(people) >=15:
        call_object_url = res.post_elevator_call_landing(res.building_id, from_floor, 'up')

        call_object_url = res.post_elevator_call_landing(res.building_id, from_floor, 'down')

        print("Calling two elevators to floor %s." % (from_floor))
    else:
        call_object_url = res.post_elevator_call_landing(res.building_id, from_floor, direction)
        print("Calling one elevator to floor %s, going %s." % (from_floor, direction))
        while True:
            call_state = res.get_call_object(call_object_url)
            call_id = call_object_url[50:]
            if(call_state["callState"] == "served"):
                print('Elevator job has finished successfully. Returning to main menu.')
                kone_logger.write_log(call_id, from_floor, 0)
                time.sleep(2)
                return False

if __name__ == '__main__':

    elevator_landing_call()
