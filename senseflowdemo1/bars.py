#!/usr/bin/python

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

import time
import serial

class AtCellModem_14A2A:
    uart = ""
    timeout = 30
    modem_type = ""
    dbg = ""
    __dbgFileName = ""
    __dbgOutput = ""
    
    def __init__(self, serial, timeout=10, debug = False, dbgFileName = ""):
        self.__dbgFileName = dbgFileName
        try :
            if dbgFileName <> "" :
                self.__dbgOutput = open(dbgFileName, 'w+')
        except KeyboardInterrupt:
            exit(-1)
        except :
            print "Bad FILE name!"
            exit(-1)
        self.uart = serial
        self.timeout = timeout
        self.modem_type = "None"
        if serial.isOpen() == True :
            serial.flush()
            result = False
            # These are critical for getting the modem back after a reboot of the Pi
            self.send_mdm_cmd('\n', 1)            
            self.send_mdm_cmd('AT', 1)
            self.send_mdm_cmd('\n', 1)            
            self.send_mdm_cmd('AT', 1)
            self.send_mdm_cmd('\n', 1)            
            self.send_mdm_cmd('AT', 1)
            result, resp = self.get_version()
            if debug == True :
                self.dbg = "Init type: " + str(resp)            
            if result == False :
                print "AT ERR: " + resp
                if debug == True :
                    self.dbg = "Init AT ERR: " + str(resp)            
            else:
                self.modem_type = resp

    def __write(self, cmd):
        try:
            if self.uart.isOpen() == True :
                self.uart.write(cmd)
                return True
            else:
                self.uart.open()
                return False
        except KeyboardInterrupt:
            exit(-1)
        except :
            self.uart.close()
            return
            
    def __readline(self):
        try:
            if self.uart.isOpen() == True :
                resp = self.uart.readline()
                return True, resp
            else:
                self.uart.open()
                return False, "None"
        except KeyboardInterrupt:
            exit(-1)
        except:
            self.uart.close()
            return False, "None"
            
    def get_version(self,debug=False):
        result, resp = self.send_mdm_cmd('AT+CGMR',debug)
        if result == True:
            try:
                resp = resp[2].replace('_', ' ').split()[0]
                self.modem_type = resp
            except KeyboardInterrupt:
                exit(-1)
            except:
                resp = "None"
        if debug == True :
            self.dbg = "get_version" + str(resp)
        return result, resp
        
    def send_mdm_cmd(self, cmd, timeout = -1, debug = False):
        result = False
        if (timeout < 1):
            timeout = self.timeout
        if debug == True : print "cmd: " + str(cmd)
        if self.__dbgFileName <> "" :
            self.__dbgOutput.write("cmd: " + str(cmd))
        if self.__write(cmd + "\n") == False :
            if self.__dbgFileName <> "" :
                self.__dbgOutput.write("***\n")
            return False, "None"
        if self.__dbgFileName <> "" :
            self.__dbgOutput.write("\n")
        start_time = time.time()
        timeout += 1 # Time is integer and adding 1 will make sure it is at least (and more)
        resp = "" 
        # Loop polls for chars until proper response is found or timeout! 
        while True :
            result, tmp = self.__readline()
            if result == False :
                return False, "None"
            if tmp.find("OK") >= 0 :
                resp += tmp
                result = True
                break
            if tmp.find("NOTIFYEV") >= 0 :
                print "NOTIFYEV: " + tmp
                # Throw away the notify event for now and don't let be passed back!
                tmp = ''
            if tmp.find("+CME ERROR") >= 0 :
                resp += tmp
                break
            if tmp.find("@EXTERR") >= 0 :
                resp += tmp
                break
            if tmp.find("ERROR") >= 0 :
                resp += tmp
                break
            if ((time.time() - start_time) >= timeout) :
                resp += tmp
                resp += "TIMEOUT"
                break
            resp += tmp
        # Remove CR, LF
        resp = resp.replace('\r', ' ').replace('\n', ' ').replace('=', ' ').replace(',', ' ').replace(':', ' ')
        #print resp
        resp = resp.split()
        if debug == True : print resp
        if self.__dbgFileName <> "" :
            self.__dbgOutput.write("resp: " + str(resp) + "\n")            
        return result, resp
        
    def is_on_network(self, debug=False):
        if self.modem_type == "M14A2A":
            try:
                cmd = 'AT+CREG?'
                result, resp = self.send_mdm_cmd(cmd, timeout = 1, debug=debug)
                if debug == True :
                    self.dbg = cmd + '::' + str(resp)
                if result == True :
                    resp = resp[3]
                    if (resp == '1' or resp == '5'):  # 1 - home network, 5 - roaming
                        return True
                    else:
                        return False
                return result
            except KeyboardInterrupt:
                exit(-1)
            except:
                if debug == True :
                    self.dbg = "Except " + str(resp)
                return False
        else:
            if debug == True :
                self.dbg = "Invalid Type"
            return False

    # 14A2A gets messed up if signal measure occurs to much!
    def calc_rx_bars(self, n, debug = False):
        n = int(round(n))
        if n < 1 : n = 1
        if self.modem_type == "M14A2A":
            avg = 0
            for i in range(n) :
                val = self.read_rsrp(debug=debug)
                if val == -150 : # If get an invalid reading invalidate it all
                    return -1
                avg += val
            avg /= n
            # Map RSRP into BARs, it is probably more accurate to use combination of RSSI and RSRQ, RSRP but I don't know the magic formula yet
            if (avg <= -120):
                return 0
            if (avg > -80):
                return 4
            if (avg > -120) and (avg <= -115):
                return 1
            if (avg > -115) and (avg <= -100):
                return 2
            if (avg > -100) and (avg <= -80):
                return 3
        else :
            print "ERR: calc_rx_bars"
            return -1
        
    def read_rsrp(self,debug=False):
        result, resp = self.read_signal_quality(0,debug)
        if result == False :
            print "ERR: read_rsrp", resp
            return -150
        else:
            try:
                rsrp = int(resp[4].replace(',',''))
            except KeyboardInterrupt:
                exit(-1)
            except:
                print resp
                rsrp = -150
            return rsrp
            
    def read_tx_pusch(self,debug=False):
        result, resp = self.read_signal_quality(4,debug)
        if result == False :
            print "ERR: read_tx_power", resp
            return -999
        else:
            try:
                pwr = int(resp[5])
            except KeyboardInterrupt:
                exit(-1)
            except:
                print "ERR read_tx_power value"
                pwr = -999
            return pwr

    def read_rssi(self,debug=False):
        result, resp = self.read_signal_quality(3,debug)
        if result == False :
            print "ERR: read_rssi", resp
            return -120
        else:
            try:
                rssi = int(resp[4].replace(',',''))
            except KeyboardInterrupt:
                exit(-1)
            except:
                print resp
                rssi = -120
            return rssi
            
    def read_signal_quality(self, type, timeout = 1, debug = False):
        # For more info see: http://www.laroccasolutions.com/78-rsrp-and-rsrq-measurement-in-lte/
        # <measurement type>: string
        # "0" - RSRP
        # "1" - RSRQ
        # "2" - SINR
        # "3" - RSSI
        # "4" - TX Power
        # "5" - Temperature
        # "6" - Path loss
        # "7" - CQI
        # "8" - Signal Quality (RSRP & RSRQ & SINR & RSSI)
        # "93" - Network Time alignment with SFN
        # "97" - RSRP & RSRQ for all detected NBS
        # "98" - RSRP for all detected NBS
        # "99" - RSRQ for all detected NBS
        # <EARFCN>: integer, Decimal EARFCN value
        # <cell ID>: integer, Decimal Physical Cell ID value
        # <RSRP>: integer, -140 <= RSRP <= 0
        # <RSRQ>: integer, -64 <= RSRQ <=0
        # <SINR>: integer, -12 <= SINR <= 40
        # <TX Power>: integer, 10dBm for TX Power, -26 <= TX Power <= 40
        # <Temperature>: integer, Degrees (C) for Temperature, -128 <= Temperature <= 128
        # <networkTTI>: integer, The subframe counter of the serving cell corresponds to the network UTC time. The subframe counter is a decimal running from 0 to 10239 (i.e. rollover at 10240) also known as TTI (Transmission Time Interval) counter.
        # <networkUtcTime>: integer, This field specifies the network UTC time which correspond to the specified TTI counter. The UTC time is a decimal counter of 1msec units counted since 00:00:00 on 1 January, 1900
        if self.modem_type == "M14A2A":
            result, resp = self.send_mdm_cmd('AT%MEAS=\"' + str(type) + '\"', timeout=timeout, debug=debug)
            return result, resp
        else:
            return False, "ERR: read_signal_quality"

        
# cmd_list = [['AT', 1],
           # ['AT+CSQ', 1],
           # ['AT+CGMR', 1]]

# UART_READ_TIMEOUT_SECS = 2
# uart1 = serial.Serial('/dev/ttyACM0', 115200, timeout=UART_READ_TIMEOUT_SECS)
# print(uart1.name)

#for cmd in cmd_list :
#    for n in range(cmd[1]) : 
#        print send_mdm_cmd(mdm1, cmd[0], UART_READ_TIMEOUT_SECS).split()
        
# mdm = AtCellModem_14A2A(uart1, timeout=UART_READ_TIMEOUT_SECS)
# print mdm.get_version()
# while 1:
    # print mdm.is_on_network()
    # print "PUSCH " + str(mdm.read_tx_pusch())
    # print "RSSI " + str(mdm.read_rssi()) + " RSRP " + str(mdm.read_rsrp()) + " BARS " + str(mdm.calc_rx_bars(50))
