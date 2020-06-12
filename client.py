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
#
# Description : 
# This file is the client which needs to be run on the client computer. It will
# receive notification data from the Weechat plugin over the network, and
# generate the notifyd notifications using notifyd-send.

# TODO : 
#   - add actual notifications
#   - read remote IP from config or from CLI arguments
#   - keep retrying to connect every so often when distant connection is broken
#   - send notifcation saying it was disconnected

import time
import socket
import os
import datetime

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.0.13', 42000))
s.send(b"I like potatoes")

while True :
    data = s.recv(4096)
    print('TCP received : ' + data.decode("utf-8") + '\r\n')

s.close()
