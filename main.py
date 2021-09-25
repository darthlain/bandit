import os, sys, platform
import wx
import keymap
from collections import OrderedDict
from pathlib import Path
import subprocess

import option, gui, command, lib

class Global:

    def main(self):
        import sys
        if len(sys.argv) >= 2:
            g.list1.setpath(Path(sys.argv[1]).resolve())
        g.app.MainLoop()

    def active(self):
        if g.list1.active:
            return g.list1
        else:
            return g.list2

    def nonactive(self):
        if g.list1.active:
            return g.list2
        else:
            return g.list1

    def otherside(self):
        g.list1.active, g.list2.active = g.list2.active, g.list1.active

    def refresh(self):
        g.notebook.SetClientSize(g.frame.GetClientSize())
        g.sp1.SetClientSize(g.mainwindow.GetClientSize())
        g.setmsgheight()
        g.list1.Refresh()
        g.list2.Refresh()
        g.infodraw1.Refresh()
        g.infodraw2.Refresh()
        g.msg.Refresh()
        g.frame.Refresh()

        g.frame.SetStatusText(g.statusformat(g.active().linepath()) if len(g.active().files) != 0 else 'NO DATA')

        path = g.active().linepath()

        if g.imgmode and path and path.suffix[1:] in g.imgexts:
            g.openimg(g.active().linepath())

    def setmsgheight(self):
        g.sp1.SetSashPosition(g.sp1.GetClientSize()[1]
                - lib.textextent(g.font)[1] * g.msgheight - g.sp1.GetSashSize())

    def sashinit(self):
        g.sp2.SetSashPosition(g.sp2.GetClientSize()[0] // 2 - g.sp2.GetSashSize() // 2)
        g.sp2.SetSashGravity(0.5)

    def pathrefresh(self):
        g.active().setpath(self.active().path)
        g.nonactive().setpath(self.nonactive().path)

    def sync_ops(self):
        g.nonactive().setpath(g.active().path)

    def clone(self):
        subprocess.Popen(['python3', __file__])

    def seteditor(self, name, arg = ''):
        g.editor = name
        g.editorcmdflag = arg

    def setshell(self, name, arg = ''):
        g.shell = name
        g.shellcmdflag = arg

    def openimg(self, s):
        g.img = wx.Image(str(s))

    # 非推奨
    def toggle_imgmode(self):
        g.imgmode = g.imgmode != True
        if g.imgmode:
            g.msg.add('画像オートモード: ON')
        else:
            g.msg.add('画像オートモード: OFF')
        g.img = None

    def imgquit(self):
        g.img = None
        g.bitmap = None
        g.imgmode = False

g = Global()

g.statusformat = lambda x: x.path

gui.g = g
option.g = g
command.g = g

g.history = OrderedDict()

g.img = None
g.bitmap = None
g.imgmode = False
g.imgexts = ['bmp','png','jpg','jpeg','gif','tiff']

option.main()
gui.main()
command.main()

g.assoc['bmp']  = lambda dummy: g.active().imgstart()
g.assoc['png']  = lambda dummy: g.active().imgstart()
g.assoc['jpg']  = lambda dummy: g.active().imgstart()
g.assoc['jpeg'] = lambda dummy: g.active().imgstart()
g.assoc['gif']  = lambda dummy: g.active().imgstart()
g.assoc['tiff'] = lambda dummy: g.active().imgstart()
