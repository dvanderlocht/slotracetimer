#!/usr/bin/env python3
###########################################################################   
#
# Description: Raspberry Pi slotrace timer software with button control and 
#              web based user interface.
#
# Copyright (C) 2018  Dave van der Locht    (dave.is@home.nl)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###########################################################################

import os
import sys
import time
import datetime
import json
import asyncio
import RPi.GPIO as GPIO
import wsserver

from tornado import ioloop
from racecontrol import racecontrol_hardware
from racecontrol import racecontrol_status
from racecontrol import racecontrol_obj
from threading import Thread


def init_gpio():     
    GPIO.setmode(GPIO.BCM)         
    # Setup sensor inputs
    GPIO.setup(racecontrol_hardware.SENSOR_LANE1_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(racecontrol_hardware.SENSOR_LANE2_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(racecontrol_hardware.SENSOR_LANE1_GPIO, GPIO.BOTH, callback=sensor_callback, bouncetime=10)
    GPIO.add_event_detect(racecontrol_hardware.SENSOR_LANE2_GPIO, GPIO.BOTH, callback=sensor_callback, bouncetime=10)     
    # Setup button inputs
    GPIO.setup(racecontrol_hardware.BUTTON_START_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(racecontrol_hardware.BUTTON_RESET_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(racecontrol_hardware.BUTTON_LAPS_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(racecontrol_hardware.BUTTON_START_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=200)    
    GPIO.add_event_detect(racecontrol_hardware.BUTTON_RESET_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=200)    
    GPIO.add_event_detect(racecontrol_hardware.BUTTON_LAPS_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=200)  

def button_callback(channel):    
    if GPIO.input(racecontrol_hardware.BUTTON_START_GPIO) is 0:     # active low
        racecontrol_obj.start_button_pressed = True
        print("Button start/stop pressed")  
    if GPIO.input(racecontrol_hardware.BUTTON_RESET_GPIO) is 0:     # active low        
        racecontrol_obj.reset_race()
        print("Button reset pressed") 
    if GPIO.input(racecontrol_hardware.BUTTON_LAPS_GPIO) is 0:     # active low
        racecontrol_obj.incr_race_laps()
        print("Button laps+ pressed")

def sensor_callback(channel):       
    if racecontrol_status.race_state == racecontrol_status.RACE:  
        now = datetime.datetime.now()      
        timestamp = time.time()
        stamp = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')          
            
        if GPIO.input(racecontrol_hardware.SENSOR_LANE1_GPIO) is 0:                              
            print("Lane 1 sensor LOW " + str(channel) + " time: "+ stamp)
            # Check if this is our first lap
            if racecontrol_obj.lane1_start_time == 0:                
                racecontrol_obj.lane1_start_time = datetime.datetime.now()
            else:
                # Lap time must be too short                
                l1laptime = now - racecontrol_obj.lane1_start_time  
                elapsedms = l1laptime.total_seconds() * 1000                              
                if elapsedms > 750:
                    racecontrol_obj.lane1_last_lap_time = l1laptime
                    racecontrol_obj.lane1_start_time = datetime.datetime.now()       
                    racecontrol_obj.lane1_total_lap_time = racecontrol_obj.lane1_total_lap_time + l1laptime         
                    racecontrol_obj.lane1_lapcount += 1                        
                    print("Lane 1 Lap: " + str(racecontrol_obj.lane1_lapcount) + " Time: " + str(racecontrol_obj.lane1_last_lap_time) )                                    
                    # Best lap time ?
                    if (racecontrol_obj.lane1_lapcount == 1):   
                        racecontrol_obj.lane1_best_lap_time = racecontrol_obj.lane1_last_lap_time        
                        racecontrol_obj.lane1_best_lap = racecontrol_obj.lane1_lapcount        
                    elif (racecontrol_obj.lane1_last_lap_time < racecontrol_obj.lane1_best_lap_time):
                        racecontrol_obj.lane1_best_lap_time = racecontrol_obj.lane1_last_lap_time 
                        racecontrol_obj.lane1_best_lap = racecontrol_obj.lane1_lapcount                   
                                    
                    racecontrol_obj.send_lap_time(1, racecontrol_obj.lane1_lapcount, racecontrol_obj.lane1_last_lap_time)
                    pos = racecontrol_obj.check_position_in_race(1)
                    lap = [1, racecontrol_obj.lane1_lapcount, racecontrol_obj.lane1_last_lap_time, pos]
                    racecontrol_obj.add_lap_to_list(lap)        
                    # update positions to websocket clients                    
                    racecontrol_obj.send_positions_to_clients()   
            
            if (racecontrol_obj.lane1_lapcount <= racecontrol_obj.laps_max):    
                racecontrol_hardware.blink_lane(1)            
                      
        if GPIO.input(racecontrol_hardware.SENSOR_LANE2_GPIO) is 0:
            print("Lane 2 sensor LOW " + str(channel) + " time: "+ stamp)
            # Check if this is our first lap
            if racecontrol_obj.lane2_start_time == 0:                
                racecontrol_obj.lane2_start_time = datetime.datetime.now()
            else:
                # Lap time must be too short
                l2laptime = now - racecontrol_obj.lane2_start_time                
                elapsedms = l2laptime.total_seconds() * 1000                              
                if elapsedms > 750:
                    racecontrol_obj.lane2_last_lap_time = l2laptime
                    racecontrol_obj.lane2_start_time = datetime.datetime.now()     
                    racecontrol_obj.lane2_total_lap_time = racecontrol_obj.lane2_total_lap_time + l2laptime           
                    racecontrol_obj.lane2_lapcount += 1
                    print("Lane 2 Lap: " + str(racecontrol_obj.lane2_lapcount) + " Time: " + str(racecontrol_obj.lane2_last_lap_time) )                                    
                    # Best lap time                
                    if (racecontrol_obj.lane2_lapcount == 1):   
                        racecontrol_obj.lane2_best_lap_time = racecontrol_obj.lane2_last_lap_time
                        racecontrol_obj.lane2_best_lap = racecontrol_obj.lane2_lapcount
                    elif (racecontrol_obj.lane2_last_lap_time < racecontrol_obj.lane2_best_lap_time):
                        racecontrol_obj.lane2_best_lap_time = racecontrol_obj.lane2_last_lap_time 
                        racecontrol_obj.lane2_best_lap = racecontrol_obj.lane2_lapcount
                    
                    racecontrol_obj.send_lap_time(2, racecontrol_obj.lane2_lapcount, racecontrol_obj.lane2_last_lap_time)
                    pos = racecontrol_obj.check_position_in_race(2)
                    lap = [2, racecontrol_obj.lane2_lapcount, racecontrol_obj.lane2_last_lap_time, pos]
                    racecontrol_obj.add_lap_to_list(lap) 
                    # update positions to websocket clients
                    racecontrol_obj.send_positions_to_clients()     
            
            if (racecontrol_obj.lane2_lapcount <= racecontrol_obj.laps_max):
                racecontrol_hardware.blink_lane(2) 
                 
     
def main():    
    try:    
        print("RPi Slotrace Timer - Copyright (C) 2018  Dave van der Locht")    
        
        # Init GPIO
        init_gpio()      
                            
        # Start websocket server thread
        ws = wsserver.WebServer()
        def start_server():
            asyncio.set_event_loop(asyncio.new_event_loop())
            ws.run()        
       
        t = Thread(target=start_server, args=())
        t.daemon = True
        t.start()                
        #t.join()                
        print("Websocket server thread started")      
        
        # Show we're done loading
        racecontrol_hardware.start_light_test()
        print("Press start button to start race " + str(racecontrol_obj.laps) + " laps")
        
        # Loop until users quits with CTRL-C
        while True:
            # Check if there's already a lane finished (max laps reached)
            if racecontrol_status.race_state == racecontrol_status.RACE:                    
                if racecontrol_obj.lane1_lapcount == racecontrol_obj.laps:
                    print("Race ended! Lane 1 is winner!")
                    racecontrol_status.race_state = racecontrol_status.FINISH
                    racecontrol_hardware.show_winner(1)
                    racecontrol_obj.send_status_to_clients()
                    
                elif racecontrol_obj.lane2_lapcount == racecontrol_obj.laps:
                    print("Race ended! Lane 2 is winner!")
                    racecontrol_status.race_state = racecontrol_status.FINISH
                    racecontrol_hardware.show_winner(2)
                    racecontrol_obj.send_status_to_clients() 
            
            if racecontrol_obj.start_button_pressed:
                # Reset button state
                racecontrol_obj.start_button_pressed = False                    
                # Place cars
                if racecontrol_status.race_state == racecontrol_status.OFF:
                    racecontrol_status.race_state = racecontrol_status.PRE_START   
                    racecontrol_hardware.start_light_red_on()
                    racecontrol_obj.send_status_to_clients()    # inform clients
                    print("Place cars...")                    
                # Start
                elif racecontrol_status.race_state == racecontrol_status.PRE_START:                        
                    print("Get set... Counting down")
                    racecontrol_status.race_state = racecontrol_status.START 
                    racecontrol_obj.send_status_to_clients()    # inform clients
                    racecontrol_hardware.start_light_countdown()
                    racecontrol_status.race_state = racecontrol_status.RACE
                    racecontrol_obj.send_status_to_clients()    # inform clients
                    print("Go!!!")                 
                # Pause / yellow flag
                elif racecontrol_status.race_state == racecontrol_status.RACE:
                    racecontrol_status.race_state = racecontrol_status.YELLOW_FLAG  
                    racecontrol_hardware.start_light_yellow_flag_on() 
                    racecontrol_obj.send_status_to_clients()    # inform clients
                    print("Race paused (yellow flag)")                                                
                # Resume from yellow flag
                elif racecontrol_status.race_state == racecontrol_status.YELLOW_FLAG:                        
                    racecontrol_status.race_state = racecontrol_status.RACE
                    racecontrol_hardware.start_light_yellow_flag_off()    
                    racecontrol_obj.send_status_to_clients()    # inform clients
                    print("Race resumed")                      
                # Reset race after finish and start again
                elif racecontrol_status.race_state == racecontrol_status.FINISH:
                    racecontrol_obj.reset_race()
                    racecontrol_hardware.start_light_red_on()    
                                                      
            time.sleep(0.1)
               
    except KeyboardInterrupt:
        # Reset GPIO settings
        #GPIO.cleanup()
        print("Exiting...")

if __name__=="__main__": 
    main()