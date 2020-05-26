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
# Releases :
# 2020-XX-XX : 
#     v0.1: it just works(tm)

try:
    import weechat as w
except:
    print("This script must be run under WeeChat.")
    print("Get WeeChat now at: https://weechat.org/")
    quit()

# Test
weechat.register("test_python", "FlashCode", "1.0", "GPL3", "Test script", "", "")
weechat.prnt("", "Hello, from python script!")
