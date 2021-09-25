import wx, platform
from unicodedata import east_asian_width

def textextent(font = wx.Font(), s = 'a'):
    dc = wx.ScreenDC()
    dc.SetFont(font)
    return dc.GetTextExtent(s)

def opencmd():
    sys = platform.system()

    if sys == 'Windows': return 'start ""'
    elif sys == 'Linux': return 'xdg-open'
    else:                return 'open'

def osenc():
    sys = platform.system()
    if sys == 'Windows': return 'shift-jis'
    else:                return 'utf-8'

class Dummy:

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, *args, **kwargs):
        return self

# マルチバイト文字列の見た目の長さ
def mblen(s):
    acc = 0
    for i in s:
        if east_asian_width(i) in 'FWA':
            acc += 2
        else:
            acc += 1

    return acc

def scalefitw(imgsize, screensize):
    # 横に合わせる
    p = screensize[0] / imgsize[0]
    a = imgsize[0] * p, imgsize[1] * p
    return a

def scalefith(imgsize, screensize):
    p = screensize[1] / imgsize[1]
    a = imgsize[0] * p, imgsize[1] * p
    return a

def scalefitaspect(imgsize, screensize):
    p1 = screensize[0] / imgsize[0]
    p2 = screensize[1] / imgsize[1]
    p = min(p1, p2)

    a = imgsize[0] * p, imgsize[1] * p
    return a
