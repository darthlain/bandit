from pathlib import Path
import os

def main():
    g.defaultsize = (800, 600)
    g.scrolloff = 9999
    g.msgmax = 99
    g.msgheight = 6
    g.shell = 'nyagos'
    g.shellcmdflag = '-c'
    g.editor = 'gvim'
    g.editorcmdflag = '--remote-tab-silent'
    g.mrufile = Path(__file__).resolve().parent / 'mru'
    g.transparency = -1
    g.assoc = dict()
    g.defaultsort = 'ngt'
    g.defaultsort2 = 'ng'
    g.defaultsortmax = 9999
    g.imgtype = 'otherside'
    
    g.color_bg   = (0,0,0)
    g.color_fg   = (255,255,255)
    g.color_dir  = (0,255,255)
    g.color_line = (255,255,255)
    g.color_hide = (255,0,255)
    g.color_ro   = (0,255,0)
    g.color_mark = (0,0,255)
    g.color_sys  = (255,0,0)
    g.color_info = (0,255,0)
