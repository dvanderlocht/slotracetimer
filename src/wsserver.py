###########################################################################   
#
# Description: Websocket server classes for use in slotracetimer, used for
#              comm interfacing through a websocket with the web-based GUI
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

import tornado.web
import tornado.websocket
import json

from racecontrol import racecontrol_status, racecontrol_obj

clients = []

class WebServer(tornado.web.Application):
    def __init__(self):
        handlers = [ (r"/", IndexHandler), 
                     (r'/ws', SocketHandler), ]
        settings = {'debug': True}
        super().__init__(handlers, **settings)

    def run(self, port=8888):
        self.listen(port)
        io_loop = tornado.ioloop.IOLoop.current()
        io_loop.start()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class SocketHandler(tornado.websocket.WebSocketHandler):    
    def check_origin(self, origin):
        return True

    def open(self):
        clients.append(self)
        # send initial race_state info
        frame = {'frame_type': 0, 'race_state': racecontrol_status.race_state, 'race_laps': racecontrol_obj.laps} 
        self.write_message(json.dumps(frame, indent=4, sort_keys=True, default=str))
        # send current laps info 
        for lap in racecontrol_obj.laps_list:
            print(lap)                        
            time = lap[2]        
            position = lap[3]
            lane = lap[0]
            lap = lap[1]            
            frame = {'frame_type': 1, 'lane': lane, 'lap': lap, 'time': time, 'position': position}               
            self.write_message(json.dumps(frame, indent=4, sort_keys=True, default=str))
        
        # send position
        racecontrol_obj.send_positions_to_clients()       
        
        print("Websocket client connected")

    def on_message(self, message):
        print("Websocket received: " + message)
        
    def on_close(self):
        clients.remove(self)
        print("Websocket client disconnected")
        
    def send_frame(self, frame):
        for c in clients:
            c.write_message(frame)

        
class ApiHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, *args):
        self.finish()
        myid = self.get_argument("id")
        value = self.get_argument("value")
        data = {"id": myid, "value" : value}
        data = json.dumps(data)
        for c in clients:
            c.write_message(data)

    @tornado.web.asynchronous
    def post(self):
        pass
