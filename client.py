# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 by Epistam
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#   
# Versions :
# 2020-05-31 : 
#     v0.1: Message recovery, hooks and UNIX socket PoC
# 2020-06-12 :
#     v0.2: TCP connection between client and server-side plugin
#     v0.3: Messages are send to the client ; plugin detects TCP disconnection.
#     v1.0: It just works!
#     v1.1: Fixed messed up notifcations
# 2020-06-13 :
#     v1.2 : Fixed notifications stacking up in notifications list to the point
#            where it's full and they are no longer displayed.
#     v1.3 : Downloads pics to directory for easier visualization
# 2020-06-14 :
#     v1.4 : client-side retries, README changes
#
# Description : 
# This file is the client which needs to be run on the client computer. It will
# receive notification data from the Weechat plugin over the network, and
# generate the notifyd notifications using notifyd-send.

# TODO : 
#   - notifications aren't sent if X is restarted
#   - implement retries when connection is broken
#   - add fade time as parameter
#   - filter out ignored prefix
#   - read remote IP from config or from CLI arguments
#   - keep retrying to connect every so often when distant connection is broken
#   - send notifcation saying it was disconnected
#   - add messenger icon to repo and add it to notification

import time
import socket
import os
import datetime
import subprocess
import datetime as d
import re

IMG_PREFIX = '/tmp/weechat-remote-notify/'

try:
    os.mkdir(IMG_PREFIX)
except OSError:
    pass

#regex = r'http.?:\/\/.+?\.+j?p[ne]?g.*?(?=\s)' # v1, would only return the link
regex = r'(http.?:\/\/.*?\.(png|jpg|jpeg).*?(?=\s))' # 2 capturing groups : one for the whole link, one for extension

###########################################################

# Print time neatly, mostly for debugging purposes
def get_time() :
    currentDT = datetime.datetime.now()
    return str(currentDT.strftime("%Y-%m-%d %H:%M:%S")) + ' | '

def debug_log(debug_object) : 
    f = open("/tmp/remote-notify.log", "a")
    f.write(get_time() + str(debug_object) + '\r\n')
    f.close()

while True :
    try : 
        debug_log('Trying to connect to the Weechat client...')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5) # This timeout is greater than the 1 server side
        s.connect(('10.100.0.3', 42000)) # If connect times out, go to except and retry
        debug_log('Connected.')

        while True :
                # If recv times out, go to except and retry
                # It literally can't timeout if the connection is still up because the server
                # keeps sending keepalives every second, as opposed to the 5s timeout
                data = s.recv(4096) 
                #debug_log('Went past recv / didn\'t timeout')
                if data.decode("utf-8") != 'Keepalive' :
                    sender = data.decode("utf-8").split(chr(31))[0]
                    message = data.decode("utf-8").split(chr(31))[1]

                    # Images download
                    links = re.findall(regex, message)
                    [subprocess.Popen(['wget', link[0], '-O', str(IMG_PREFIX + str(d.datetime.now()).replace(" ", "_") + '_' + sender + '.' + link[1])]) for link in links]

                    # Message processing
                    debug_log('Sender : ' + sender)
                    debug_log('Message : ' + message)

                    cmd_string = 'notify-send --hint int:transient:1 -t 8000 "' + sender + '" "' + message + '"'
                    os.system(cmd_string)

    except Exception as e :
        debug_log('Connection timed out.')
        s.close()
        pass

s.close()
