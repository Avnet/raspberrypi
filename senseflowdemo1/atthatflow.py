#!/usr/bin/python

"""
PI HAT FLOW SENSOR DEMO!!!

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

import time
import sys
import subprocess 
import httplib
import json

def print_usage() :
    print
    print 'usage: atthatflow.py [emu_cell | noemu_cell | emu_nocell | noemu_nocell]'
    print
    print 'If no command lines then default is virtual sense hat and no cellular modem'
    print
    print '    emu_cell = Use Virtual Sense Emulator and Cellular WNC modem'
    print '    noemu_cell = Use real Sense Emulator and Cellular WNC modem'
    print '    emu_nocell = Use Virtual Sense Emulator and use other internet connection'
    print '    moemu_nocell = Use real Sense Emulator and use other internet connection'
    print

# Parse command line input:
if len(sys.argv) == 1 :
    # Make True if you would like to use the GUI Sense Hat Emulator instead of the real one
    USE_VIRTUAL_SENSE_HAT = False
    # If you have an ethernet connection make this false, if you want to use the cellular modem make true
    USE_CELL_MODEM = True
elif len(sys.argv) == 2 :
    if sys.argv[1] == '--help' :
        print_usage()
        exit(0)
    elif sys.argv[1] == 'emu_cell' :
        USE_VIRTUAL_SENSE_HAT = True
        USE_CELL_MODEM = True
    elif sys.argv[1] == 'noemu_cell' :
        USE_VIRTUAL_SENSE_HAT = False
        USE_CELL_MODEM = True
    elif sys.argv[1] == 'emu_nocell' :
        USE_VIRTUAL_SENSE_HAT = True
        USE_CELL_MODEM = False
    elif sys.argv[1] == 'noemu_nocell' :
        USE_VIRTUAL_SENSE_HAT = False
        USE_CELL_MODEM = False
else:
    print_usage()
    exit(0)

if USE_CELL_MODEM == True :
    import serial
    from bars import AtCellModem_14A2A
    
if USE_VIRTUAL_SENSE_HAT == False :
    from sense_hat import SenseHat
else :
    from sense_emu import SenseHat


######################################################
#  A few setup items:
######################################################
    
# Base parameters used to connect to the FLOW demo
FLOW_SERVER_URL1 = 'runm-east.att.io'
FLOW_BASE_URL1 = '/ce323678bacc7/d235133ae3dc/0e68c11f947776c/in/flow'
FLOW_INPUT_NAME1 = "/climate"
MAX_NUM_SENSORS = 8
MAX_NUM_SENSE_ROWS = 8
REBOOT_HOLD_TIME = 10
NUM_POSITION_READINGS_AVG = 1
DISCONNECTED_LED_RGB_HTTP = [64, 0, 0]
DISCONNECTED_LED_RGB = [64, 64, 64]
UART_READ_TIMEOUT_SECS = 2
WATCHDOG_CNT_MAX = 10
HTTP_CONNECTION_TIMEOUT = 10
FIRMWARE_PATH = '/home/pi/senseflowdemo1'

# Assign server based upon selected ID
UrlById = [FLOW_SERVER_URL1,
           FLOW_SERVER_URL1,
           FLOW_SERVER_URL1,
           FLOW_SERVER_URL1,
           FLOW_SERVER_URL1,
           FLOW_SERVER_URL1,
           FLOW_SERVER_URL1,
           FLOW_SERVER_URL1]

FlowPathById = [FLOW_BASE_URL1 + FLOW_INPUT_NAME1,
                FLOW_BASE_URL1 + FLOW_INPUT_NAME1,
                FLOW_BASE_URL1 + FLOW_INPUT_NAME1,
                FLOW_BASE_URL1 + FLOW_INPUT_NAME1,
                FLOW_BASE_URL1 + FLOW_INPUT_NAME1,
                FLOW_BASE_URL1 + FLOW_INPUT_NAME1,
                FLOW_BASE_URL1 + FLOW_INPUT_NAME1,
                FLOW_BASE_URL1 + FLOW_INPUT_NAME1]
              

def display_bars(bars, sense_hat):    
    if bars < 1 :
        bars = 0
        f = [255,0,0]
    else :
        f = [0,0,255]
        
    b = [0,0,0]

    if bars == 0 :
        rgb_pixels = \
        [b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         f,b,b,b,b,b,b,b]
    elif bars == 1 :
        rgb_pixels = \
        [b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,f,b,b,b,b,b,b,
         b,f,b,b,b,b,b,b]
    elif bars == 2 :
        rgb_pixels = \
        [b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,b,b,f,b,b,b,b,
         b,b,b,f,b,b,b,b,
         b,f,b,f,b,b,b,b,
         b,f,b,f,b,b,b,b]
    elif bars == 3 :
        rgb_pixels = \
        [b,b,b,b,b,b,b,b,
         b,b,b,b,b,b,b,b,
         b,b,b,b,b,f,b,b,
         b,b,b,b,b,f,b,b,
         b,b,b,f,b,f,b,b,
         b,b,b,f,b,f,b,b,
         b,f,b,f,b,f,b,b,
         b,f,b,f,b,f,b,b]
    else :
        rgb_pixels = \
        [b,b,b,b,b,b,b,f,
         b,b,b,b,b,b,b,f,
         b,b,b,b,b,f,b,f,
         b,b,b,b,b,f,b,f,
         b,b,b,f,b,f,b,f,
         b,b,b,f,b,f,b,f,
         b,f,b,f,b,f,b,f,
         b,f,b,f,b,f,b,f]

    sense_hat.clear()
    sense_hat.set_pixels(rgb_pixels)

def display_mdm_bars(mdm, sense_hat):
    bars = mdm.calc_rx_bars(1)  # Danger danger, leave at 1, 14A2A can't handle back to back
    display_bars(bars, sense_hat)
    
def wait_for_at_ok(mdm, sense_hat, debug=False) :
    sense_hat.show_message("Wait for AT OK", scroll_speed = 0.03, text_colour = [255, 0, 0])
    cnt = 0
    while 1:
        result, resp = mdm.send_mdm_cmd('AT', timeout=1)
        sense_hat.show_message(".", scroll_speed = 0.01, text_colour = [255, 0, 0])
        if result == True :
           cnt += 1
        if cnt >= 4 :
            sense_hat.show_message("AT OK", scroll_speed = 0.03, text_colour = [255, 0, 0])
            break
    
######### Program begin

sense = SenseHat()

if USE_CELL_MODEM == True :
    # Try to find something in serial ACM0 or AMC1
    while 1 :
        try :
            uart = serial.Serial('/dev/ttyACM0', 115200, timeout=UART_READ_TIMEOUT_SECS)
            break
        except KeyboardInterrupt:
            exit(-1)
        except:
            try :
                uart = serial.Serial('/dev/ttyACM1',115200, timeout=UART_READ_TIMEOUT_SECS)
                break
            except KeyboardInterrupt:
                exit(-1)
            except:
                sense.show_message("Unable to talk to Modem", scroll_speed = 0.05, text_colour = [255, 0, 0])
                sense.show_message("Recheck USB...", scroll_speed = 0.05, text_colour = [255, 0, 0])

if USE_CELL_MODEM == True :
    # Attempt open close
    for n in range(20, 1, -1):
            uart.close()
            uart.open()
            if uart.isOpen() == True :
                sense.show_message(uart.name, scroll_speed = 0.03, text_colour = [255, 0, 0])         
                break;
            else :
                sense.show_message("Wait Mdm Serial " + str(n), scroll_speed = 0.03, text_colour = [255, 0, 0])

    print(uart.name)

# Create AT modem controller object, validate serial with modem type
if USE_CELL_MODEM == True :
    at_mdm = AtCellModem_14A2A(uart, timeout=UART_READ_TIMEOUT_SECS) #, dbgFileName = '/home/pi/at.log')
    no_type = True
    while no_type == True :
        sense.show_message("Type: " + str(at_mdm.modem_type), scroll_speed = 0.03, text_colour = [255, 0, 0])
        at_mdm.get_version()
        no_type = (at_mdm.modem_type == 'None') or (at_mdm.modem_type == 'command')
        if (at_mdm.modem_type == 'command') :
            sense.show_message("FAIL: modem in serial debug mode, power cycle and reconnect modem!", scroll_speed = 0.03, text_colour = [255, 0, 0])        

    # Wait for a few AT OKs, wait until.
    wait_for_at_ok(at_mdm, sense)

# Enter Setup Mode, select the ID
while 1 :
    if USE_CELL_MODEM == True :
        # Poll mdm with AT commands to see if we're connected and measure signal strength
        idIsNotDone = 1 
        while idIsNotDone == 1 :
            # Show bars
            #print 'Update bars'
            display_mdm_bars(at_mdm, sense)
            for button_events in sense.stick.get_events() :
                if (button_events.direction == "middle") :
                    idIsNotDone = 0
            # 14A2A cannot handle just hitting it hard with read signal strength
            # It messes up the AT command response from the modem
            time.sleep(.3)
    
    # Handle possible double push
    time.sleep(.3)
    for button_events in sense.stick.get_events() : dummy = 1
        
    # Gather user input for setting serial device name
    id = 1
    sense.show_letter(str(id), text_colour = [255,0,0], back_colour = [0,0,255])
    idIsNotDone = 1 
    while idIsNotDone == 1 :
        for button_events in sense.stick.get_events() :
            if (button_events.action == "pressed") :
                if (button_events.direction == "down" or button_events.direction == "right") :
                     id -= 1
                if (button_events.direction == "up" or button_events.direction == "left") :
                     id += 1
                if (id > MAX_NUM_SENSORS) :
                     id = 1
                if (id < 1) :
                     id = MAX_NUM_SENSORS 
                if (button_events.direction == "middle") :
                    idIsNotDone = 0 
            sense.show_letter(str(id), text_colour = [255,0,0], back_colour = [0,0,255])
    
    if (id > 99) :
        serialName = "SenseHat" + str(id)    
    if (id > 9) :
        serialName = "SenseHat0" + str(id)    
    else :
        serialName = "SenseHat00" + str(id)        

    sense.clear()
    for button_events in sense.stick.get_events() : tmp = 1 # Empty Event Queue
    reboot_pi_timer = time.time() # Initialize the variable, cause a push and hold causes trouble
    sig_display = False
    mdm_rsrp = mdm_rssi = 0
    bars_on = False
    blank_pos = 0
    WatchDogCnt = 0

    if USE_CELL_MODEM == True :    
        # Try to make the IP traffic use the cellular modem which should which show up as eth1 
        subprocess.call("sudo route add default eth1", shell=True)
    
    # Poll the sense hat and report the results to the Flow server
    # Wait for server reply and update LED Matrix with the results
    while 1 :
        if USE_CELL_MODEM == True :
            # Poll mdm with AT commands to see if we're connected to the celluar network
            if at_mdm.uart.isOpen() == True :
                mdm_connected = at_mdm.is_on_network()
                mdm_rsrp = at_mdm.read_rsrp()
                mdm_rssi = at_mdm.read_rssi()
            else :
                at_mdm.uart.close()
                try :
                    at_mdm.uart = serial.Serial('/dev/ttyACM0',115200, timeout=UART_READ_TIMEOUT_SECS)
                    sense.show_message('/dev/ttyACM0', scroll_speed = 0.05, text_colour = [255, 0, 0])
                    wait_for_at_ok(at_mdm, sense)
                except KeyboardInterrupt:
                    exit(-1)
                except:
                    try:
                        at_mdm.uart = serial.Serial('/dev/ttyACM1',115200, timeout=UART_READ_TIMEOUT_SECS)
                        sense.show_message('/dev/ttyACM1', scroll_speed = 0.05, text_colour = [255, 0, 0])
                        wait_for_at_ok(at_mdm, sense)                        
                    except KeyboardInterrupt:
                        exit(-1)
                    except:
                        sense.show_message("Unable to open Serial", scroll_speed = 0.05, text_colour = [255, 0, 0])                    
                mdm_connected = False
                mdm_rsrp = mdm_rssi = 0
                # Try to make the IP traffic use the cellular modem which should which show up as eth1 
                subprocess.call("sudo route add default eth1", shell=True)
        else :
            mdm_rsrp = mdm_rssi = 0
            mdm_connected = True
        
        # Read PI HAT Sensor data to send to the Flow program via an http get request
        tempstr = str(round(sense.temp))
        humiditystr = str(round(sense.humidity))
        pressurestr = str(round(sense.pressure))
        accelZ = accelY = accelX = 0 
        for i in range(1, NUM_POSITION_READINGS_AVG + 1) :
            orientation = sense.get_gyroscope()
            accelZ += -180 + orientation["pitch"]
            accelY += -180 + orientation["roll"]
            accelX += -180 + orientation["yaw"]
        accelXstr = str(round(accelX/i))
        accelYstr = str(round(accelY/i))
        accelZstr = str(round(accelZ/i))
        #print accelXstr, accelYstr, accelZstr 

        # Button time!
        button1 = button2 = button3 = button4 = button5 = "0"
        buttons = sense.stick.get_events() 
        for button_events in buttons :
            #print button_events.action
            #print button_events.direction
            if button_events.action == "pressed" : 
                button1 = "1" if button_events.direction == "up" else "0"
                button2 = "1" if button_events.direction == "down" else "0"
                button3 = "1" if button_events.direction == "left" else "0"
                button4 = "1" if button_events.direction == "right" else "0"
                button5 = "1" if button_events.direction == "middle" else "0"
                reboot_pi_timer = time.time() 
            if button_events.action == "held" :
                if button_events.direction == "middle" :
                    if (time.time() - reboot_pi_timer) > REBOOT_HOLD_TIME :
                        sense.clear()                    
                        subprocess.call("sudo reboot &", shell=True)
                        while 1 : a = 1 

        # This is the GET request body, it will be parsed by the Flow server and a response will be given in the form of a JSON string with a color
        getflow = FlowPathById[id - 1] + \
                  "?serial=" + serialName + \
                  "&measuredTempC=" + tempstr + \
                  "&measuredHumidity=" + humiditystr + \
                  "&measuredAccelX=" + accelXstr + \
                  "&measuredAccelY=" + accelYstr + \
                  "&measuredAccelZ=" + accelZstr + \
                  "&inBtn1=" + button1 + \
                  "&inBtn2=" + button2 + \
                  "&inBtn3=" + button3 + \
                  "&inBtn4=" + button4 + \
                  "&inBtn5=" + button5 + \
                  "&rssi=" + str(mdm_rssi)  + \
                  "&rsrp=" + str(mdm_rsrp) + \
                  "&measuredPressure=" + pressurestr 
    
        # Echo the string so you can see what is going on 
        #print "HTTP GET:"
        #print getflow

        httpSuccess = False        
        # Connect to the Flow server and send the request
        try :
            conn = httplib.HTTPSConnection(UrlById[id-1], timeout = HTTP_CONNECTION_TIMEOUT)
            try :
                conn.request("GET", getflow)
                # Wait and obtain the response from the server
                reply = conn.getresponse()
                replystr = reply.read()
                # Close the socket
                conn.close()
                httpSuccess = True
            except KeyboardInterrupt :
                exit(-1)
            except httplib.HTTPException:
                sense.show_message("HTTP response/close Exception ", scroll_speed = 0.04, text_colour = [255, 0, 0])            
                try :
                    conn.close()
                except KeyboardInterrupt :
                    exit(-1)
                except :
                    sense.show_message("HTTP close Exception ", scroll_speed = 0.04, text_colour = [255, 0, 0])                
            except :
                sense.show_message("HTTP general ERR1 ", scroll_speed = 0.04, text_colour = [255, 0, 0])
        except KeyboardInterrupt:
            exit(1)
        except httplib.HTTPException:
            sense.show_message("HTTP open Exception ", scroll_speed = 0.04, text_colour = [255, 0, 0])                
        except :
            sense.show_message("HTTP general ERR2 ", scroll_speed = 0.04, text_colour = [255, 0, 0])            

        if httpSuccess == False or mdm_connected == False :
            pixels = sense.get_pixels()
            if httpSuccess == False :
                led_rgb = DISCONNECTED_LED_RGB_HTTP
            else :
                led_rgb = DISCONNECTED_LED_RGB
            for r in range(0,64,8) :
                pixels[r] = led_rgb
            sense.set_pixels(pixels)

        # Echo whether the server accepted the GET request
        #print "Server http reply:", reply.status, reply.reason
        # Echo the response the server gave
        #print "Server response:", replystr
    
        if httpSuccess == True :
            if reply.reason == "Accepted" :
                WatchDogCnt = 0

                # Parse out the LED color from the json string
                parsedjson = json.loads(replystr)

                # Check for cmd
                action = parsedjson['action']
                if action != 'none' :
                    print action
                if action == 'update' :
                    sense.show_message("Firmware update begin...", scroll_speed = 0.03, text_colour = [255, 0, 0])
                    subprocess.call("wget -P " + FIRMWARE_PATH + " www.fredkellerman.com/atthatflow.py", shell=True)
                    subprocess.call("wget -P " + FIRMWARE_PATH + " www.fredkellerman.com/bars.py", shell=True)
                    subprocess.call("chmod 0700 " + FIRMWARE_PATH + "/bars.py.1", shell=True)
                    subprocess.call("chmod 0700 " + FIRMWARE_PATH + "/atthatflow.py.1", shell=True)
                    subprocess.call("mv " + FIRMWARE_PATH + "/bars.py.1 " + FIRMWARE_PATH + "/bars.py", shell=True)
                    subprocess.call("mv " + FIRMWARE_PATH + "/atthatflow.py.1 " + FIRMWARE_PATH + "/atthatflow.py", shell=True)
                    sense.show_message("Firmware update complete!", scroll_speed = 0.03, text_colour = [255, 0, 0])
                if action == 'reboot' :
                    subprocess.call("sudo shutdown -r now &", shell=True)
                    sense.clear()
                    while (1) : a = 1
                if action == 'shutdown' :
                    subprocess.call("sudo shutdown now &", shell=True)
                    sense.clear()              
                    while (1) : a = 1
                if action == 'reset' :
                    break
                if action == 'hi' :
                    hiMsg = 'Heat Index: ' + parsedjson['computedHeatIndexC'] + 'C'
                    sense.show_message(hiMsg, scroll_speed = 0.05, text_colour = [255, 255, 0])
                if action == 'signalon' :
                    bars_on = True
                if action == 'signaloff' :
                    bars_on = False

                # Move a dot at the rate of the FLOW responses
                blank_pos = (blank_pos + 1) % 8

                # Check the mailbox
                msg = parsedjson["MSG"]
                if msg != "" :
                    sense.show_message(msg, scroll_speed = 0.05, text_colour = [255, 255, 0], back_colour = [0, 0, 128])

                # Signal bars if turned on else colored rows
                if bars_on == True :
                    if USE_CELL_MODEM == True :
                        display_mdm_bars(at_mdm, sense)
                    else :
                        display_bars(-1, sense)
                else:
                    rgbLEDs = []
                    for i in range(0, min(MAX_NUM_SENSORS,MAX_NUM_SENSE_ROWS)) :
                        rLedColor = int(parsedjson["R" + str(i % MAX_NUM_SENSE_ROWS + 1)])
                        gLedColor = int(parsedjson["G" + str(i % MAX_NUM_SENSE_ROWS + 1)])
                        bLedColor = int(parsedjson["B" + str(i % MAX_NUM_SENSE_ROWS + 1)])
                        rgbLEDRow = [[rLedColor, gLedColor, bLedColor]]
                        rgbLEDRow *= 8
                        if mdm_connected == False :
                           rgbLEDRow[0] = DISCONNECTED_LED_RGB
                        if i == ((id - 1) % MAX_NUM_SENSE_ROWS) :
                            rgbLEDRow[blank_pos] = [0,0,0]
                            rgbLEDRow[(blank_pos + 1) % 8] = [0,0,0]
                            rgbLEDRow[(blank_pos + 2) % 8] = [0,0,0]
                            rgbLEDRow[(blank_pos + 3) % 8] = [0,0,0]
                        rgbLEDs += rgbLEDRow
                    sense.set_pixels(rgbLEDs)
                try :
                    a = 1
                except KeyboardInterrupt :
                    exit(-1)
                except :
                    sense.show_message("JSON ERROR ", scroll_speed = 0.04, text_colour = [255, 0, 0])
                    break
            else:
                WatchDogCnt += 1
                sense.show_message("HTTP GET: rejected ", scroll_speed = 0.04, text_colour = [255, 0, 0])
        else:
            WatchDogCnt += 1
            sense.show_message("HTTP GET: not sent ", scroll_speed = 0.04, text_colour = [255, 0, 0])
        
        if WatchDogCnt >= WATCHDOG_CNT_MAX :
            sense.show_message("Watchdog Expired: Rebooting...", scroll_speed = 0.03, text_colour = [255, 0, 0])            
            sense.clear()
            subprocess.call("sudo shutdown -r now &", shell=True)
            exit(0)
