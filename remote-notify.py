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
#     v0.3: Messages are sent to the client ; plugin detects TCP disconnection.
#     v1.0: It just works!
#
# Description : 
# This file is the plugin which needs to be loaded into Weechat. It will listen
# for client connections and send notification data once it is established.
# 
# TODO :
# - Limit to n first characters of a message
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
SERVER_NAME = 'localhost'

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

def debug_log(debug_string) : 
    f = open("/tmp/test.log", "a")
    f.write(get_time() + debug_string + '\r\n')
    f.close()

# Listens to incoming network connections. Once connection is established with
# the client, it will listen on the local UNIX socket and forward messages as
# notifications over the network.
def tcp_listener(data) :

    # Binding TCP socket
    tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_s.bind(('0.0.0.0', TCP_PORT))
    tcp_s.listen(1) # 1 simultaneous connections max
    
    # Binding UNIX socket
    try:
        os.remove(UNIX_SOCK_PATH)
    except OSError:
        pass
    unix_s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    unix_s.bind(UNIX_SOCK_PATH)
    unix_s.listen(1) # 1 simultaneous connections max
    unix_s.settimeout(1) # accept() timeout set on 1 second
    
    debug_log('LISTENER LOG START =============')
    
    # Put conncetions in the function scope
    tconn = None
    uconn = None

    while True :
        tconn, taddr = tcp_s.accept() # Waiting for client connection
        debug_log('TCP connection accepted.')
        # This block catches exceptions related to the TCP socket
        # If an exception is raised, it means the socket is dead somehow and the plugin needs
        # to wait for a TCP connection again.
        try : 
            while True :
                # This block handles UNIX socket exceptions.
                # The UNIX socket is set to timeout at 1s, so that we can check if the TCP
                # connection is still alive every so often.
                try : 
                    # Throws a timeout exception when it times out
                    uconn, uaddr = unix_s.accept()

                    # If we get this far, there has been a connection on the UNIX socket.

                    # Receive UNIX socket data an store it in a buffer
                    data = uconn.recv(4096)
                    debug_log('\tMessage received : ' + data)

                    # Forward the buffer to the client via the TCP connection
                    # Edge case : the TCP connection breaks before than : in this case,
                    # this will throw an exception, and move on the keepalive which will cascade
                    # back to the bigger "try" block.
                    tconn.send(data)
                    debug_log('\tMessage sent to client.')
                    
                    # The hook will have closed the connection, so we'll close it here too 
                    # to clean things up.
                    uconn.close()
                except Exception as e : 
                    pass

                # This check keepalive checks if the TCP connection is still alive.
                # If not, it will raise an exception which will be caught outside of the loop.
                tconn.send(b'Keepalive')

        except Exception as e :
            tconn.close()
            debug_log('TCP connection closed.')
            pass

    return ""

# Sends the message to the listener upon line printing
def hook_print_callback(data, buffer, date, tags, displayed, highlight, prefix, message) :

    if weechat.info_get("irc_nick", SERVER_NAME) not in prefix :

        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sent_string = ""

        # s.connect() doesn't seem to return an exception, just blocks waiting for connection apparently
        s.settimeout(1) 
        try :
            debug_log('HOOK : Trying to connect to UNIX socket.')
            s.connect(UNIX_SOCK_PATH)
            sent_string = prefix + chr(31) + message # Using ASCII unit separator
            s.send(sent_string)
        except Exception as e :
            debug_log('HOOK : UNIX socket is unavailable. Dismissing message.')
            pass

        s.close()

    return weechat.WEECHAT_RC_OK

def callback(data, command, return_code, out, err) : 
    return weechat.WEECHAT_RC_OK

################################################################################################

listener_hook = weechat.hook_process("func:tcp_listener", 0, "callback", "")
message_hook = weechat.hook_print("", "notify_none,notify_message,notify_private", "", 1, "hook_print_callback", "")
