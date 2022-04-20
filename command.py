import wx

def main():
    g.keymap.end = lambda: g.refresh()

    # shift ctrl altの順番でないとダメ あるいは同時押しだめな可能性も

    g.keymap.add(wx.WXK_DOWN,           lambda: g.active().linedown())
    g.keymap.add(wx.WXK_UP,             lambda: g.active().lineup())
    g.keymap.add(wx.WXK_LEFT,           lambda: g.active().back())
    g.keymap.add(wx.WXK_RIGHT,          lambda: g.active().enter())
    g.keymap.add(wx.WXK_RETURN,         lambda: g.active().open())
    g.keymap.add(wx.WXK_BACK,           lambda: g.active().back())
    g.keymap.add(ord('J'),              lambda: g.active().linedown())
    g.keymap.add(ord('K'),              lambda: g.active().lineup())
    g.keymap.add(ord('H'),              lambda: g.active().back())
    g.keymap.add(ord('L'),              lambda: g.active().enter())
    g.keymap.add(ord('J'),     'shift', lambda: g.notebook.previous())
    g.keymap.add(ord('K'),     'shift', lambda: g.notebook.next())
    g.keymap.add(ord('L'),     'shift', lambda: g.active().open_newtab())
    g.keymap.add(ord('D'),     'ctrl',  lambda: g.active().linehalfdown())
    g.keymap.add(ord('U'),     'ctrl',  lambda: g.active().linehalfup())
    g.keymap.add(wx.WXK_PAGEDOWN,       lambda: g.active().linehalfdown())
    g.keymap.add(wx.WXK_PAGEUP,         lambda: g.active().linehalfup())
    g.keymap.add(ord('G'),              lambda: g.active().linetop())
    g.keymap.add(ord('G'),     'shift', lambda: g.active().linebottom())
    g.keymap.add(ord('O'),              lambda: g.sync_ops())
    g.keymap.add(ord('E'),              lambda: g.active().edit())
    g.keymap.add(ord('V'),              lambda: g.active().open())
    g.keymap.add(ord('L'),     'ctrl',  lambda: g.msg.clear())
    g.keymap.add(wx.WXK_TAB,            lambda: g.otherside())
    g.keymap.add(wx.WXK_ESCAPE,         lambda: g.frame.Close(True))
    g.keymap.add(wx.WXK_SPACE,          lambda: g.active().lineselect())
    g.keymap.add(wx.WXK_SPACE, 'shift', lambda: g.active().lineselect_ops())
    g.keymap.add(ord('X'),              lambda: g.active().lineclear())
    g.keymap.add(ord('A'),              lambda: g.active().allfileselect())
    g.keymap.add(ord('A'),     'shift', lambda: g.active().allselect())
    g.keymap.add(ord('T'),              lambda: g.active().terminal())
    g.keymap.add(ord('Y'),              lambda: g.active().clip_linepath())
    g.keymap.add(ord('Y'),     'shift', lambda: g.active().clip_linename())
    g.keymap.add(ord('T'),     'shift', lambda: g.active().touch())
    g.keymap.add(ord('T'),     'ctrl',  lambda: g.active().newtab())
    g.keymap.add(ord('I'),     'shift', lambda: g.active().info())
    g.keymap.add(ord('I'),              lambda: g.active().winproperty())
    g.keymap.add(ord('G'),     'ctrl',  lambda: g.active().goto())
    g.keymap.add(ord('W'),              lambda: g.active().mkdir())
    g.keymap.add(ord('W'),     'ctrl',  lambda: g.notebook.close())
    g.keymap.add(ord('R'),              lambda: g.active().rename())
    g.keymap.add(ord('R'),     'ctrl',  lambda: g.active().rightclick())
    g.keymap.add(ord('D'),              lambda: g.active().trash())
    g.keymap.add(ord('C'),              lambda: g.active().copy())
    g.keymap.add(ord('M'),              lambda: g.active().move())
    g.keymap.add(ord('C'),     'shift', lambda: g.active().duplicate())
    g.keymap.add(ord('U'),              lambda: g.active().mru())
    g.keymap.add(ord('/'),              lambda: g.active().search())
    g.keymap.add(ord('N'),              lambda: g.active().next())
    g.keymap.add(ord('N'),     'shift', lambda: g.active().next_ops())
    g.keymap.add(ord('F'),              lambda: g.active().filemask())
    g.keymap.add(ord('S'),              lambda: g.active().sort())
    g.keymap.add(ord('Z'),              lambda: g.clone())
    g.keymap.add(ord('1'),     'shift', lambda: g.active().shellcmd())
    g.keymap.add(ord('2'),     'shift', lambda: g.active().eval())
    g.keymap.add(ord('3'),     'shift', lambda: g.active().exec())
    g.keymap.add(ord('7'),              lambda: g.toggle_imgmode())
    g.keymap.add(ord('8'),              lambda: g.active().es())
    g.keymap.add(ord('Q'),              lambda: g.imgquit())
    g.keymap.add(ord('0'),              lambda: g.sashinit())
