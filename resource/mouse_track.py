import ctypes as ct
import ctypes.wintypes as w

# Constants derived from WinSDK headers.
RIDEV_INPUTSINK = 0x00000100
RID_HEADER = 0x10000005
RID_INPUT = 0x10000003
WM_INPUT = 0x00FF
HID_USAGE_PAGE_GENERIC = 0x01
HID_USAGE_GENERIC_MOUSE = 0x02
RIDEV_REMOVE = 0x00000001

# Types not available in ctypes.wintypes
LRESULT = ct.c_ssize_t
HCURSOR = ct.c_void_p
HRAWINPUT = ct.c_void_p

# callback prototype
WNDPROC = ct.WINFUNCTYPE(LRESULT, w.HWND, w.UINT, w.WPARAM, w.LPARAM)

# Use wintypes that exactly match MSDN documentation when possible.
class RAWINPUTDEVICE(ct.Structure):
    _fields_ = (('usUsagePage', w.USHORT),
                ('usUsage', w.USHORT),
                ('dwFlags', w.DWORD),
                ('hwndTarget', w.HWND))

class RAWINPUTHEADER(ct.Structure):
    _fields_ = (('dwType', w.DWORD),
                ('dwSize', w.DWORD),
                ('hDevice', w.HANDLE),
                ('wParam', w.WPARAM))

class DUMMYSTRUCTNAME(ct.Structure):
    _fields_ = (('usButtonFlags', w.USHORT),
                ('usButtonData', w.USHORT))

class DUMMYUNIONNAME(ct.Union):
    _anonymous_ = 's',
    _fields_ = (('ulButtons', w.ULONG),
                ('s', DUMMYSTRUCTNAME))
class RAWMOUSE(ct.Structure):
    _anonymous_ = 'u',
    _fields_ = (('usFlags', w.USHORT),
                ('u', DUMMYUNIONNAME),
                ('ulRawButtons', w.ULONG),
                ('lLastX', w.LONG),
                ('lLastY', w.LONG),
                ('ulExtraInformation', w.ULONG))

class RAWKEYBOARD(ct.Structure):
    _fields_ = (('MakeCode', w.USHORT),
                ('Flags', w.USHORT),
                ('Reserved', w.USHORT),
                ('vKey', w.USHORT),
                ('Message', w.UINT),
                ('ExtraInformation', w.ULONG))

class RAWHID(ct.Structure):
    _fields_ = (('dwSizeHid', w.DWORD),
                ('dwCount', w.DWORD),
                ('bRawData', w.BYTE * 1))

class DUMMYUNIONNAME(ct.Union):
    _fields_ = (('mouse', RAWMOUSE),
                ('keyboard', RAWKEYBOARD),
                ('hid', RAWHID))
class RAWINPUT(ct.Structure):
    _fields_ = (('header', RAWINPUTHEADER),
                ('data', DUMMYUNIONNAME))

class WNDCLASSW(ct.Structure):
    _fields_ = (('style', w.UINT),
                ('lpfnWndProc', WNDPROC),
                ('cbClsExtra', ct.c_int),
                ('cbWndExtra', ct.c_int),
                ('hInstance', w.HINSTANCE),
                ('hIcon', w.HICON),
                ('hCursor', HCURSOR),
                ('hbrBackground', w.HBRUSH),
                ('lpszMenuName', w.LPCWSTR),
                ('lpszClassName', w.LPCWSTR))

# Error checking handlers post-process function results
# and raise exceptions if the API fails.
def rawinputcheck(result, func, args):
    if result == w.UINT(-1).value:
        raise ct.OSError('GetRawInputData failed')
    return result

def zerocheck(result, func, args):
    if result == 0:
        raise ct.WinError(ct.get_last_error())
    return result

def nullcheck(result, func, args):
    if result is None:
        raise ct.WinError(ct.get_last_error())
    return result

def boolcheck(result, func, args):
    if not result:
        raise ct.WinError(ct.get_last_error())
    return None

# use_last_error=True/get_last_error() capture and return the GetLastError() immediately after the API call.
user32 = ct.WinDLL('user32', use_last_error=True)
# Best practice: fully declare arguments and return types.
# .errcheck handlers help by raising exceptions on error.
GetRawInputData = user32.GetRawInputData
GetRawInputData.argtypes = HRAWINPUT, w.UINT, w.LPVOID, w.PUINT, w.UINT
GetRawInputData.restype = w.UINT
GetRawInputData.errcheck = rawinputcheck
DefWindowProcW = user32.DefWindowProcW
DefWindowProcW.argtypes = w.HWND, w.UINT, w.WPARAM, w.LPARAM
DefWindowProcW.restype = LRESULT
RegisterClassW = user32.RegisterClassW
RegisterClassW.argtypes = ct.POINTER(WNDCLASSW),
RegisterClassW.restype = w.ATOM
RegisterClassW.errcheck = zerocheck
CreateWindowExW = user32.CreateWindowExW
CreateWindowExW.argtypes = w.DWORD, w.LPCWSTR, w.LPCWSTR, w.DWORD, ct.c_int, ct.c_int, ct.c_int, ct.c_int, w.HWND, w.HMENU, w.HINSTANCE, w.LPVOID
CreateWindowExW.restype = w.HWND
CreateWindowExW.errcheck = nullcheck
RegisterRawInputDevices = user32.RegisterRawInputDevices
RegisterRawInputDevices.argtypes = ct.POINTER(RAWINPUTDEVICE), w.UINT, w.UINT
RegisterRawInputDevices.restype = w.BOOL
RegisterRawInputDevices.errcheck = boolcheck
GetMessageW = user32.GetMessageW
GetMessageW.argtypes = ct.POINTER(w.MSG), w.HWND, w.UINT, w.UINT
GetMessageW.restype = w.BOOL
GetMessageW.errcheck = boolcheck
TranslateMessage = user32.TranslateMessage
TranslateMessage.argtypes = ct.POINTER(w.MSG),
TranslateMessage.restype = w.BOOL
DispatchMessageW = user32.DispatchMessageW
DispatchMessageW.argtypes = ct.POINTER(w.MSG),
DispatchMessageW.restype = LRESULT

def handle_raw_input(lparam):
    global sum_move
    raw_input_data = RAWINPUT()
    raw_input_size = w.UINT(ct.sizeof(raw_input_data))

    # Get raw input data
    GetRawInputData(HRAWINPUT(lparam), RID_INPUT, ct.byref(raw_input_data), ct.byref(raw_input_size), ct.sizeof(RAWINPUTHEADER))
    if raw_input_data.header.dwType == 0:
        sum_move=sum_move+raw_input_data.data.mouse.lLastX

@WNDPROC  # decorating a callback with its prototype makes it callable from C
def wnd_proc(hwnd, msg, wparam, lparam):
    if msg == WM_INPUT:
        handle_raw_input(lparam)
    return DefWindowProcW(hwnd, msg, wparam, lparam)

# Main loop
# Create a message loop to handle WM_INPUT messages
wndclass = WNDCLASSW()
wndclass.lpfnWndProc = wnd_proc
wndclass.lpszClassName = 'RawInputClass'
RegisterClassW(ct.byref(wndclass))

hwnd = CreateWindowExW(0, 'RawInputClass', 'Raw Input Window', 0, 0, 0, 0, 0, None, None, None, None)

# Register raw input device
#rid = RAWINPUTDEVICE(HID_USAGE_PAGE_GENERIC, HID_USAGE_GENERIC_MOUSE, RIDEV_INPUTSINK, hwnd)
#RegisterRawInputDevices(ct.byref(rid), 1, ct.sizeof(rid))

# Run the message loop
#sum_move=0
