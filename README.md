# weechat-remote-notify

## Description
This Weechat plugin aims to provide a simple way to send notifyd notifications
from remote hosts. In order to do that, it will bind a port on which it will
listen to incoming connections from the client script, and send notifications to
be displayed on the client computer.

It can be used in combination with a Weechat client being accessed through SSH
(using mosh and GNU Screen) for example.

## Security
Authentification and / or encryption is not taken into account yet since I
intend to use this plugin in a LAN or through a VPN. It should, however, be an
expected future development.

Thus, please note **all the network trafic caused by this plugin will be sent
unencrypted** and as such will be perfectly readable to any attacker on the
network. 

**USE AT YOUR OWN RISK.**

## Installation

TODO.

## Structure
The program is made up of two files : 
- `remote-notify.py`, which is meant to be run as a plugin by Weechat. It works
  by creating a launch a thread which will listen to incoming TCP connections.
  In parallel, the Weechat API will call a hook function every time a message
  is to be displayed, sending it to the listener via UNIX socket.
- `client.py, which is meant to be run on the "client machine", i.e the one
  supposed to receive the notifications. It establishes connection to the
  server / plugin running on Weechat, and basically forwards messages in the
  form of Xorg notifications.


## Licensing
something something yada yada...
Just slapped a GPLv3 on that, I guess I'll see what becomes of it later.

## Ressources

Useful links : 
- [Weechat scripting reference](https://weechat.org/files/doc/devel/weechat_scripting.en.html)
- [Weechat API documentation](https://weechat.org/files/doc/stable/weechat_plugin_api.en.html)
- [Python sockets documentation](https://docs.python.org/3/library/socket.html)
