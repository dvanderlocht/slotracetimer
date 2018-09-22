###########################################################################   
#
# Description: RaceControl classes for slotracetimer
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

import threading
import time
import datetime
import json
import asyncio
import wsserver

from gpiozero import LED


LED_RED1 = LED(7)
LED_RED2 = LED(8)
LED_RED3 = LED(9)
LED_RED4 = LED(10)
LED_RED5 = LED(11)
LED_YELLOW = LED(24)
LED_GREEN = LED(25)   


class RaceControlSession(object):
    
    def __init__(self):
        self.__laps = []

racecontrol_session = RaceControlSession()


class RaceControlLap(object):
    
    def __init__(self):
        self.__lane = None
        self.__number = None
        self.__time = None
    
    @property
    def lane(self):
        return self.__lane
    
    @lane.setter
    def lane(self, value):
        self.__lane = value
        
    @property
    def number(self):
        return self.__number
    
    @number.setter
    def number(self, value):
        self.__number = value              
        
    @property
    def time(self):
        return self.__time
    
    @time.setter
    def time(self, value):
        self.__time = value          

        
class RaceControlHardware():   
     
    def __init__(self):               
        # Hardware GPIO connections (BCM numbering)
        self.SENSOR_LANE1_GPIO = 4
        self.SENSOR_LANE2_GPIO = 14
        self.BUTTON_START_GPIO = 17
        self.BUTTON_RESET_GPIO = 18
        self.BUTTON_LAPS_GPIO = 27

    def start_light_test(self):
        LED_RED1.on()
        time.sleep(0.5)
        LED_RED2.on()
        time.sleep(0.5)        
        LED_RED3.on()
        time.sleep(0.5)
        LED_RED4.on()
        time.sleep(0.5)
        LED_RED5.on()
        time.sleep(0.5)      
        LED_YELLOW.on()
        LED_GREEN.on()
        time.sleep(1.5)  
        self.start_light_all_off()                   
        
    def start_light_red_on(self):
        # Set leds
        LED_RED1.on()
        LED_RED2.on()
        LED_RED3.on()
        LED_RED4.on()
        LED_RED5.on()               
        
    def start_light_countdown(self):
        #asyncio.set_event_loop(asyncio.new_event_loop())
        # all off
        self.start_light_all_off()      
        time.sleep(2)       
        # 1 
        LED_RED1.on()
        frame = {'frame_type': 3, 'count_down': 5 }
        for c in wsserver.clients:
            c.write_message(json.dumps(frame, indent=4, sort_keys=True, default=str))           
        time.sleep(1)
        # 2
        LED_RED2.on()
        frame = {'frame_type': 3, 'count_down': 4 }
        for c in wsserver.clients:
            c.write_message(json.dumps(frame, indent=4, sort_keys=True, default=str))           
        time.sleep(1)
        # 3
        LED_RED3.on()
        frame = {'frame_type': 3, 'count_down': 3 }
        for c in wsserver.clients:
            c.write_message(json.dumps(frame, indent=4, sort_keys=True, default=str))           
        time.sleep(1)
        # 4
        LED_RED4.on()
        frame = {'frame_type': 3, 'count_down': 2 }
        for c in wsserver.clients:
            c.write_message(json.dumps(frame, indent=4, sort_keys=True, default=str))    
        time.sleep(1)
        # 5
        LED_RED5.on()
        frame = {'frame_type': 3, 'count_down': 1 }
        for c in wsserver.clients:
            c.write_message(json.dumps(frame, indent=4, sort_keys=True, default=str))           
        time.sleep(1)
        # off -> go go go                        
        self.start_light_all_off()          
        LED_GREEN.on()
        frame = {'frame_type': 3, 'count_down': 0 }
        for c in wsserver.clients:
            c.write_message(json.dumps(frame, indent=4, sort_keys=True, default=str))         
        
    def start_light_all_off(self):
        LED_RED1.off()
        LED_RED2.off()
        LED_RED3.off()
        LED_RED4.off()
        LED_RED5.off()
        LED_GREEN.off()  
        LED_YELLOW.off()         
        
    def start_light_yellow_flag_on(self):
        LED_GREEN.off()
        LED_YELLOW.blink(0.3, 0.3)  

    def start_light_yellow_flag_off(self):
        LED_GREEN.on()
        LED_YELLOW.off()
        
    def blink_lane(self, lane):
        if (lane == 1):
            LED_RED1.blink(0.1, 0.1, 1) # single blink
        elif (lane == 2): 
            LED_RED5.blink(0.1, 0.1, 1) # single blink
            
    def show_winner(self, lane):
        LED_GREEN.off()  
        LED_YELLOW.on()  
        if (lane == 1):
            LED_RED1.on()
        elif (lane == 2):                 
            LED_RED5.on()
            
    def show_laps_setting(self, value):
        if (value == 1):
            LED_RED1.blink(0.5, 0.5, 1)
        elif (value == 2):
            LED_RED1.blink(0.5, 0.5, 1)
            LED_RED2.blink(0.5, 0.5, 1)
        elif (value == 3):
            LED_RED1.blink(0.5, 0.5, 1)
            LED_RED2.blink(0.5, 0.5, 1)
            LED_RED3.blink(0.5, 0.5, 1)
        elif (value == 4):
            LED_RED1.blink(0.5, 0.5, 1)
            LED_RED2.blink(0.5, 0.5, 1)
            LED_RED3.blink(0.5, 0.5, 1)                
            LED_RED4.blink(0.5, 0.5, 1)
        elif (value == 5):
            LED_RED1.blink(0.5, 0.5, 1)
            LED_RED2.blink(0.5, 0.5, 1)
            LED_RED3.blink(0.5, 0.5, 1)
            LED_RED4.blink(0.5, 0.5, 1)                
            LED_RED5.blink(0.5, 0.5, 1)        
            
racecontrol_hardware = RaceControlHardware()
           

class RaceControlStatus(object):
    # Status constants
    OFF = 0     
    PRE_START = 1
    START = 2
    RACE = 3
    FINISH = 4
    YELLOW_FLAG = 5
    FALSE_START = 6  
    MODE_RACE = 0
    MODE_PRACTICE = 1
    
    def __init__(self):
        self.__race_state = self.OFF
        
    @property
    def race_state(self):
        return self.__race_state
    
    @race_state.setter
    def race_state(self, value):
        self.__race_state = value          
    
racecontrol_status = RaceControlStatus()


class RaceControl(object):
    def __init__(self):
        self.__laps_list = []                
        self.__start_button_pressed = False                     
        self.__laps = 10
        self.__laps_max = 50    
        self.__lane1_start_time = 0
        self.__lane1_lapcount = 0
        self.__lane1_last_lap_time = datetime.timedelta(0)
        self.__lane1_best_lap = 0
        self.__lane1_best_lap_time = datetime.timedelta(0)
        self.__lane1_total_lap_time = datetime.timedelta(0)
        self.__lane2_start_time = 0
        self.__lane2_lapcount = 0 
        self.__lane2_last_lap_time = datetime.timedelta(0) 
        self.__lane2_best_lap = 0  
        self.__lane2_best_lap_time = datetime.timedelta(0)
        self.__lane2_total_lap_time = datetime.timedelta(0)     
        
    @property
    def laps_list(self):
        return self.__laps_list
    
    @laps_list.setter
    def laps_list(self, value):
        self.__laps_list = value      
    
    @property
    def start_button_pressed(self):
        return self.__start_button_pressed
    
    @start_button_pressed.setter
    def start_button_pressed(self, value):
        self.__start_button_pressed = value    
        
    @property
    def laps(self):
        return self.__laps
    
    @laps.setter
    def laps(self, value):
        self.__laps = value  
        
    @property
    def laps_max(self):
        return self.__laps_max
    
    @laps_max.setter
    def laps_max(self, value):
        self.__laps_max = value          
        
    @property
    def lane1_start_time(self):
        return self.__lane1_start_time
    
    @lane1_start_time.setter
    def lane1_start_time(self, value):
        self.__lane1_start_time = value     
        
    @property
    def lane1_lapcount(self):
        return self.__lane1_lapcount
    
    @lane1_lapcount.setter
    def lane1_lapcount(self, value):
        self.__lane1_lapcount = value   
        
    @property
    def lane1_last_lap_time(self):
        return self.__lane1_last_lap_time
    
    @lane1_last_lap_time.setter
    def lane1_last_lap_time(self, value):
        self.__lane1_last_lap_time = value          
        
    @property
    def lane1_best_lap_time(self):
        return self.__lane1_best_lap_time
    
    @lane1_best_lap_time.setter
    def lane1_best_lap_time(self, value):
        self.__lane1_best_lap_time = value     

    @property
    def lane1_best_lap(self):
        return self.__lane1_best_lap
    
    @lane1_best_lap.setter
    def lane1_best_lap(self, value):
        self.__lane1_best_lap = value

    @property
    def lane1_total_lap_time(self):
        return self.__lane1_total_lap_time
    
    @lane1_total_lap_time.setter
    def lane1_total_lap_time(self, value):
        self.__lane1_total_lap_time = value               
                
    @property
    def lane2_start_time(self):
        return self.__lane2_start_time
    
    @lane2_start_time.setter
    def lane2_start_time(self, value):
        self.__lane2_start_time = value     
        
    @property
    def lane2_lapcount(self):
        return self.__lane2_lapcount
    
    @lane2_lapcount.setter
    def lane2_lapcount(self, value):
        self.__lane2_lapcount = value  

    @property
    def lane2_last_lap_time(self):
        return self.__lane2_last_lap_time
    
    @lane2_last_lap_time.setter
    def lane2_last_lap_time(self, value):
        self.__lane2_last_lap_time = value    
      
    @property
    def lane2_best_lap_time(self):
        return self.__lane2_best_lap_time
    
    @lane2_best_lap_time.setter
    def lane2_best_lap_time(self, value):
        self.__lane2_best_lap_time = value     

    @property
    def lane2_best_lap(self):
        return self.__lane2_best_lap
    
    @lane2_best_lap.setter
    def lane2_best_lap(self, value):
        self.__lane2_best_lap = value   

    @property
    def lane2_total_lap_time(self):
        return self.__lane2_total_lap_time
    
    @lane2_total_lap_time.setter
    def lane2_total_lap_time(self, value):
        self.__lane2_total_lap_time = value   

    def _get_diff_str(self, diff_lapcount):
        diff_str = ""   
        if diff_lapcount > 1:                
            diff_str = "+" + str(diff_lapcount) + " laps"
        elif diff_lapcount > 0:
            diff_str = "+" + str(diff_lapcount) + " lap"                    
        return diff_str
    
    def add_lap_to_list(self, value):
        self.__laps_list.append(value)

    def check_position_in_race(self, lane):
        retval = 0        
        if lane == 1:
            if self.__lane1_lapcount > self.__lane2_lapcount:
                retval = 1
            else:
                retval = 2
        elif lane == 2:
            if self.__lane2_lapcount > self.__lane1_lapcount:
                retval = 1
            else:
                retval = 2        
        # equal
        else:
            retval = 1
            
        return retval
                
    def send_lap_time(self, lane, lap, lap_time):                          
        # Get position in race
        position = self.check_position_in_race(lane)        
        # Send lap time data to websocket clients         
        frame = {'frame_type': 1, 'lane': lane, 'lap': lap, 'time': lap_time, 'position': position } 
        #print("Sent to websocket clients: " + json.dumps(frame, indent=4, sort_keys=True, default=str))
        asyncio.set_event_loop(asyncio.new_event_loop())
        for c in wsserver.clients:
            c.write_message(json.dumps(frame, indent=4, sort_keys=True, default=str))
        
    def send_positions_to_clients(self):           
        asyncio.set_event_loop(asyncio.new_event_loop())          
        # Check positions
        if self.__lane1_lapcount > self.__lane2_lapcount:
            # Lane 1 has first position
            # calc difference with pos 2
            diff_lapcount = self.__lane1_lapcount - self.__lane2_lapcount    
            
            # build json data
            json_pos1 = '"position1": { "lane": 1, "lap": '+str(self.__lane1_lapcount)+', "time": "'+str(self.__lane1_last_lap_time)+'", "best_lap": '+str(self.__lane1_best_lap)+', "best_lap_time": "'+str(self.__lane1_best_lap_time)+'", "total_lap_time": "'+str(self.__lane1_total_lap_time)+'", "diff_lapcount": ""}'           
            json_pos2 = '"position2": { "lane": 2, "lap": '+str(self.__lane2_lapcount)+', "time": "'+str(self.__lane2_last_lap_time)+'", "best_lap": '+str(self.__lane2_best_lap)+', "best_lap_time": "'+str(self.__lane2_best_lap_time)+'", "total_lap_time": "'+str(self.__lane2_total_lap_time)+'", "diff_lapcount": "'+str(diff_lapcount)+'"}'
            json_data = '{"positions": { '+json_pos1+','+json_pos2+'} }' 

            #print("Sent to websocket clients: " + json_data)
            for c in wsserver.clients:
                c.write_message(json_data)     
             
        elif self.__lane1_lapcount < self.__lane2_lapcount:
            # Lane 2 has first position
            # calc difference with pos 1
            diff_lapcount = self.__lane2_lapcount - self.__lane1_lapcount
            
            # build json data
            json_pos1 = '"position1": { "lane": 2, "lap": '+str(self.__lane2_lapcount)+', "time": "'+str(self.__lane2_last_lap_time)+'", "best_lap": '+str(self.__lane2_best_lap)+', "best_lap_time": "'+str(self.__lane2_best_lap_time)+'", "total_lap_time": "'+str(self.__lane2_total_lap_time)+'", "diff_lapcount": ""}' 
            json_pos2 = '"position2": { "lane": 1, "lap": '+str(self.__lane1_lapcount)+', "time": "'+str(self.__lane1_last_lap_time)+'", "best_lap": '+str(self.__lane1_best_lap)+', "best_lap_time": "'+str(self.__lane1_best_lap_time)+'", "total_lap_time": "'+str(self.__lane1_total_lap_time)+'", "diff_lapcount": "'+str(diff_lapcount)+'"}'                       
            json_data = '{"positions": { '+json_pos1+','+json_pos2+'} }'                        
        
            #print("Sent to websocket clients: " + json_data)
            for c in wsserver.clients:
                c.write_message(json_data)   
        
        else:
            # skip if both lanes have equal lap counts
            if (self.__lane1_lapcount and self.__lane2_lapcount):
                # Equal lap count, use total_lap_time  
                if (self.__lane1_total_lap_time < self.__lane2_total_lap_time):
                    # build json data
                    json_pos1 = '"position1": { "lane": 1, "lap": '+str(self.__lane1_lapcount)+', "time": "'+str(self.__lane1_last_lap_time)+'", "best_lap": '+str(self.__lane1_best_lap)+', "best_lap_time": "'+str(self.__lane1_best_lap_time)+'", "total_lap_time": "'+str(self.__lane1_total_lap_time)+'", "diff_lapcount": ""}'           
                    json_pos2 = '"position2": { "lane": 2, "lap": '+str(self.__lane2_lapcount)+', "time": "'+str(self.__lane2_last_lap_time)+'", "best_lap": '+str(self.__lane2_best_lap)+', "best_lap_time": "'+str(self.__lane2_best_lap_time)+'", "total_lap_time": "'+str(self.__lane2_total_lap_time)+'", "diff_lapcount": ""}'
                    json_data = '{"positions": { '+json_pos1+','+json_pos2+'} }'                                         
                else:
                    # build json data
                    json_pos1 = '"position1": { "lane": 2, "lap": '+str(self.__lane2_lapcount)+', "time": "'+str(self.__lane2_last_lap_time)+'", "best_lap": '+str(self.__lane2_best_lap)+', "best_lap_time": "'+str(self.__lane2_best_lap_time)+'", "total_lap_time": "'+str(self.__lane2_total_lap_time)+'", "diff_lapcount": ""}'
                    json_pos2 = '"position2": { "lane": 1, "lap": '+str(self.__lane1_lapcount)+', "time": "'+str(self.__lane1_last_lap_time)+'", "best_lap": '+str(self.__lane1_best_lap)+', "best_lap_time": "'+str(self.__lane1_best_lap_time)+'", "total_lap_time": "'+str(self.__lane1_total_lap_time)+'", "diff_lapcount": ""}'                       
                    json_data = '{"positions": { '+json_pos1+','+json_pos2+'} }'                      
                
                print("Sent to websocket clients: " + json_data)
                for c in wsserver.clients:
                    c.write_message(json_data)                    
                
    def send_status_to_clients(self):           
        frame = {'frame_type': 0, 'race_state': racecontrol_status.race_state, 'race_laps': self.__laps }        
        asyncio.set_event_loop(asyncio.new_event_loop())
        for c in wsserver.clients:
            c.write_message(json.dumps(frame, indent=4, sort_keys=True, default=str))
                        
    def reset_race(self):
        # reset state and lights
        racecontrol_status.race_state = racecontrol_status.OFF
        racecontrol_hardware.start_light_all_off()        
        # reset some vars
        self.__laps_list = []    
        self.__lane1_start_time = 0
        self.__lane1_lapcount = 0
        self.__lane1_last_lap_time = datetime.timedelta(0)
        self.__lane1_total_lap_time = datetime.timedelta(0)
        self.__lane1_best_lap_time = datetime.timedelta(0)
        self.__lane2_start_time = 0
        self.__lane2_lapcount = 0 
        self.__lane2_last_lap_time = datetime.timedelta(0)
        self.__lane2_total_lap_time = datetime.timedelta(0)  
        self.__lane2_best_lap_time = datetime.timedelta(0)             
        # inform clients    
        self.send_status_to_clients() 
        print("Race reset!")    
        print("Press start button to start race with " + str(self.__laps) + " laps")         
            
    def incr_race_laps(self):
        if racecontrol_status.race_state == racecontrol_status.OFF:
            if (self.__laps < self.__laps_max):
                self.__laps += 10
            else:
                self.__laps = 10                  
            value = self.__laps / 10
            racecontrol_hardware.show_laps_setting(value);                        
            self.send_status_to_clients();
            print("Race changed, press start button to start race with " + str(self.__laps) + " laps")
            
        else:
            print("Cannot change laps while race is started or in progress!")  

racecontrol_obj = RaceControl()
