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

import time
import socket
import os
import datetime

try:
    import weechat
except:
    print("This script must be run under WeeChat.")
    print("Get WeeChat now at: https://weechat.org/")
    quit()

weechat.register("remote-notify", "Epistam", "0.1", "GPL3", "Send Bitlbee notifications to notifyd over the network", "", "")
w.prnt("", "remote-notify.py has been loaded into Weechat.")

################################################################################################

# Print time neatly, mostly for debugging purposes
def get_time() :
    currentDT = datetime.datetime.now()
    return str(currentDT.strftime("%Y-%m-%d %H:%M:%S")) + ' | '

# Listens to incoming network connections. Once connection is established with
# the client, it will listen on the local UNIX socket and forward messages as
# notifications over the network.
# 
# In v0.1, it just listens on the UNIX socket and writes messages to a log file.
def listener(data) :

    try:
        os.remove("/tmp/weechat-notify-remote.sock")
    except OSError:
        pass

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind("/tmp/weechat-notify-remote.sock")
    s.listen(1) # 1 simultaneous connections max

    f = open("/tmp/test.log", "a")
    f.write(get_time() + 'LISTENER LOG START =============' + '\r\n')
    f.close()

    conn = None

    while True :
        f = open("/tmp/test.log", "a")
        conn, addr = s.accept()
        f.write(get_time() + 'Connection accepted.\r\n')
        try :
            data = conn.recv(4096)
            f.write(get_time() + ' - Message : ')
            f.write(data + '\r\n')
        except Exception as e :
            f.write(e + '\r\n')
            f.write(get_time() + 'Connection closed.\r\n')
            pass
        f.close()

    f = open("/tmp/test.log", "a")
    f.write(get_time() + 'LISTENER LOG END =============' + '\r\n')
    f.close()

    conn.close()

    return ""

# Sends the message to the listener upon line printing
def hook_print_callback(data, buffer, date, tags, displayed, highlight, prefix, message) :

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect("/tmp/weechat-notify-remote.sock")
    
    s.send(message)

    s.close()

    return weechat.WEECHAT_RC_OK

def callback(data, command, return_code, out, err) : 
    return weechat.WEECHAT_RC_OK

################################################################################################

listener_hook = weechat.hook_process("func:listener", 0, "callback", "")
message_hook = weechat.hook_print("", "notify_none,notify_message,notify_private", "", 1, "hook_print_callback", "")



















################################################################################################

#import time
#import socket
#import os
#
#def child_func(socket_fd) : 
#
#    try : 
#        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0, socket_fd)
#
#        s.send(b'kkkk')
#    except Exception as e :
#        print("CHILD FAILED")
#        print(e)
#
#def parent_func() : 
#
#    
#    s_recv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#    s_send = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#
#    try : 
#        # Bind receiving end of the socket
#        s_recv.bind("/tmp/test7.sock")
#        s_recv.listen(1) # 1 simultaneous connections max
#
#        # Connect on the sending end
#        s_send = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#        s_send.connect("/tmp/test7.sock")
#
#        child_func(s_send.fileno())
#
#        msg = s_recv.recv(4)
#
#        print(msg)
#    except Exception as e :
#        print("PARENT FAILED")
#        print(e)
#        s_recv.close()
#        s_send.close()
#
#    s_recv.close()
#    s_send.close()
#
#parent_func()
