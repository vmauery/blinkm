#!/usr/bin/env python3

# applet for controlling blinkm LED
# Copyright (C) 2021 Vernon Mauery
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import wx.adv
import wx
from blink1.blink1 import Blink1
import time, regex, sys

class NoBlnkReady(Exception):
    pass

class Blnk:
    def __init__(self):
        try:
            self.b = Blink1()
            self.off()
        except:
            raise NoBlnkReady()

    def on(self):
        try:
            self.b.fade_to_color(0, 'red')
            self.is_on = True
        except:
            return False
        return True

    def off(self):
        try:
            self.b.off()
            self.is_on = False
        except:
            return False
        return True

    def lit(self):
        return self.is_on

def istime(v):
    m = regex.match(r'^([0-9]+)([hms]?)$', v)
    if m is None:
        return 0
    m = m.groups()
    n = int(m[0])
    if m[1] == 'm':
        n *= 60
    elif m[1] == 'h':
        n *= 3600
    return n

class OneArgMenu:
    def __init__(self, handler, arg):
        self.handler = handler
        self.arg = arg
    def __call__(self, event):
        self.handler(event, self.arg)

class TaskBarIcon(wx.adv.TaskBarIcon):
    LED_LIT = ('red-led.png', 'LED On')
    LED_OFF = ('off-led.png', 'LED Off')

    def __init__(self, frame):
        self.blnk = Blnk()
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(self.LED_OFF)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

    def CreatePopupMenu(self):
        def create_menu_item(menu, label, func):
            item = wx.MenuItem(menu, -1, label)
            menu.Bind(wx.EVT_MENU, func, id=item.GetId())
            menu.Append(item)
            return item
        menu = wx.Menu()
        # create_menu_item(menu, '10 Seconds', OneArgMenu(self.on_arm_timer, 10))
        create_menu_item(menu, '30 Minutes', OneArgMenu(self.on_arm_timer, 32*60))
        create_menu_item(menu, '1 Hour', OneArgMenu(self.on_arm_timer, 62*60))
        create_menu_item(menu, '1.5 Hours', OneArgMenu(self.on_arm_timer, 92*60))
        create_menu_item(menu, '2 Hours', OneArgMenu(self.on_arm_timer, 122*60))
        menu.AppendSeparator()
        create_menu_item(menu, 'On', self.on_on)
        create_menu_item(menu, 'Off', self.on_off)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, choice):
        icon = wx.Icon(choice[0])
        self.SetIcon(icon, choice[1])

    def on(self):
        self.set_icon(self.LED_LIT)
        if not self.blnk.on():
            self.blnk = None
            self.blnk = Blnk()
            self.blnk.on()

    def off(self):
        self.set_icon(self.LED_OFF)
        if not self.blnk.off():
            self.blnk = None
            self.blnk = Blnk()
            self.blnk.off()

    def on_left_down(self, event):
        # print('Toggle on-off')
        self.timer.Stop()
        if self.blnk.lit():
            self.off()
        else:
            self.on()

    def on_arm_timer(self, event, timeout):
        # print('Turn on for {} seconds'.format(timeout))
        self.timer.Start(timeout*1000, wx.TIMER_ONE_SHOT)
        self.on()

    def on_timer(self, event):
        # print('Timeout')
        self.timer.Stop()
        self.off()

    def on_on(self, event):
        # print('Turn On')
        self.timer.Stop()
        self.on()

    def on_off(self, event):
        # print('Turn Off')
        self.timer.Stop()
        self.off()

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Close()

class App(wx.App):
    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True

def main():
    app = App(False)
    app.MainLoop()


if __name__ == '__main__':
    main()
