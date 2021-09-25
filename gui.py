import wx, keymap
import ctypes
import wx.aui
import pathlib
from pathlib import Path
import lib
import traceback
import subprocess
from send2trash import send2trash
import os
import shutil
import functools
from collections import OrderedDict
import pyperclip
import platform
from natsort import os_sorted
import re

# Pathを模倣する
class SpPath(lib.Dummy):

    def __init__(self, s):
        self.name = s

    def __str__(self):
        return self.name

# os.DirEntryでpathlib.Pathのメソッドが使えるように
# 追加でpathlib.Pathもラップするようになった
class DirEntryWrapper:

    def __init__(self, x):
        if isinstance(x, os.DirEntry):
            self.path = os.path.abspath(x.path)
            self.suffix = os.path.splitext(x.name)[1]
            self.stat = x.stat()
            self.size = self.stat.st_size
        elif isinstance(x, pathlib.Path):
            self.path = str(x)
            self.suffix = x.suffix

        self.ins = x
        self.name = x.name

    def is_dir(self):
        return self.ins.is_dir()

    def __eq__(self, x):
        return self.ins == x

    def __str__(self):
        return self.path

class List(wx.Panel):

    def __init__(self, parent, active = True, history = OrderedDict(), path = Path().resolve()):
        self.history = history
        self.active = active
        self.searching = None
        self.setpath(path)

        # .name = ライン表記のフォーマット 基本は lambda x: x.name

        super().__init__(parent)

        self.SetBackgroundColour(g.color_bg)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.onpaint)
        self.Bind(wx.EVT_CHAR_HOOK, lambda e: wx.PostEvent(g.frame, e))

    def onpaint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        dc.SetFont(g.font)

        w = self.GetClientSize()[0]
        h = dc.GetTextExtent('a')[1]

        if len(self.files) == 0:
            dc.SetPen(wx.Pen(g.color_fg))
            dc.SetTextForeground(g.color_fg)

            nodata = '-NODATA-'

            dc.DrawText(nodata,
                    w // 2 - dc.GetTextExtent('a')[0] * lib.mblen(nodata) // 2,
                    h * self.looknum() // 2)

        self.scroll = min(max(0, self.line - self.looknum() // 2),
                max(0, len(self.files) - self.looknum()))

        # 逆側に画像表示
        if g.img and g.imgtype == 'otherside' and not self.active:

            a = g.img.GetWidth(), g.img.GetHeight()
            b = self.GetClientSize()

            g.img = g.img.Scale(*lib.scalefitaspect(a, b), wx.IMAGE_QUALITY_HIGH)
            g.bitmap = wx.Bitmap(g.img)
            dc.SetPen(wx.Pen(wx.BLACK, 4))
            dc.DrawBitmap(g.bitmap, 0, 0, True)

        else:
            for i in range(min(len(self.files), self.looknum())):

                ipath = DirEntryWrapper(self.files[i + self.scroll])

                if ipath in self.selects:
                    dc.SetPen(wx.Pen(g.color_mark))
                    dc.SetBrush(wx.Brush(g.color_mark))
                    dc.DrawRectangle(0, i * h, w, h)

                if self.active and ipath == self.linepath():
                    dc.SetPen(wx.Pen(g.color_line))
                    dc.DrawLine(0, i * h + h - 1, w, i * h + h - 1)

                dc.SetPen(wx.Pen(g.color_fg))

                try:
                    if ipath.is_dir():
                        dc.SetTextForeground(g.color_dir)
                        acc = self.name(ipath)
                    # ファイル
                    else:
                        dc.SetTextForeground(g.color_fg)

                        acc = ''
                        size = w // dc.GetTextExtent('a')[0]
                        name = self.name(ipath)

                        # 拡張子
                        acc += ' ' + os.path.splitext(ipath.path)[1]
                        size -= 1 + len(os.path.splitext(ipath.path)[1])

                        # ファイル名
                        #if ipath.name[0] == '.' or '.' not in name:
                        #    noext = name 
                        #else:
                        #    noext = '.'.join(name.split('.')[:-1])
                        noext = name
                        if lib.mblen(noext) <= size:
                            acc = noext + ' ' * (size - lib.mblen(noext)) + acc
                        else:
                            accs = ''
                            accn = 0
                            while 1:
                                if size < accn + 2 + lib.mblen(noext[0]):
                                    break
                                accs += noext[0]
                                accn += lib.mblen(noext[0])
                                noext = noext[1:]
                            acc = accs + '…' + (' ' if size == accn + 3 else '') +acc

                except PermissionError:
                    dc.SetTextForeground(g.color_sys)
                    acc = self.name(ipath)

                dc.DrawText(acc, 0, h * i)

        g.frame.SetTitle('bandit - [%s]' % str(g.active().path))

    def setpath(self, path = Path().resolve(), clearselects = True):
        # historyに以前のパスを登録
        if 'line' in dir(self) and not isinstance(self.path, SpPath):
            self.history[self.path] = (self.line)
            self.history.move_to_end(self.path)

        if hasattr(self, 'path'):
            oldpath = self.path
            oldline = self.line

        self.path = path

        try:

            # history読み込み
            if path in self.history:
                (self.line) = self.history[path]
            else:
                self.line = 0

            # historyに現在のパスを登録
            if not isinstance(path, SpPath):
               self.setmask('*')

               self.history[path] = self.line
               self.history.move_to_end(path)

            if clearselects:
                self.selects = []
            self.name = lambda x: x.name

        except PermissionError:

            self.path = oldpath
            self.line = oldline
            g.msg.add('ACCESS DENIED [%s]' % self.linepath())

    def setmask(self, mask = '*'):
        self.mask = mask
        self.files = list(os.scandir(self.path))

        self.line = min(self.line, max(len(self.files) - 1, 0))

        if len(self.files) <= g.defaultsortmax:
            self.setsort(g.defaultsort)
        else:
            self.setsort(g.defaultsort2)
        
    def setsort(self, s):
        # TODO
        if 'g' in s:
            self.files = os_sorted(self.files)
        elif 'n' in s:
            self.files.sort()
        if 't' in s:
            self.files.sort(key=lambda i: i.is_file())

    def looknum(self):
        return self.GetClientSize()[1] // lib.textextent(g.font)[1]

    def linepath(self):
        return DirEntryWrapper(self.files[self.line]) if len(self.files) != 0 else None

    def lineup(self):
        self.line = min(max(self.line - 1, 0), self.line)

    def linedown(self):
        self.line = max(min(self.line + 1, len(self.files) - 1), self.line)

    def linehalfup(self):
        self.line = min(max(self.line - self.looknum() // 2, 0), self.line)

    def linehalfdown(self):
        self.line = max(min(self.line + self.looknum() // 2, len(self.files) - 1),
                self.line)

    def linetop(self):
        self.line = 0

    def linebottom(self):
        self.line = len(self.files) - 1

    def pathback(self):

        # 特殊パスの場合
        if isinstance(self.path, SpPath):
            self.setpath(next(reversed(self.history), None))
            return

        # 親ディレクトリがない場合
        if self.path.parent == self.path:
            return

        old = self.path
        self.setpath(self.path.parent)

        t = 0

        for i in self.files:
            if i.path == str(old):
                self.line = t
            t += 1

    def back(self):
        if g.img:
            g.imgmode = False
            g.img = None
        else:
            self.pathback()

    def enter(self):
        if self.linepath().is_dir():
            self.setpath(Path(str(self.linepath())))
        else:
            a = g.assoc.get(self.linepath().suffix[1:].lower())

            if a:
                a(self.linepath())

    def edit(self):
        os.system('%s %s %s' % (g.editor, g.editorcmdflag, self.linepath()))

    def open(self):
        a = lib.opencmd() + ' "' + self.linepath().path + '"'
        subprocess.call(a, shell=True)

    def lineselect(self):
        if self.linepath() in self.selects:
            self.selects.remove(self.linepath())
        else:
            self.selects.append(self.linepath())
        self.linedown()

    def lineselect_ops(self):
        if self.linepath() in self.selects:
            self.selects.remove(self.linepath())
        else:
            self.selects.append(self.linepath())
        self.lineup()

    def lineclear(self):
        self.selects = []

    def allfileselect(self):
        self.selects = [i for i in self.files if i.is_file()]

    def allselect(self):
        self.selects = [i for i in self.files]

    def terminal(self):
        subprocess.run(lib.opencmd() + ' ' + g.shell, shell=True, cwd=self.path)

    def winproperty(self):
        ctypes.windll.shell32.SHObjectProperties(0, 2, self.linepath().path, None)

        # TODO 複数のファイルのプロパティを見る方法がわからない
        #ctypes.windll.shell32.SHMultiFileProperties(['F:\\download\\'], 0)

    def goto(self):
        dlg = wx.TextEntryDialog(None, 'goto?')
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_CANCEL: return

        path = Path(dlg.GetValue()).expanduser()

        if path.is_absolute():
            pass
        else:
            path = (self.path / path).resolve()

        if path.exists():
            self.setpath(path)
        else:
            g.msg.add('goto: パスが見つかりません')

    def mkdir(self):
        dlg = wx.TextEntryDialog(None, 'mkdir?')
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_CANCEL: return
        (self.path / dlg.GetValue()).mkdir()
        self.setpath(self.path)
        g.pathrefresh()

    def touch(self):
        dlg = wx.TextEntryDialog(None, 'touch?')
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_CANCEL: return
        (self.path / dlg.GetValue()).touch(exist_ok=False)
        self.setpath(self.path)
        g.pathrefresh()

    def rename(self):
        dlg = wx.TextEntryDialog(None, 'rename?')
        dlg.ShowModal()
        dlg.Destroy()

        if dlg.GetValue() != '':
            newpath = self.linepath().parent / dlg.GetValue()
            self.linepath().rename(newpath)
            self.setpath(self.path)

    def duplicate(self):
        dlg = wx.TextEntryDialog(None, 'duplicate?')
        dlg.ShowModal()
        dlg.Destroy()

        if dlg.GetValue() != '':
            os.chdir(str(self.path))
            shutil.copyfile(self.linepath().name, dlg.GetValue())
            self.setpath(self.path)

    def clip(self, a):
        pyperclip.copy(a)
        g.msg.add('clip: %s' % a)

    def clip_linepath(self):
        self.clip('"' + str(self.linepath()) + '"')

    def clip_linename(self):
        self.clip(self.linepath().name)

    def info(self):
        dlgmsg  = '名前: %s\n' % self.linepath().name
        dlgmsg += '種類: %s\n' % (self.linepath().suffix if not self.linepath().is_dir() else 'フォルダ')
        dlgmsg += '場所: %s\n' % str(self.path)
        dlgmsg += 'サイズ: %d' % self.linepath().size
        dlg = wx.MessageDialog(None, dlgmsg, '', wx.ICON_NONE)
        val = dlg.ShowModal()
        dlg.Destroy()

    def do(self, name, do, msg = '', _type = 1):

        if len(self.selects) == 0:
            dlgmsg = name + '?' + msg
        else:
            dlgmsg = name + ' selects?' + msg

        dlg = wx.MessageDialog(None, dlgmsg, '', wx.YES_NO | wx.CANCEL)
        val = dlg.ShowModal()
        dlg.Destroy()

        if val == wx.ID_YES:
            for i in self.selects if self.selects != [] else [self.linepath()]:
                try:
                    do(i, g.nonactive().path)
                    s = name + ' ' + str(self.linepath())
                    if _type == 2:
                        s += ' -> '
                        try:
                            s += os.path.relpath(g.nonactive().path, i.parent)
                        except ValueError:
                            s += str(g.nonactive().path)
                    g.msg.add(s)
                    g.pathrefresh()
                except shutil.SameFileError:
                    g.msg.add(name + ': 送り先に同名のファイルが既に存在します')
                except shutil.Error:
                    g.msg.add(name + ': エラー')
                except:
                    traceback.print_exc()

    def trash(self):
        self.do('trash', lambda x, y: send2trash(str(x)),
                '\n(注意！ LAN内ファイルは完全削除されます)',
                _type = 1)

    def copy(self):
        self.do('copy', shutil.copy2, _type = 2)

    def move(self):
        self.do('move', shutil.move, _type = 2)

    def symbolic(self):
        if self.selects == []:
            self.symbolicone()
        else:
            self.symbolicselects()

    def filemask(self):
        dlg = wx.TextEntryDialog(None, 'current mask(glob): %s' % self.mask)
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_CANCEL: return
        self.setmask(dlg.GetValue())

    def shellcmd(self):
        txt = 'cmd?'
        txt += '\n(DYNAマクロ ヒント: $ FCXD OP ~$)'
        dlg = wx.TextEntryDialog(None, txt)
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_CANCEL: return

        a = dlg.GetValue()
        # DYNAのマクロ
        a = a.replace('$F',  str(self.linepath()))
        a = a.replace('$C',  self.linepath().name)
        a = a.replace('$X',  self.linepath().stem)
        a = a.replace('$D',  str(self.path))

        a = a.replace('$OF', str(g.nonactive().linepath()))
        a = a.replace('$OC', g.nonactive().linepath().name)
        a = a.replace('$OX', g.nonactive().linepath().stem)
        a = a.replace('$OD', str(g.nonactive().path))

        a = a.replace('$PF', ' '.join(str(i) for i in self.selects))
        a = a.replace('$PC', ' '.join(i.name for i in self.selects))
        a = a.replace('$PX', ' '.join(i.stem for i in self.selects))

        a = a.replace('$~',  __file__)
        a = a.replace('$$',  '$')

        s = ' '.join([g.shell, g.shellcmdflag, a])
        os.chdir(self.path)
        b = subprocess.check_output(s, encoding = lib.osenc())
        g.msg.add(b)
        g.pathrefresh()

    def eval(self):
        dlg = wx.TextEntryDialog(None, 'eval')
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_CANCEL: return

        g.msg.add(str(eval(dlg.GetValue())))

    def exec(self):
        dlg = wx.TextEntryDialog(None, 'exec')
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_CANCEL: return

        exec(dlg.GetValue())

    def sort(self):
        txt = 'sort?'
        txt += '\n(ヒント： gnt)'
        dlg = wx.TextEntryDialog(None, txt)
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_CANCEL: return

        self.setsort(dlg.GetValue())

    def search(self):
        dlg = wx.TextEntryDialog(None, 'search?')
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_CANCEL: return

        self.searching = dlg.GetValue()
        self.next()

    def next(self):
        if not self.searching: return

        if all([self.searching not in self.name(i) for i in self.files]):
            g.msg.add('パターンは見つかりませんでした: %s' % self.searching)
            return

        while 1:
            if self.line == len(self.files) - 1:
                g.msg.add('下まで検索したので上に戻ります')
                self.line = 0
            else:
                self.linedown()

            if self.searching in self.name(self.linepath()):
                return

    def next_ops(self):
        if not self.searching: return

        if all([self.searching not in self.name(i) for i in self.files]):
            g.msg.add('パターンは見つかりませんでした: %s' % self.searching)
            return

        while 1:
            if self.line == 0:
                g.msg.add('上まで検索したので下に戻ります')
                self.line = len(self.files) - 1
            else:
                self.lineup()

            if self.searching in self.name(self.linepath()):
                return

    def mru(self):
        self.setpath(SpPath('*MRU*'))
        self.files = list(g.history)
        self.files.reverse()

    def es(self):
        self.setpath(SpPath('*Everything*'))

        dlg = wx.TextEntryDialog(None, 'everything?(es.exe)')
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_CANCEL: return
        a = subprocess.check_output('es ' + dlg.GetValue(), encoding = lib.osenc())
        a = a.split('\n')[:-1]
        self.files = [Path(i) for i in a]
        # self.name = lambda x: x.path

    def imgstart(self, dummy = 0):
        g.imgmode = True
        g.openimg(self.linepath())

    def open_newtab(self):
        try:
            act = g.list1.active
            path = Path(str(g.active().linepath()))
            self.newtab()

            if act:
                g.list1.setpath(path)
            else:
                g.list2.setpath(path)
                g.otherside()

            if path.parent == g.active().path:
                g.notebook.close()
                g.msg.add('ACCESS DENIED [%s]' % self.linepath())
        except NotADirectoryError:
            g.msg.add('NotADirectoryError')

    def newtab(self):
        path1 = g.list1.path
        path2 = g.list2.path
        line1 = g.list1.line
        line2 = g.list2.line
        g.notebook.new()
        g.list1.setpath(path1)
        g.list2.setpath(path2)
        g.list1.line = line1
        g.list2.line = line2

class InfoDraw(wx.Panel):

    def __init__(self, parent, data):
        super().__init__(parent)
        self.data = data

        self.SetBackgroundColour(g.color_bg)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.onpaint)
        self.Bind(wx.EVT_CHAR_HOOK, lambda e: wx.PostEvent(g.frame, e))

    def onpaint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        dc.SetFont(g.font)
        dc.SetTextForeground(g.color_info)

        w = self.GetClientSize()[0]
        h = dc.GetTextExtent('a')[1]

        s = self.data.path.as_posix()

        # 横サイズが足りない場合は右揃え
        lim = w // dc.GetTextExtent('a')[0]

        if not isinstance(s, SpPath) and lim <= lib.mblen(s):
            while 1:
                if lim >= lib.mblen(s):
                    break
                s = s[1:]

        #s = s[max(0, lib.mblen(s) - w // dc.GetTextExtent('a')[0] ):]

        dc.DrawText(str(s), 0, 0)

        dc.DrawText('%d/%d'
                % (self.data.line + 1, len(self.data.files)),
                0, h)

class Msg(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour(g.color_bg)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.onpaint)
        self.Bind(wx.EVT_CHAR_HOOK, lambda e: wx.PostEvent(g.frame, e))

        self.clear()

    def clear(self):
        self.lst = ["" for i in range(g.msgmax)]
        self.add('Ready')

    def looknum(self):
        return self.GetClientSize()[1] // lib.textextent(g.font)[1]

    def onpaint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        dc.SetFont(g.font)

        h = dc.GetTextExtent('a')[1]

        dc.SetPen(wx.Pen(g.color_fg))
        dc.SetTextForeground(g.color_fg)

        for i in range(self.looknum()):
            dc.DrawText(self.lst[g.msgmax - self.looknum() + i], 0, h * i)

    def add(self, s):
        self.lst.pop(0)
        self.lst.append(s)

class Frame(wx.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Centre()
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.onsashchanged)
        self.Bind(wx.EVT_PAINT, self.onpaint)
        self.Bind(wx.EVT_SIZE, self.onsize)
        self.CreateStatusBar()
        self.SetBackgroundColour(g.color_bg)

    def onsize(self, evt):
        g.setmsgheight()
        g.refresh()
    
    def onsashchanged(self, evt):
        g.refresh()

    def onpaint(self, evt):
        pass

class MainWindow(wx.Panel):

    def __init__(self):
        super().__init__(g.notebook, wx.ID_ANY)
        self.sp1 = wx.SplitterWindow(self)
        self.sp2 = wx.SplitterWindow(self.sp1)
        self.sp3 = wx.SplitterWindow(self.sp2)
        self.sp4 = wx.SplitterWindow(self.sp2)

        self.list1     = List(self.sp3, True, g.history)
        self.list2     = List(self.sp4, False, g.history)
        self.infodraw1 = InfoDraw(self.sp3, self.list1)
        self.infodraw2 = InfoDraw(self.sp4, self.list2)
        self.msg       = Msg(self.sp1)

        self.sp1.SplitHorizontally(self.sp2, self.msg)
        self.sp2.SplitVertically(self.sp3, self.sp4)
        self.sp3.SplitHorizontally(self.infodraw1, self.list1, lib.textextent(g.font)[1] * 2)
        self.sp4.SplitHorizontally(self.infodraw2, self.list2, lib.textextent(g.font)[1] * 2)

        self.SetBackgroundColour(g.color_bg)

    def do(self):

        g.sp1 = self.sp1
        g.sp2 = self.sp2
        g.sp3 = self.sp3
        g.sp4 = self.sp4
        g.list1 = self.list1
        g.list2 = self.list2
        g.infodraw1 = self.infodraw1
        g.infodraw2 = self.infodraw2
        g.msg = self.msg
        g.mainwindow = self

class Notebook(wx.aui.AuiNotebook):

    def __init__(self):
        super().__init__(g.frame, wx.ID_ANY)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.onchanged)
        #self.SetBackgroundColour(g.color_bg)
        g.windows = []

    def onchanged(self, evt):
        g.windows[self.GetSelection()].do()
        g.refresh()

    def add(self, i):
        g.windows.insert(i, MainWindow())
        self.InsertPage(i, g.windows[i], 'Tab')

        self.change(i)

        g.sashinit()
        g.refresh()

    def new(self):
        self.add(self.index() + 1)

    def change(self, i):
        self.SetSelection(i)
        g.windows[i].do()

    def index(self):
        return self.GetSelection()

    def close(self):
        if not self.GetPageCount() <= 1:
            self.DeletePage(self.index())
            g.windows[self.index()].do()

    def next(self):
        if self.GetPageCount() == self.index() + 1:
            self.change(0)
        else:
            self.change(self.index() + 1)

    def previous(self):
        if self.index() == 0:
            self.change(self.GetPageCount() - 1)
        else:
            self.change(self.index() - 1)

def main():
    g.app = wx.App()

    g.frame = Frame(None, wx.ID_ANY, 'bandit')

    if g.transparency >= 0:
        g.frame.SetTransparent(g.transparency)

    g.notebook = Notebook()

    g.keymap = keymap.Keymap()
    g.keymap.binded(g.frame)


    g.font = wx.Font(9,
            wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
            faceName = 'MS Gothic')

    g.notebook.new()

    g.frame.SetSize(g.defaultsize)
    g.sashinit()
    g.frame.Show()
