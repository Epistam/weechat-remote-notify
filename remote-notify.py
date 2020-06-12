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
#
# Description : 
# This file is the plugin which needs to be loaded into Weechat. It will listen
# for client connections and send notification data once it is established.
# 
# TODO :
# - Create a config file with options like : 
#    - Listening port
#    - Socket path
#    - IP we want to bind (defaults to 0.0.0.0)
# - Introduce somekind of client authentification

import time
import socket
import os
import datetime

###################################### Configuration ###########################################

UNIX_SOCK_PATH = '/tmp/weechat-notify-remote.sock'
TCP_PORT = 42000
WNR_PREFIX = '[WNR] '

################################################################################################

try:
    import weechat
except:
    print("This script must be run under WeeChat.")
    print("Get WeeChat now at: https://weechat.org/")
    quit()

weechat.register("remote-notify", "Epistam", "0.1", "GPL3", "Send Bitlbee notifications to notifyd over the network", "", "")
weechat.prnt("", WNR_PREFIX + "remote-notify.py was successfully loaded into Weechat.")

################################################################################################

# Print time neatly, mostly for debugging purposes
def get_time() :
    currentDT = datetime.datetime.now()
    return str(currentDT.strftime("%Y-%m-%d %H:%M:%S")) + ' | '

# Legacy listener from v0.1 : listens to the UNIX socket and throws messages to a /tmp/test.log.
# Will be reused later.
def listener(data) :
    try:
        os.remove(UNIX_SOCK_PATH)
    except OSError:
        pass

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(UNIX_SOCK_PATH)
    s.listen(1) # 1 simultaneous connections max

    f = open("/tmp/test.log", "a")
    f.write(get_time() + 'LISTENER LOG START =============' + '\r\n')
    f.close()

    conn = None

    while True :
        f = open("/tmp/test.log", "a")                                      #LOG
        conn, addr = s.accept()
        f.write(get_time() + 'Connection accepted.\r\n')                    #LOG
        try :
            data = conn.recv(4096)
            f.write(get_time() + ' - Message : ')                           #LOG
            f.write(data + '\r\n')                                          #LOG
        except Exception as e :
            f.write(e + '\r\n' + get_time() + 'Connection closed.\r\n')     #LOG
            pass
        f.close()

    return ""

# Listens to incoming network connections. Once connection is established with
# the client, it will listen on the local UNIX socket and forward messages as
# notifications over the network.
# 
# As of v0.2, it just pings periodically the client until the client closes connection.
def tcp_listener(data) :

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', TCP_PORT))
    s.listen(1) # 1 simultaneous connections max

    f = open("/tmp/test.log", "a")                                          #LOG
    f.write(get_time() + 'LISTENER LOG START =============' + '\r\n')       #LOG
    f.close()                                                               #LOG

    conn = None

    while True :
        f = open("/tmp/test.log", "a")                                      #LOG
        conn, addr = s.accept()
        f.write(get_time() + 'TCP connection accepted.\r\n')                #LOG
        f.close()
        try :
            # Receive greetings from the client, useful when we'll want some kind of auth
            #data = conn.recv(4096)
            
            # Listen on the UNIX socket as long as TCP conn is alive
            # In v0.2, just loop and send a ping every second
            while True : 
                f = open("/tmp/test.log", "a")                              #LOG
                f.write(get_time() + '\tSending ping.\r\n')                 #LOG
                conn.send(b'I am potato')
                time.sleep(1)
                f.close()                                                   #LOG
        
        # When the client closes connection, we are back out of the try block
        except Exception as e :
            pass
        # Close connection for good measure
        conn.close()
        f = open("/tmp/test.log", "a")                                      #LOG
        f.write(get_time() + 'TCP connection closed.\r\n')                  #LOG
        f.close()                                                           #LOG

    return ""

# Sends the message to the listener upon line printing
def hook_print_callback(data, buffer, date, tags, displayed, highlight, prefix, message) :

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(UNIX_SOCK_PATH)
    
    s.send(message)

    s.close()

    return weechat.WEECHAT_RC_OK

def callback(data, command, return_code, out, err) : 
    return weechat.WEECHAT_RC_OK

################################################################################################

listener_hook = weechat.hook_process("func:tcp_listener", 0, "callback", "")
message_hook = weechat.hook_print("", "notify_none,notify_message,notify_private", "", 1, "hook_print_callback", "")
