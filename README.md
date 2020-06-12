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
- `remote-notify.py`, which is meant to be run as a plugin by Weechat
- `remote-notify-client.py, which is meant to be run on the "client machine", i.e the one supposed to receive the notifications. 

`remote-notify.py` works by creating a 

## Licensing

## Ressources

Useful links : 
- [Weechat scripting reference](https://weechat.org/files/doc/devel/weechat_scripting.en.html)
- ...
