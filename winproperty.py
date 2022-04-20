# https://stackoverflow.com/questions/7985122/

import ctypes
import ctypes.wintypes

SEE_MASK_NOCLOSEPROCESS = 0x00000040
SEE_MASK_INVOKEIDLIST = 0x0000000C

class SHELLEXECUTEINFO(ctypes.Structure):
    _fields_ = (
        ("cbSize", ctypes.wintypes.DWORD),
        ("fMask", ctypes.c_ulong),
        ("hwnd", ctypes.wintypes.HANDLE),
        ("lpVerb", ctypes.c_char_p),
        ("lpFile", ctypes.c_char_p),
        ("lpParameters", ctypes.c_char_p),
        ("lpDirectory", ctypes.c_char_p),
        ("nShow", ctypes.c_int),
        ("hInstApp", ctypes.wintypes.HINSTANCE),
        ("lpIDList", ctypes.c_void_p),
        ("lpClass", ctypes.c_char_p),
        ("hKeyClass", ctypes.wintypes.HKEY),
        ("dwHotKey", ctypes.wintypes.DWORD),
        ("hIconOrMonitor", ctypes.wintypes.HANDLE),
        ("hProcess", ctypes.wintypes.HANDLE),
    )

ShellExecuteEx = ctypes.windll.shell32.ShellExecuteEx
ShellExecuteEx.restype = ctypes.wintypes.BOOL

def winproperty(filename):

    sei = SHELLEXECUTEINFO()
    sei.cbSize = ctypes.sizeof(sei)
    sei.lpVerb = "properties".encode('shiftjis')
    sei.lpFile = str(filename).encode('shiftjis')
    sei.fMask  = SEE_MASK_NOCLOSEPROCESS | SEE_MASK_INVOKEIDLIST
    # sei.nShow = 1

    ShellExecuteEx(ctypes.byref(sei))
