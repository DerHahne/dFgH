#!/usr/bin/env python
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import kone_api_decompile as res
import time


from time import sleep

class Elevator(Widget):
	r = NumericProperty(1)
	g = NumericProperty(0)
	b = NumericProperty(0)
	color = ReferenceListProperty(r,g,b)
	floor = -2

	def close_doors(self):
		self.color = (1,0,0)

	def open_doors(self):
		self.color = (0,1,0)

	def change_floor(self, next_floor):
		next_floor = int(next_floor)
		if (next_floor == 0):
			print ("Floor 0 doesn't exist")
		else:
			if (next_floor > self.floor):
				print("Subiendo")
				self.close_doors()
				print("self.center_y before: {}".format(self.center_y))
				if (next_floor < 0):
					self.pos[1] = self.parent.height * (next_floor+3) / 22
				else:
					self.pos[1] = self.parent.height * (next_floor+2) / 22
				self.floor = next_floor
				self.open_doors()

			elif (next_floor < self.floor):
				print("Bajando")
				self.close_doors()
				if (next_floor > 0):
					self.pos[1] = self.parent.height * (next_floor+3) / 22
				else:
					self.pos[1] = self.parent.height * (next_floor+2) / 22
				self.floor = next_floor
				self.open_doors()

			else:
				print("Misma planta")
				self.open_doors()


class JunctionKONE(Widget):
	elevator1 = ObjectProperty(None)
	elevator2 = ObjectProperty(None)
	elevator3 = ObjectProperty(None)
	elevators = [elevator1, elevator2, elevator3]

	def update(self, dt):
		floors_array = res.get_building_floors(res.building_id)
		num_elevators = res.get_number_of_elevators(res.building_id)
		floor1 = 0
		floor2 = 0
		floor3 = 0
		for elevator_number, _ in enumerate(range(num_elevators), start=1):
        	# Read elevator deck state
        	# Elevator numbers start from 1, while for loop starts from 0, thus enumerate here
			(carstate_array, links_array) = res.get_elevator_location(res.building_id, elevator_number)
			cardoor_array = res.get_cardoor_state(links_array["carDoors"])

            # Formatting the printout with fixed width fields
			# print("{:1d}: {:8s}, direction={:4s}, floor={:2s}, weight={:3d}%, doors={:1s}".format(
			# 	elevator_number,
			# 	carstate_array["movingState"],
			# 	carstate_array["movingDirection"],
			# 	floors_array[links_array["currentFloor"]]["floorMark"],
			# 	carstate_array["loadPercent"],", ".join(cardoor_array)))
			# if elevator_number == num_elevators:
			# 	print("")
            # e.g. Default Plan: allowed call rate is 5/second: The delay below aims to try to avoid going above that.
			#time.sleep(0.5)
			if((floors_array[links_array["currentFloor"]]["floorMark"] == "K1") and elevator_number == 1):
				floor1 = -1
			elif((floors_array[links_array["currentFloor"]]["floorMark"] == "K2") and elevator_number == 1):
				floor1 = -2
			elif(elevator_number == 1):
				floor1 = int(floors_array[links_array["currentFloor"]]["floorMark"])

			if((floors_array[links_array["currentFloor"]]["floorMark"] == "K1") and elevator_number == 2):
				floor2 = -1
			elif((floors_array[links_array["currentFloor"]]["floorMark"] == "K2") and elevator_number == 2):
				floor2 = -2
			elif(elevator_number == 2):
				floor2 = int(floors_array[links_array["currentFloor"]]["floorMark"])

			if((floors_array[links_array["currentFloor"]]["floorMark"] == "K1") and elevator_number == 3):
				floor3 = -1
			elif((floors_array[links_array["currentFloor"]]["floorMark"] == "K2") and elevator_number == 3):
				floor3 = -2
			elif(elevator_number == 3):
				floor3 = int(floors_array[links_array["currentFloor"]]["floorMark"])

		#f = open('elevators_data.txt', 'r')
		#elevators_pos = f.readline()

		#print("Position: Elevator 1 --> Floor {}, Elevator 2 --> Floor {}, Elevator 3 --> Floor {}".format(floor1, floor2, floor3))

		#self.elevator1.change_floor(int(elevators_pos.split("\n")[0].split(" ")[0]))
		self.elevator1.change_floor(floor1)
		#self.elevator2.change_floor(int(elevators_pos.split("\n")[0].split(" ")[1]))
		self.elevator2.change_floor(floor2)
		#self.elevator3.change_floor(int(elevators_pos.split("\n")[0].split(" ")[2]))
		self.elevator3.change_floor(floor3)


		#f.close()

	def __init__(self, **kwargs):
		super(JunctionKONE, self).__init__(**kwargs)


class JunctionApp(App):
	def build(self):
		kone = JunctionKONE()
		Clock.schedule_interval(kone.update, 0.25)
		return kone
def startUI():
	JunctionApp().run()

if __name__ == '__main__':
	#response = res.get_building(res.building_id)
 	#print("Trying %s responded with code %s" % (res.building_id, response.status_code))
 	#if response.status_code != 200:
  	#	exit(1)
	JunctionApp().run()
	#startUI()
