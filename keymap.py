# キーマップ

import wx
from collections import defaultdict

class Keymap:
    def __init__(self):
        self.keymap = defaultdict(lambda: lambda: None)
        self.begin = lambda: None
        self.end   = lambda: None
    
    def oncharhook(self, evt):
        lst = [evt.GetKeyCode()]
        if lst[0] in (wx.WXK_ALT, wx.WXK_SHIFT, wx.WXK_CONTROL): return
    
        if evt.ShiftDown():   lst.append('shift')
        if evt.ControlDown(): lst.append('ctrl')
        if evt.AltDown():     lst.append('alt')
    
        self.begin()
        self.keymap[tuple(lst)]()
        self.end()
    
    def binded(self, window):
        window.Bind(wx.EVT_CHAR_HOOK, self.oncharhook)
    
    def add(self, *args):
        self.keymap[args[:-1]] = args[-1]
