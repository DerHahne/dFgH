import json
import time
import requests
import kone_api_decompile as res
import sys
import os
import kone_logger

def elevator_call():
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
    to_floor = raw_input("Please enter the floor you wish to go to: ")
    while inputcheck:
        if to_floor.isdigit() and 0 < int(to_floor) < 21 and to_floor != from_floor:
            inputcheck = False
        else:
            to_floor = raw_input("Please enter a number between 1 and 20: ")
    # Make an elevator call

    call_object_url = res.post_elevator_call(res.building_id, from_floor, to_floor)
    time.sleep(2)
    call_state = res.get_call_object(call_object_url)

    print("Elevator %s is coming to floor %s, going to floor %s." % (call_state["assignedlift"], from_floor, to_floor))
    while True:
        call_state = res.get_call_object(call_object_url)
        call_id = call_object_url[50:]
        if(call_state["callState"] == "served"):
            print('Elevator job has finished successfully. Returning to main menu.')
            time.sleep(2)
            kone_logger.write_log(call_id, from_floor, 0)
            return False

if __name__ == '__main__':

    elevator_call()
