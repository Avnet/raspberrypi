"""
PI HAT FLOW SENSOR DEMO

   Contributors:
     * Fred Kellerman

   Licensed under the Apache License, Version 2.0 (the "License"); 
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, 
   software distributed under the License is distributed on an 
   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
   either express or implied. See the License for the specific 
   language governing permissions and limitations under the License.
"""

import sys
import httplib
import json
from sense_emu import SenseHat 

# Base parameters used to connect to the FLOW demo
FLOW_SERVER_URL = "run-west.att.io"
FLOW_BASE_URL = "/1e464b19cdcde/774c88d68202/86694923d5bf28a/in/flow"
FLOW_INPUT_NAME = "/climate"
FLOW_DEVICE_NAME = "vstarterkit001"
FLOW_URL_TYPE = " HTTP/1.1\r\nHost: "

sense = SenseHat()
oldrow = 0
oldcol = 0
while 1 :
    for row in range(0,8) :
        for col in range(0,8) :
            print "row:", row, "col:", col
            # Read PI HAT Sensor data to send to the Flow program via an http get request
            tempstr = str(sense.temp)
            humiditystr = str(sense.humidity)
            orientation = sense.get_orientation()
            accelZstr = str(orientation["pitch"])
            accelYstr = str(orientation["roll"])
            accelXstr = str(orientation["yaw"])

            # This is the GET request body, it will be parsed by the Flow server and a response will be given in the form of a JSON string with a color
            getflow = FLOW_BASE_URL + FLOW_INPUT_NAME + "?serial=" + FLOW_DEVICE_NAME + \
                      "&temp=" + tempstr + "&humidity=" + humiditystr + "&accelX=" + accelXstr + "&accelY=" + accelYstr + "&accelZ=" + accelZstr + \
                      " " + FLOW_URL_TYPE + FLOW_SERVER_URL + "\r\n\r\n"
            # Echo the string so you can see what is going on 
            print getflow

            # Connect to the Flow server and send the request
            conn = httplib.HTTPSConnection(FLOW_SERVER_URL)
            conn.request("GET", getflow)

            # Wait and obtain the response from the server
            reply = conn.getresponse()
            replystr = reply.read()
            # Close the socket
            conn.close()

            # Echo whether the server accepted the GET request
            print "Server reply status:", reply.status, reply.reason
            # Echo the response the server gave
            print "Server response:", replystr

            if reply.reason == "Accepted" :
                # Parse out the LED color from the json string
                parsedjson = json.loads(replystr)
                ledcolor   = parsedjson["LED"]

                # The Flow program will only send back the following LED colors:
                #     OFF, RED, GREEN, YELLOW, BLUE, MAGENTA, TURQUOISE, WHITE
                # Convert these colors to the Pi HAT LED colors
                if ledcolor == "OFF" :
                    rgbLED = [0, 0, 0]
                elif ledcolor == "RED" :
                    rgbLED = [255, 0, 0]
                elif ledcolor == "GREEN" :
                    rgbLED = [0, 255, 0]
                elif ledcolor == "YELLOW" :
                    rgbLED = [255, 255, 0]
                elif ledcolor == "BLUE" :
                    rgbLED = [0, 0, 255]
                elif ledcolor == "MAGENTA" :
                    rgbLED = [255, 0, 255]
                elif ledcolor == "TURQUOISE" :
                    rgbLED = [0, 255, 255]
                elif ledcolor == "WHITE" :
                    rgbLED = [255, 255, 255]
                else :
                    rgbLED = [0, 0, 0]

                #Echo out parsed color
                print "LED color:", ledcolor, rgbLED
                sense.set_pixel(oldcol, oldrow, [0,0,0])
                sense.set_pixel(col, row, rgbLED)
                oldrow = row
                oldcol = col
