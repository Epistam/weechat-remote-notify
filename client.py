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
#
# Description : 
# This file is the client which needs to be run on the client computer. It will
# receive notification data from the Weechat plugin over the network, and
# generate the notifyd notifications using notifyd-send.

# TODO : 
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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.0.13', 42000))
s.send(b"I like potatoes")

while True :
    data = s.recv(4096)
    if data.decode("utf-8") != 'Keepalive' :
        sender = data.decode("utf-8").split(chr(31))[0]
        message = data.decode("utf-8").split(chr(31))[1]

        # Images download
        links = re.findall(regex, message)
        [subprocess.Popen(['wget', link[0], '-O', str(IMG_PREFIX + str(d.datetime.now()).replace(" ", "_") + '_' + sender + '.' + link[1])]) for link in links]

        # Message processing
        print('Sender : ' + sender)
        print('Message : ' + message)

        cmd_string = 'notify-send --hint int:transient:1 -t 8000 "' + sender + '" "' + message + '"'
        os.system(cmd_string)

s.close()
