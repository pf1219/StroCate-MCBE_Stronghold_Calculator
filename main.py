# Import modules
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
import pyperclip, math, csv, os, webbrowser, msvcrt, time, ctypes, string, random
from functools import partial
from bindglobal import BindGlobal as BG

# Pyinstaller setting
def path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path,relative_path)

# Import data
data=list(csv.reader(open(path("resource/pdf.csv"))))
pdf=[float(data[i][0]) for i in range(len(data))]
data=list(csv.reader(open(path("resource/vilprob16.csv"))))
vilprob16=[float(data[i][0]) for i in range(len(data))]+[0]*(1000-len(data))
data=list(csv.reader(open(path("resource/vilprob.csv"))))
vilprob=[float(data[i][0]) for i in range(len(data))]+[0]*(1000-len(data))

data=list(csv.reader(open(path("resource/distprob.csv"))))
distprob=[float(data[i][0]) for i in range(len(data))]
data=list(csv.reader(open(path("resource/distprob16.csv"))))
distprob16=[float(data[i][0]) for i in range(len(data))]

# Import setting
# 0 align, 1 pixel, 2 pixper, 3 mode, 4 coordinate, 5 str within, 6 mean, 7 version, 8 prior, 9 search rad
# 10~12 mouse track, 13 highlight color, 14 manual input
preset_name=[]
preset_default=[]
if "StroCate_setting.csv" in os.listdir():
    setting_data=list(csv.reader(open("StroCate_setting.csv")))
    default=setting_data[0]
else:
    setting_data=[]
    default=["0.3","0.1","0.1","Coord+Coord","Copy+Paste","12","Show","1.18.30+","Simulation","10000",0,0,0,0,"Show coordinate"]
while len(default)<14:
    default.append(0)
for i in range(10,14):
    default[i]=float(default[i])
if len(default)<15:
    default.append("Show coordinate")
    
default_hotkey=["[","]","=","F9","F10","F4","s p","s m","p","m","d c","d v","d x","d n","d m","s i"]
for i in range(len(default_hotkey)):
    if len(default)<(16+i):
        default.append(default_hotkey[i])

# version parity
if default[14]=="Copy+Paste":
    default[14]="Copy coordinate UI"

# Load preset
if len(setting_data)<2:
    cur_hotkey=[]
    for i in range(len(default_hotkey)):
        try:
            cur_hotkey.append(default[15+i])
        except:
            cur_hotkey.append(default_hotkey[i])
else:
    cur_hotkey=setting_data[1]
    for i in range(len(default_hotkey)):
        try:
            cur_hotkey[i]
        except:
            cur_hotkey.append(default_hotkey[i])
            
if len(setting_data)>2:
    for i in range(3,len(setting_data)):
        preset_name.append(setting_data[i][0])
        preset_default.append(setting_data[i][1:])

pt=[]
pt_mode=[]
pt_prec=[]
pt_err=[]
pt_coord=[]
pt_pixel=[]
pt_pixel_err=[]
pt_manual=[]

# Functions
def disprob(x):
    a=100*x
    return(f'{a:.2f}'+"%")
def disprob2(x):
    a=100*x
    return(f'{a:.1f}'+"%")
def rgb_to_hex(r, g, b):
  return '#{:02X}{:02X}{:02X}'.format(r, g, b)

user32=ctypes.windll.user32
def clear_input_buffer():
    msg=ctypes.wintypes.MSG()
    while user32.PeekMessageW(ctypes.byref(msg), 0, 0x0100, 0x0109, 0x0001):
        pass
    while user32.PeekMessageW(ctypes.byref(msg), 0, 0x0200, 0x020E, 0x0001):
        pass

# Window
win=tk.Tk()
win.title("/StroCate: Bedrock Stronghold Calculator")
sw=win.winfo_screenwidth()
sh=win.winfo_screenheight()
move_x=sw-420
move_y=sh-340
win.geometry("400x320+"+str(move_x)+"+30")
win.resizable(False,False)
win.attributes("-topmost",True)
win.iconbitmap(path("resource/icon.ico"))

sys_default = font.nametofont("TkDefaultFont")
sys_family = sys_default.cget("family")
ft=font.Font(family=sys_family,size=10)
ft2=font.Font(family=sys_family,size=10,underline=True)
ft_small=font.Font(family=sys_family,size=8)
win.option_add("*Font",ft)

# screen reading setup
class Coords(ctypes.Structure):
    _fields_=[("x",ctypes.c_int),("y",ctypes.c_int),("z",ctypes.c_int),("valid",ctypes.c_int)]
dll3=ctypes.CDLL(path("resource/screen.dll"))
READCOORD=dll3.read_coords
READCOORD.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.POINTER(ctypes.c_int),ctypes.c_int]
READCOORD.restype=Coords

BTCALC=dll3.calculate_bt
BTCALC.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.POINTER(ctypes.c_int)]
BTCALC.restype=ctypes.c_int

OutputArrayType=ctypes.c_int*100
debug=OutputArrayType()
OutputArrayType=ctypes.c_int*6
btres=OutputArrayType()

# dll
class Result(ctypes.Structure):
    _fields_=[("prob",ctypes.c_double),("ratio",ctypes.c_double),("x",ctypes.c_int),("z",ctypes.c_int)]

dll2=ctypes.CDLL(path("resource/update.dll"))
IFVILPROB=dll2.if_vil_prob
IFVILPROB.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.POINTER(Result),ctypes.c_int,ctypes.POINTER(ctypes.c_double)]
IFVILPROB.restype=ctypes.c_double

# angle measurement setup
mouse_dll=ctypes.CDLL(path("resource/mouse.dll"))

START_TRACK=mouse_dll.start_tracking
START_TRACK.argtypes=[]
START_TRACK.restype=None

GET_TRACK=mouse_dll.get_mouse_data
GET_TRACK.argtypes=[ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_int)]
GET_TRACK.restype=None

RESET_TRACK=mouse_dll.reset_data
RESET_TRACK.argtypes=[]
RESET_TRACK.restype=None

STOP_TRACK=mouse_dll.stop_tracking
STOP_TRACK.argtypes=[]
STOP_TRACK.restype=None

# Info bar
def set_infobar():
    if calibrating==1:
        dis="Calibrating mouse tracking. Press F9, turn 90 degree and press F10"
        fgcol="#0000FF"
    elif calibrating==2:
        dis="Calibrating mouse tracking (F9 pressed). Turn 90 degree and press F10"
        fgcol="#0000FF"
    else:
        dis="Align: "+str(cur_error_angle.get())+" / "
        dis=dis+"PixPer: "+str(cur_pixel_perfect.get())+" / "
        k=cinp_display[cinp_list.index(cur_cinp.get())]
        dis=dis+k+" / "
        dis=dis+game_version.get()+" / "
        dis=dis+"~"+str(cur_within.get())
        fgcol="#888888"
    option_info.config(text=dis,fg=fgcol)
option_info=tk.Label(win,text="Align: 0.3 / PixPer: 0.1 / Copy+Paste / 1.18.30+ / ~4000",font=ft_small,fg="#888888")
option_info.place(x=0,y=278)

# Menu bar
menubar=tk.Menu(win)
calibrationbar=tk.Menu(menubar,tearoff=False)
menubar.add_cascade(label="Accuracy",menu=calibrationbar)
inputbar=tk.Menu(menubar,tearoff=False)
menubar.add_cascade(label="Input",menu=inputbar)
settingbar=tk.Menu(menubar,tearoff=False)
menubar.add_cascade(label="Options",menu=settingbar)
presetbar=tk.Menu(menubar,tearoff=False)
menubar.add_cascade(label="Preset",menu=presetbar)
displaybar=tk.Menu(menubar,tearoff=False)
menubar.add_cascade(label="Display",menu=displaybar)
hotkeybar=tk.Menu(menubar,tearoff=False)
menubar.add_cascade(label="Hotkey",menu=hotkeybar)
about=tk.Menu(menubar,tearoff=False)
menubar.add_cascade(label="About",menu=about)

# Preset
def save_preset():
    global preset_name, preset_default
    current_default=[str(cur_error_angle.get()),str(cur_error_pixel.get()),str(cur_pixel_perfect.get())]
    current_default=current_default+[cur_input_mode.get(),cur_cinp.get(),str(cur_pc.get()),cur_dismean.get()]
    current_default=current_default+[game_version.get(),cur_prior.get(),str(cur_within.get()),cur_manual_input.get()]

    current_preset_name="{}/{}".format(game_version.get(),cur_input_mode.get())
    current_preset_ind=1
    while True:
        if "{} {}".format(current_preset_name,current_preset_ind) not in preset_name:
            break
        else:
            current_preset_ind=current_preset_ind+1
    preset_name.append("{} {}".format(current_preset_name,current_preset_ind))
    preset_default.append(current_default)
    update_preset_list()
def update_preset_list():
    npreset=presetlist.index("end")
    if isinstance(npreset,int):
        for i in range(npreset+1):
            presetlist.delete(0,npreset)
    for i in range(len(preset_name)):
        presetlist.add_cascade(label=preset_name[i],command=partial(apply_preset,preset_name[i]))
def apply_preset(selected_preset):
    print(["APPLY",selected_preset])
    cur_preset=preset_default[preset_name.index(selected_preset)]
    cur_error_angle.set(float(cur_preset[0]))
    cur_error_pixel.set(float(cur_preset[1]))
    cur_pixel_perfect.set(float(cur_preset[2]))
    cur_input_mode.set(cur_preset[3])
    cur_cinp.set(cur_preset[4])
    cur_pc.set(int(cur_preset[5]))
    cur_dismean.set(cur_preset[6])
    game_version.set(cur_preset[7])
    cur_prior.set(cur_preset[8])
    cur_within.set(int(cur_preset[9]))
    cur_manual_input.set(cur_preset[10])
    set_mode()
    set_prior(0)
    set_pc(cur_pc.get())
    
presetbar.add_cascade(label="Save current setting",command=save_preset)
presetlist=tk.Menu(presetbar,tearoff=False)
presetbar.add_cascade(label="Apply preset",menu=presetlist)
update_preset_list()

# Help
hotkeylist=tk.Menu(hotkeybar,tearoff=False)
hotkeybar.add_cascade(label="Hotkeys",menu=hotkeylist)

# About
about.add_cascade(label="/StroCate: Bedrock Stronghold Calculator")
about.add_cascade(label="Made by LHS1219")
about.add_cascade(label="Version 2.10.3 (2026.06.22.)")
about.add_separator()
def open_github():
    webbrowser.open("https://github.com/pf1219/StroCate-MCBE_Stronghold_Calculator")
def open_youtube():
    webbrowser.open("https://www.youtube.com/@lhs1219")
about.add_cascade(label="Open Github",command=open_github)
about.add_cascade(label="Open Youtube",command=open_youtube)

# Error options
## Align
acc_list=[0.03,0.05,0.075,0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.75,1.0,1.5,2.0,2.5,3.0,4.0]
cur_error_angle=tk.DoubleVar()
cur_error_angle.set(float(default[0]))
alignerrormenu=tk.Menu(calibrationbar,tearoff=False)
calibrationbar.add_cascade(label="Eye align error",menu=alignerrormenu)
for i in range(len(acc_list)):
    alignerrormenu.add_radiobutton(label=acc_list[i],variable=cur_error_angle,value=acc_list[i],command=set_infobar)

## Pixel
pixel_list=[0.01,0.03,0.05,0.075,0.1,0.15,0.2,0.3]
cur_error_pixel=tk.DoubleVar()
cur_error_pixel.set(float(default[1]))
pixelerrormenu=tk.Menu(calibrationbar,tearoff=False)
calibrationbar.add_cascade(label="Pixel count error",menu=pixelerrormenu)
for i in range(len(pixel_list)):
    pixelerrormenu.add_radiobutton(label=pixel_list[i],variable=cur_error_pixel,value=pixel_list[i],command=set_infobar)

## Pixel Perfect
pixel_perfect_list=[0.03,0.06,0.075,0.1,0.15,0.2,0.25,0.3]
cur_pixel_perfect=tk.DoubleVar()
cur_pixel_perfect.set(float(default[2]))
pixelperfectmenu=tk.Menu(calibrationbar,tearoff=False)
calibrationbar.add_cascade(label="Pixel perfect error",menu=pixelperfectmenu)
for i in range(len(pixel_perfect_list)):
    pixelperfectmenu.add_radiobutton(label=pixel_perfect_list[i],variable=cur_pixel_perfect,value=pixel_perfect_list[i],command=set_infobar)

## Mouse Tracking
def start_calibration():
    print("START CALIBRATION")
    global calibrating
    calibrating=1
    set_infobar()
def clear_calibration():
    global default, track_angle, track_move
    default[10]=0
    default[11]=0
    default[12]=0
    mousecalibratemenu.delete(2,3)
    mousecalibratemenu.add_cascade(label="Mean: "+f'{default[10]:.1f}')
    mousecalibratemenu.add_cascade(label="SD: "+f'{default[11]:.1f}')
    if cur_input_mode.get()=="Mouse Tracking":
        track_dis.config(text="Add calibration first")
        start_calibration()
        track_angle=0
        track_move=0
        c2_dis.config(text="Angle: 0 Deg")

mousecalibratemenu=tk.Menu(calibrationbar,tearoff=False)
calibrationbar.add_cascade(label="Mouse tracking",menu=mousecalibratemenu)
mousecalibratemenu.add_cascade(label="Add calibration data",command=start_calibration)
mousecalibratemenu.add_cascade(label="Clear calibration data",command=clear_calibration)
mousecalibratemenu.add_cascade(label="Mean: "+f'{default[10]:.1f}')
mousecalibratemenu.add_cascade(label="SD: "+f'{default[11]:.1f}')
measuring=0
track_angle=0

# Input options
## Mode
def set_mode():
    global x1,x2,z1,z2, measuring, track_move, track_angle, calibrating
    c1_but.place_forget()
    c2_but.place_forget()
    x1_inp.place_forget()
    x2_inp.place_forget()
    z1_inp.place_forget()
    z2_inp.place_forget()
    facing_dir.place_forget()
    pixel_inp.place_forget()
    pixel_dis.place_forget()
    track_dis.place_forget()
    c1_dis.place(x=5,y=7)
    c2_dis.place(x=5,y=37)
    add_but.place(x=265,y=19)
    calibrating=0
    set_infobar()
    if cur_cinp.get()=="Copy+Paste" or cur_cinp.get()=="Copy+Paste (Corner)" or cur_cinp.get()=="Show Coordinate":
        c1_but.place(x=200,y=5)
        c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
        if cur_input_mode.get()=="Coord+Coord" or cur_input_mode.get()=="Pixel Perfect":
            x2,z2=0,0
            c2_dis.config(text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")
            c2_but.place(x=200,y=35)
        elif cur_input_mode.get()=="Corner+Facing":
            c2_dis.config(text="Direction:")
            facing_dir.set("Facing")
            facing_dir.place(x=90,y=37)
            pixel_inp.delete(0,tk.END)
            pixel_inp.insert(0,"Pixel")
            pixel_inp.place(x=175,y=38)
            if round(x1%1,1) not in [0.3,0.7] or round(z1%1,1) not in [0.3,0.7]:
                x1,z1=0,0
                c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
    else:
        x1_inp.delete(0,tk.END)
        x2_inp.delete(0,tk.END)
        z1_inp.delete(0,tk.END)
        z2_inp.delete(0,tk.END)
        x1_inp.place(x=80,y=8)
        z1_inp.place(x=160,y=8)
        x1,x2,z1,z2=0,0,0,0
        c1_dis.config(text="Coord 1:")
        if cur_input_mode.get()=="Coord+Coord" or cur_input_mode.get()=="Pixel Perfect":
            c2_dis.config(text="Coord 2:")
            x2_inp.place(x=80,y=38)
            z2_inp.place(x=160,y=38)
        elif cur_input_mode.get()=="Corner+Facing":
            c2_dis.config(text="Direction:")
            facing_dir.set("Facing")
            facing_dir.place(x=90,y=37)
            pixel_inp.delete(0,tk.END)
            pixel_inp.insert(0,"Pixel")
            pixel_inp.place(x=175,y=38)
    if cur_input_mode.get()=="Pixel Perfect":
        pixel_dis.place(x=342,y=9)
        pixel_inp.place(x=330,y=30)
        pixel_inp.delete(0,tk.END)
    elif cur_input_mode.get()=="Mouse Tracking":
        c2_dis.config(text="Angle: 0 Deg")
        if default[12]>0:
            track_dis.config(text="Face pos X, Press F9")
            measuring=0
        else:
            track_dis.config(text="Add calibration first")
            start_calibration()
        track_dis.place(x=115,y=37)
        track_move=0
        track_angle=0
    set_infobar()

cur_input_mode=tk.StringVar()
cur_input_mode.set(default[3])
inputmodemenu=tk.Menu(inputbar,tearoff=False)
inputbar.add_cascade(label="Input mode",menu=inputmodemenu)
input_mode_list=["Coord+Coord","Corner+Facing","Pixel Perfect","Mouse Tracking"]
inputmodemenu.add_radiobutton(label="Coord+Coord",value="Coord+Coord",variable=cur_input_mode,command=set_mode)
inputmodemenu.add_radiobutton(label="Corner+Facing",value="Corner+Facing",variable=cur_input_mode,command=set_mode)
inputmodemenu.add_radiobutton(label="Pixel perfect",value="Pixel Perfect",variable=cur_input_mode,command=set_mode)
inputmodemenu.add_radiobutton(label="Mouse tracking",value="Mouse Tracking",variable=cur_input_mode,command=set_mode)

## Coordinate
cur_cinp=tk.StringVar()
cur_cinp.set(default[4])
cinpmenu=tk.Menu(inputbar,tearoff=False)
inputbar.add_cascade(label="Coord input",menu=cinpmenu)
cinp_list=["Copy+Paste","Copy+Paste (Corner)","Show Coordinate","Manual Input"]
cinp_display=["Copy+Paste","Copy+Paste(Corner)","Read Coord","Manual"]
cinpmenu.add_radiobutton(label="Copy+Paste",value="Copy+Paste",variable=cur_cinp,command=set_mode)
cinpmenu.add_radiobutton(label="Copy+Paste (corner)",value="Copy+Paste (Corner)",variable=cur_cinp,command=set_mode)
cinpmenu.add_radiobutton(label="Read coordinate",value="Show Coordinate",variable=cur_cinp,command=set_mode)
cinpmenu.add_radiobutton(label="Maunal input",value="Manual Input",variable=cur_cinp,command=set_mode)

## Manual Input
manual_input_list=["Count monitor pixel","Copy coordinate UI","Count minecraft pixel","Show coordinate"]
cur_manual_input=tk.StringVar()
cur_manual_input.set(default[14])
if cur_manual_input.get() not in manual_input_list:
    cur_manual_input.set(manual_input_list[2])
manualinputmenu=tk.Menu(inputbar,tearoff=False)
inputbar.add_cascade(label="Manual coord input",menu=manualinputmenu)
for i in range(len(manual_input_list)):
    manualinputmenu.add_radiobutton(label=manual_input_list[i],variable=cur_manual_input,value=manual_input_list[i],command=set_infobar)

## input help
inputbar.add_separator()
inputmodehelp=tk.Menu(inputbar,tearoff=False)
inputbar.add_cascade(label="Help",menu=inputmodehelp)

inputcchelp=tk.Menu(inputmodehelp,tearoff=False)
inputmodehelp.add_cascade(label="Coord+Coord",menu=inputcchelp)
inputcchelp.add_cascade(label="1. Input Coord 1")
inputcchelp.add_cascade(label="2. Align crosshair with the center of the eye")
inputcchelp.add_cascade(label="3. Walk forward")
inputcchelp.add_cascade(label="4. Input Coord 2")

inputcfhelp=tk.Menu(inputmodehelp,tearoff=False)
inputmodehelp.add_cascade(label="Corner+Facing",menu=inputcfhelp)
inputcfhelp.add_cascade(label="1. Throw an eye and face its direction")
inputcfhelp.add_cascade(label="2. Wedge into a block corner")
inputcfhelp.add_cascade(label="3. Input Coord 1")
inputcfhelp.add_cascade(label="4. Align crosshair with the center of the eye")
inputcfhelp.add_cascade(label="5. Look straight down")
inputcfhelp.add_cascade(label="6. Input facing direction and pixel offset")

inputpfhelp=tk.Menu(inputmodehelp,tearoff=False)
inputmodehelp.add_cascade(label="Pixel Perfect",menu=inputpfhelp)
inputpfhelp.add_cascade(label="1. Input Coord 1")
inputpfhelp.add_cascade(label="2. Align crosshair with the left edge of the eye")
inputpfhelp.add_cascade(label="3. Strafe right")
inputpfhelp.add_cascade(label="4. Input Coord 2")
inputpfhelp.add_cascade(label="5. Throw an eye and input the pixel shift")

inputmthelp=tk.Menu(inputmodehelp,tearoff=False)
inputmodehelp.add_cascade(label="Mouse Tracking",menu=inputmthelp)
inputmthelp.add_cascade(label="1. Input Coord 1")
inputmthelp.add_cascade(label="2. Face exactly positive X direction and press F9")
inputmthelp.add_cascade(label="3. Align crosshair with the center of the eye")
inputmthelp.add_cascade(label="4. Press F10")

## Mouse Track display
if default[12]>0:
    track_dis=tk.Label(win,text="Face pos X and press F9")
else:
    track_dis=tk.Label(win,text="Add calibration first")
if cur_input_mode.get()=="Mouse Tracking":
    track_dis.place(x=15,y=37)
    if default[12]==0:
        start_calibration()
    
# Display options
pc_list=[-1,0,6,8,10,12,14,16,18,20]
cur_pc=tk.IntVar()
cur_pc.set(int(default[5]))
pcmenu=tk.Menu(displaybar,tearoff=False)
displaybar.add_cascade(label="Probability within",menu=pcmenu)
def set_pc(inp):
    if inp<1:
        pc_lab.config(text="")
    else:
        pc_lab.config(text="≤"+str(inp)+"C")
    if inp<0:
        PROB_Label.config(text="PROB(Grid)")
    else:
        PROB_Label.config(text="PROB")
    display()
pcmenu.add_radiobutton(label="Village grid",value=-1,variable=cur_pc,command=partial(set_pc,-1))
pcmenu.add_radiobutton(label="Off",value=0,variable=cur_pc,command=partial(set_pc,0))
for i in range(2,len(pc_list)):
    pcmenu.add_radiobutton(label=str(pc_list[i])+" chunks",value=pc_list[i],variable=cur_pc,command=partial(set_pc,pc_list[i]))

cur_dismean=tk.StringVar()
cur_dismean.set(default[6])
dismeanmenu=tk.Menu(displaybar,tearoff=False)
displaybar.add_cascade(label="Display mean",menu=dismeanmenu)
def set_dismean():
    display()
dismeanmenu.add_radiobutton(label="Show",value="Show",variable=cur_dismean,command=set_dismean)
dismeanmenu.add_radiobutton(label="Hide",value="Hide",variable=cur_dismean,command=set_dismean)

high_col=tk.IntVar()
high_col.set(int(default[13]))
highcolmenu=tk.Menu(displaybar,tearoff=False)
displaybar.add_cascade(label="Highlight color",menu=highcolmenu)
def set_highcol():
    global max_col
    max_col=highcol_list[high_col.get()]
    default[13]=high_col.get()
    display()
highcol_list=[[255,0,0],[0,255,0],[0,0,255],[0,127,127],[127,0,127],[127,127,0],
              [191,64,0],[0,64,191],[64,0,191],[191,0,64]]
higicol_name=["Red","Green","Blue","Cyan","Magenta","Yellow","Orange","Azure","Violet","Rose"]
max_col=highcol_list[high_col.get()]
for i in range(len(highcol_list)):
    highcolmenu.add_radiobutton(label=higicol_name[i],value=i,variable=high_col,command=set_highcol)

# Load data
def set_version():
    for i in range(len(pt)):
        if i==0:
            add_prob(len(pt)-i-1,True)
        else:
            add_prob(len(pt)-i-1,False)
    display()
    set_infobar()
    
# Game version
game_version=tk.StringVar()
game_version.set(default[7])
gameversionmenu=tk.Menu(settingbar,tearoff=False)
settingbar.add_cascade(label="Minecraft version",menu=gameversionmenu)
gameversionmenu.add_radiobutton(label="1.21.100+",value="1.21.100+",variable=game_version,command=set_version)
gameversionmenu.add_radiobutton(label="1.18.30+",value="1.18.30+",variable=game_version,command=set_version)
gameversionmenu.add_radiobutton(label="Pre 1.18.30",value="Pre 1.18.30",variable=game_version,command=set_version)

cur_prior=tk.StringVar()
cur_prior.set(default[8])
priormenu=tk.Menu(settingbar,tearoff=False)
settingbar.add_cascade(label="Prior probability",menu=priormenu)
def set_prior(disp):
    for i in range(len(pt)):
        if i==0:
            add_prob(len(pt)-i-1,True)
        else:
            add_prob(len(pt)-i-1,False)
    if disp:
        display()
priormenu.add_radiobutton(label="Based on simulation",value="Simulation",variable=cur_prior,command=partial(set_prior,1))
priormenu.add_radiobutton(label="Uniform probability",value="Uniform",variable=cur_prior,command=partial(set_prior,1))

# Stronghold within
cur_within=tk.IntVar()
cur_within.set(int(default[9]))
withinmenu=tk.Menu(settingbar,tearoff=False)
settingbar.add_cascade(label="Search radius",menu=withinmenu)
withinmenu.add_radiobutton(label="2000",value=2000,variable=cur_within,command=set_version)
withinmenu.add_radiobutton(label="3000",value=3000,variable=cur_within,command=set_version)
withinmenu.add_radiobutton(label="4000",value=4000,variable=cur_within,command=set_version)
withinmenu.add_radiobutton(label="6000",value=6000,variable=cur_within,command=set_version)
withinmenu.add_radiobutton(label="10000",value=10000,variable=cur_within,command=set_version)


# Initialize infobar
calibrating=0
set_infobar()

# Add coordinate
x1,z1,x2,z2=0,0,0,0

def set_c1():
    global x1, z1, coords
    try:
        if cur_cinp.get()=="Show Coordinate":
            coords=READCOORD(sw,sh,debug,0)
            print(["screen reader",coords.x,coords.y,coords.z,coords.valid])
            if coords.valid:
                x1=coords.x+0.5
                z1=coords.z+0.5
            else:
                x1,z1=0,0
        elif cur_cinp.get()=="Copy+Paste (Corner)" or cur_cinp.get()=="Copy+Paste":
            inp=pyperclip.paste()
            inp=inp.split(" ")
            x1=float(inp[0])
            z1=float(inp[2])
            if cur_input_mode.get()=="Corner+Facing" or cur_cinp.get()=="Copy+Paste (Corner)":
                if round(x1%1,1) not in [0.3,0.7] or round(z1%1,1) not in [0.3,0.7]:
                    x1,z1=0,0
        set_infobar()
    except:
        x1,z1=0,0
        option_info.config(text="Coordinate has not been copied",fg="#AA0000")
    if cur_cinp.get()!="Manual Input":
        c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")

def set_c2():
    global x2, z2, coords
    try:
        if cur_cinp.get()=="Show Coordinate":
            coords=READCOORD(sw,sh,debug,0)
            print(["screen reader",coords.x,coords.y,coords.z,coords.valid])
            if coords.valid:
                x2=coords.x+0.5
                z2=coords.z+0.5
            else:
                x1,z1=0,0
        elif cur_cinp.get()=="Copy+Paste (Corner)" or cur_cinp.get()=="Copy+Paste":
            inp=pyperclip.paste()
            inp=inp.split(" ")
            x2=float(inp[0])
            z2=float(inp[2])
        set_infobar()
    except:
        x2,z2=0,0
        option_info.config(text="Coordinate has not been copied",fg="#AA0000")
    if cur_cinp.get()!="Manual Input":
        c2_dis.config(text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")

def add_point():
    global pt, x1, x2, z1, z2, pt_mode, pt_prec, pt_err, pt_coord, pt_pixel, pt_pixel_err, pt_manual, track_angle, track_move, sum_abs
    curmode=cur_input_mode.get()
    if curmode=="Corner+Facing" or curmode=="Mouse Tracking":
        cneed=False
    else:
        cneed=True
    if cur_cinp.get()=="Manual Input" and cneed:
        try:
            x1=float(x1_inp.get())
            x2=float(x2_inp.get())
            z1=float(z1_inp.get())
            z2=float(z2_inp.get())
        except:
            x1,x2,z1,z2=0,0,0,0
    elif cur_cinp.get()=="Manual Input":
        try:
            x1=float(x1_inp.get())
            z1=float(z1_inp.get())
        except:
            x1,z1=0,0
    if cur_cinp.get()=="Manual Input" and cur_manual_input.get()=="Show coordinate":
        x1=x1+0.5
        x2=x2+0.5
        z1=z1+0.5
        z2=z2+0.5
    print(["ADD",x1,z1,x2,z2])
    if cur_input_mode.get()=="Coord+Coord":
        valid=True
        if cur_cinp.get()=="Copy+Paste (Corner)":
            mod1=round(x1%1,2)
            mod2=round(z1%1,2)
            if (mod1==0.3 or mod1==0.7) and (mod2==0.3 or mod2==0.7):
                valid=True
            else:
                valid=False
        if (x1,z1)!=(x2,z2) and valid:
            pt.insert(0,[x1,z1,x2,z2])
            pt_mode.insert(0,cur_input_mode.get())
            pt_err.insert(0,cur_error_angle.get())
            pt_prec.insert(0,0)
            pt_coord.insert(0,cur_cinp.get())
            pt_pixel.insert(0,0)
            pt_pixel_err.insert(0,0)
            pt_manual.insert(0,cur_manual_input.get())
            listdata.insert(0,'cc/'+f'{x1:.0f}'+","+f'{z1:.0f}'+"/"+f'{x2:.0f}'+","+f'{z2:.0f}')
            x1,x2,z1,z2=0,0,0,0
            if cur_cinp.get()=="Copy+Paste" or cur_cinp.get()=="Copy+Paste (Corner)" or cur_cinp.get()=="Show Coordinate":
                c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
                c2_dis.config(text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")
            else:
                x1_inp.delete(0,tk.END)
                x2_inp.delete(0,tk.END)
                z1_inp.delete(0,tk.END)
                z2_inp.delete(0,tk.END)
            if len(pt)==1:
                add_prob(0,True)
            else:
                add_prob(0,False)
            set_infobar()
            display()
        elif not valid:
            option_info.config(text="Fractional part of Coord 1 should be 0.3 or 0.7 in Copy+Paste(Corner) mode",fg="#AA0000")
        else:
            option_info.config(text="Invalid coordinate input",fg="#AA0000")
    elif cur_input_mode.get()=="Corner+Facing":
        mod1=round(x1%1,2)
        mod2=round(z1%1,2)
        facing=facing_dir.get()
        if (mod1==0.3 or mod1==0.7) and (mod2==0.3 or mod2==0.7) and (facing=="X" or facing=="Z"):
            valid=True
            try:
                dir_pixel=float(pixel_inp.get())
                if dir_pixel>=0 and dir_pixel<=8:
                    valid=True
                else:
                    valid=False
            except:
                valid=False
            if valid:
                if mod1==0.7 and mod2==0.7:
                    if facing=="X":
                        x2=x1+0.3
                        z2=z1+0.3-dir_pixel/16
                    else:
                        x2=x1+0.3-dir_pixel/16
                        z2=z1+0.3
                elif mod1==0.7 and mod2==0.3:
                    if facing=="X":
                        x2=x1+0.3
                        z2=z1-0.3+dir_pixel/16
                    else:
                        x2=x1+0.3-dir_pixel/16
                        z2=z1-0.3
                elif mod1==0.3 and mod2==0.7:
                    if facing=="X":
                        x2=x1-0.3
                        z2=z1+0.3-dir_pixel/16
                    else:
                        x2=x1-0.3+dir_pixel/16
                        z2=z1+0.3
                else:
                    if facing=="X":
                        x2=x1-0.3
                        z2=z1-0.3+dir_pixel/16
                    else:
                        x2=x1-0.3+dir_pixel/16
                        z2=z1-0.3
                    
                pt.insert(0,[x1,z1,x2,z2])
                pt_mode.insert(0,cur_input_mode.get())
                pt_err.insert(0,cur_error_angle.get())
                listdata.insert(0,'cf/'+f'{x1:.0f}'+","+f'{z1:.0f}'+"/"+f'{x2-x1:.2f}'+"/"+f'{z2-z1:.2f}')
                facing_dir.set("Facing")
                pixel_inp.delete(0,tk.END)
                pixel_inp.insert(0,"Pixel")
                pt_coord.insert(0,cur_cinp.get())
                pt_prec.insert(0,cur_error_pixel.get())
                pt_pixel.insert(0,0)
                pt_pixel_err.insert(0,0)
                pt_manual.insert(0,cur_manual_input.get())
                x1,x2,z1,z2=0,0,0,0
                if cur_cinp.get()=="Copy+Paste" or cur_cinp.get()=="Copy+Paste (Corner)" or cur_cinp.get()=="Show Coordinate":
                    c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
                else:
                    x1_inp.delete(0,tk.END)
                    x2_inp.delete(0,tk.END)
                    z1_inp.delete(0,tk.END)
                    z2_inp.delete(0,tk.END)
                if len(pt)==1:
                    add_prob(0,True)
                else:
                    add_prob(0,False)
                display()
                set_infobar()
            else:
                option_info.config(text="Invalid pixel input",fg="#AA0000")
        else:
            option_info.config(text="Invalid coordinate or facing direction",fg="#AA0000")
    elif cur_input_mode.get()=="Pixel Perfect":
        valid=True
        if cur_cinp.get()=="Copy+Paste (Corner)":
            mod1=round(x1%1,2)
            mod2=round(z1%1,2)
            if (mod1==0.3 or mod1==0.7) and (mod2==0.3 or mod2==0.7):
                valid=True
            else:
                valid=False
        valid_pixel=True
        try:
            npixel=float(pixel_inp.get())
            if npixel<=0:
                valid_pixel=False
        except:
            valid_pixel=False
        if (x1,z1)!=(x2,z2) and valid:
            pt.insert(0,[x1,z1,x2,z2])
            if valid_pixel:
                pt_mode.insert(0,cur_input_mode.get())
                pt_pixel.insert(0,npixel)
                pt_pixel_err.insert(0,cur_pixel_perfect.get())
            else:
                pt_mode.insert(0,"Coord+Coord")
                pt_pixel.insert(0,0)
                pt_pixel_err.insert(0,0)
            pt_err.insert(0,cur_error_angle.get())
            pt_prec.insert(0,0)
            pt_coord.insert(0,cur_cinp.get())
            pt_manual.insert(0,cur_manual_input.get())
            if valid_pixel:
                listdata.insert(0,'pf/'+f'{x1:.0f}'+","+f'{z1:.0f}'+"/"+f'{x2:.0f}'+","+f'{z2:.0f}'+"/"+str(npixel))
            else:
                listdata.insert(0,'cc/'+f'{x1:.0f}'+","+f'{z1:.0f}'+"/"+f'{x2:.0f}'+","+f'{z2:.0f}')
            x1,x2,z1,z2=0,0,0,0
            pixel_inp.delete(0,tk.END)
            if cur_cinp.get()=="Copy+Paste" or cur_cinp.get()=="Copy+Paste (Corner)" or cur_cinp.get()=="Show Coordinate":
                c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
                c2_dis.config(text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")
            else:
                x1_inp.delete(0,tk.END)
                x2_inp.delete(0,tk.END)
                z1_inp.delete(0,tk.END)
                z2_inp.delete(0,tk.END)
            if len(pt)==1:
                add_prob(0,True)
            else:
                add_prob(0,False)
            display()
            set_infobar()
        elif not valid:
            option_info.config(text="Fractional part of Coord 1 should be 0.3 or 0.7 in Copy+Paste(Corner) mode",fg="#AA0000")
        else:
            option_info.config(text="Invalid coordinate input",fg="#AA0000")
    else:
        valid=True
        valid_measurement=True
        if cur_cinp.get()=="Copy+Paste (Corner)":
            mod1=round(x1%1,2)
            mod2=round(z1%1,2)
            if (mod1==0.3 or mod1==0.7) and (mod2==0.3 or mod2==0.7):
                valid=True
            else:
                valid=False
        try:
            sum_abs+1
            if sum_abs==0:
                valid_measurement=False
        except:
            valid_measurement=False
        if valid and valid_measurement and sum_abs>0:
            pt.insert(0,[x1,z1,track_move,default[10],default[11],sum_abs])
            print(["mouse track",track_move,sum_abs])
            pt_mode.insert(0,cur_input_mode.get())
            pt_err.insert(0,cur_error_angle.get())
            pt_prec.insert(0,0)
            pt_coord.insert(0,cur_cinp.get())
            pt_pixel.insert(0,0)
            pt_pixel_err.insert(0,cur_pixel_perfect.get())
            pt_manual.insert(0,cur_manual_input.get())
            listdata.insert(0,'mt/'+f'{x1:.0f}'+","+f'{z1:.0f}'+"/"+str(round(track_angle)))
            x1,x2,z1,z2,track_move,track_angle,sum_abs=0,0,0,0,0,0,0
            if cur_cinp.get()=="Copy+Paste" or cur_cinp.get()=="Copy+Paste (Corner)" or cur_cinp.get()=="Show Coordinate":
                c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
            else:
                x1_inp.delete(0,tk.END)
                x2_inp.delete(0,tk.END)
                z1_inp.delete(0,tk.END)
                z2_inp.delete(0,tk.END)
            c2_dis.config(text="Angle: 0 Deg")
            if len(pt)==1:
                add_prob(0,True)
            else:
                add_prob(0,False)
            display()
            set_infobar()
        elif not valid:
            option_info.config(text="Fractional part of Coord 1 should be 0.3 or 0.7 in Copy+Paste(Corner) mode",fg="#AA0000")
        else:
            option_info.config(text="Invalid angle measurement",fg="#A0000")

def del_point():
    global pt, pt_mode, pt_prec, pt_err, pt_coord, pt_pixel, pt_pixel_err, pt_manual, lencand
    try:
        ind=listdata.curselection()[0]
        listdata.delete(ind)
        pt.pop(ind)
        pt_prec.pop(ind)
        pt_mode.pop(ind)
        pt_err.pop(ind)
        pt_coord.pop(ind)
        pt_pixel.pop(ind)
        pt_pixel_err.pop(ind)
        pt_manual.pop(ind)
        lencand=0
        for i in range(len(pt)):
            if i==0:
                add_prob(len(pt)-i-1,True)
            else:
                add_prob(len(pt)-i-1,False)
        display()
    except:
        pass

def clear():
    a=time.time()
    global pt, pt_mode, pt_prec, pt_err, pt_coord, pt_pixel, pt_pixel_err, pt_manual, lencand
    pt=[]
    pt_mode=[]
    pt_prec=[]
    pt_err=[]
    pt_coord=[]
    pt_pixel=[]
    pt_pixel_err=[]
    pt_manual=[]
    listdata.delete(0,tk.END)
    lencand=0
    display()

def clear_inp(event):
    pixel_inp.delete(0,tk.END)

c1_dis=tk.Label(win,text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
c1_dis.place(x=5,y=7)
c1_but=tk.Button(win,text="PASTE",command=set_c1,padx=5,pady=1)
c1_but.place(x=200,y=4)

c2_dis=tk.Label(win,text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")
c2_dis.place(x=5,y=37)
facing_dir=ttk.Combobox(win,values=["X","Z"],width=6,state="readonly")
facing_dir.set("Facing")
pixel_inp=tk.Entry(win,width=6)
pixel_inp.insert(0,"Pixels")
pixel_inp.bind("<Button-1>",clear_inp)
c2_but=tk.Button(win,text="PASTE",command=set_c2,padx=5,pady=1)
c2_but.place(x=200,y=35)
pixel_dis=tk.Label(win,text="Pixel")

# Hotkey
bg=BG()
bg.gbind("<KeyRelease>",clear_input_buffer())

def key_press1(event):
    set_c1()
    clear_input_buffer()

def key_press2(event):
    if calibrating_align:
        set_cal_c2()
    elif cur_input_mode.get()=="Coord+Coord" or cur_input_mode.get()=="Pixel Perfect":
        set_c2()
    clear_input_buffer()

def key_press3(event):
    if calibrating_align:
        add_align_calibration()
    else:
        add_point()
    clear_input_buffer()

def key_press7(event):
    if cur_input_mode.get()=="Pixel Perfect":
        try:
            cur_pixel_inp=float(pixel_inp.get())
            cur_pixel_inp=round(cur_pixel_inp+0.5,1)
            pixel_inp.delete(0,tk.END)
            pixel_inp.insert(0,cur_pixel_inp)
        except:
            pixel_inp.delete(0,tk.END)
            pixel_inp.insert(0,"0.5")
    clear_input_buffer()

def key_press8(event):
    if cur_input_mode.get()=="Pixel Perfect":
        try:
            cur_pixel_inp=float(pixel_inp.get())
            cur_pixel_inp=max(0,round(cur_pixel_inp-0.5,1))
            pixel_inp.delete(0,tk.END)
            pixel_inp.insert(0,cur_pixel_inp)
        except:
            pixel_inp.delete(0,tk.END)
            pixel_inp.insert(0,"0")
    clear_input_buffer()

def key_press9(event):
    if cur_input_mode.get()=="Pixel Perfect":
        try:
            cur_pixel_inp=float(pixel_inp.get())
            cur_pixel_inp=round(cur_pixel_inp+0.1,1)
            pixel_inp.delete(0,tk.END)
            pixel_inp.insert(0,cur_pixel_inp)
        except:
            pixel_inp.delete(0,tk.END)
            pixel_inp.insert(0,"0.1")
    clear_input_buffer()

def key_press10(event):
    if cur_input_mode.get()=="Pixel Perfect":
        try:
            cur_pixel_inp=float(pixel_inp.get())
            cur_pixel_inp=max(0,round(cur_pixel_inp-0.1,1))
            pixel_inp.delete(0,tk.END)
            pixel_inp.insert(0,cur_pixel_inp)
        except:
            pixel_inp.delete(0,tk.END)
            pixel_inp.insert(0,"0")
    clear_input_buffer()

# Dig spot
def key_press11(event):
    coords=READCOORD(sw,sh,debug,0)
    if coords.valid:
        x=coords.x
        z=coords.z
        cx=x//16
        cz=z//16
        
        digcand=[]
        for i in range(cx-1,cx+2):
            for j in range(cz-1,cz+2):
                candx=i*16+4
                candz=j*16+4
                digcand.append([(candx-x)**2+(candz-z)**2,candx,candz])
        digcand=sorted(digcand)
        
        digx=digcand[0][1]
        digz=digcand[0][2]
        dx=digx-x
        dz=digz-z
        labels[8][0].config(text="({},{})".format(digx,digz))
        
        if dx>0:
            sign1="+"
        elif dx==0:
            sign1="0"
        else:
            sign1="-"
        if dz>0:
            sign2="+"
        elif dz==0:
            sign2="0"
        else:
            sign2="-"
            
        labels[8][1].config(text="( {} , {} )".format(sign1,sign2),fg="#000000")
        labels[8][2].config(text="SH Dig",fg="#000000")

        in_grid=0

        if len(pt)==0:
            chunk_dist=int((cx**2+cz**2)**0.5)
            if chunk_dist>999:
                prob_dig=0
            elif game_version.get()=="Pre 1.18.30":
                if cx%27<=17 and cz%17<=17:
                    prob_dig=vilprob16[chunk_dist]*18*18/0.267
                    in_grid=1
                else:
                    prob_dig=0
            else:
                if cx%34<=27 and cz%34<=27:
                    prob_dig=vilprob[chunk_dist]*28*28/0.267
                    in_grid=1
                else:
                    prob_dig=0
        else:
            if game_version.get()=="Pre 1.18.30":
                if cx%27<=17 and cz%17<=17:
                    prob_dig=IFVILPROB(digx//16,digz//16,1,res,lencand,info)
                    in_grid=1
                else:
                    prob_dig=0
            else:
                if cx%34<=27 and cz%34<=27:
                    prob_dig=IFVILPROB(digx//16,digz//16,0,res,lencand,info)
                    in_grid=1
                else:
                    prob_dig=0
        col_code=[int(max_col[j]*(prob_dig)) for j in range(3)]
        if in_grid:
            labels[8][3].config(text=f'{prob_dig*100:.1f}'+"%",fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]))
        else:
            labels[8][3].config(text='')
    clear_input_buffer()

def key_press12(event):
    coords=READCOORD(sw,sh,debug,0)
    if coords.valid:
        BTCALC(coords.x,coords.z,btres)
        labels[8][0].config(text="({},{})".format(btres[0],btres[1]),fg="#000000")
        labels[8][1].config(text="({},{})".format(btres[2],btres[3]),fg="#000000")
        labels[8][2].config(text="({},{})".format(btres[4],btres[5]),fg="#000000")
        labels[8][3].config(text="BT Dig",fg="#000000")
    clear_input_buffer()

def key_press13(event):
    display()
    clear_input_buffer()
    
saved_coord=[0,0,0]
def key_press14(event):
    global saved_coord
    coords=READCOORD(sw,sh,debug,1)
    if coords.valid:
        saved_coord=[coords.x,coords.y,coords.z]
    labels[8][0].config(text="({},{},{})".format(saved_coord[0],saved_coord[1],saved_coord[2]),fg="#000000")
    labels[8][1].config(text="")
    labels[8][2].config(text="Saved Coord",fg="#000000")
    labels[8][3].config(text="")
    clear_input_buffer()
    
def key_press15(event):
    labels[8][0].config(text="({},{},{})".format(saved_coord[0],saved_coord[1],saved_coord[2]),fg="#000000")
    labels[8][1].config(text="")
    labels[8][2].config(text="Saved Coord",fg="#000000")
    labels[8][3].config(text="")
    clear_input_buffer()
    
def key_press16(event):
    curinpind=input_mode_list.index(cur_input_mode.get())
    curinpind=(curinpind+1)%4
    cur_input_mode.set(input_mode_list[curinpind])
    set_mode()
    clear_input_buffer()

# Mouse tracking
sum_move=ctypes.c_int(0)
sum_abs=ctypes.c_int(0)
def start_track():
    global sum_move, calibrating, measuring, sum_abs
    print("START TRACKING")
    sum_move=ctypes.c_int(0)
    sum_abs=ctypes.c_int(0)
    START_TRACK()
    if calibrating==1:
        calibrating=2
        set_infobar()
    if calibrating==0 and cur_input_mode.get()=="Mouse Tracking" and default[12]>0:
        track_dis.config(text="Align and press F10")
        measuring=2
def key_press4(event):
    start_track()
    clear_input_buffer()

def stop_track():
    global sum_move, default, calibrating, track_angle, measuring, track_move, sum_abs
    print("STOP TRACKING")
    if type(sum_move)==int:
        sum_move=ctypes.c_int(0)
        sum_abs=ctypes.c_int(0)
    GET_TRACK(ctypes.byref(sum_move),ctypes.byref(sum_abs))
    STOP_TRACK()
    sum_move=sum_move.value
    sum_abs=sum_abs.value
    if calibrating==2:
        sum_move=abs(sum_move)
        default[10]=(default[10]*default[12]+sum_move)/(default[12]+1)
        default[11]=((default[12]*default[11]**2+(sum_move-default[10])**2)/(default[12]+1))**0.5
        default[12]=default[12]+1
        calibrating=0
        set_infobar()
        mousecalibratemenu.delete(2,3)
        mousecalibratemenu.add_cascade(label="Mean: "+f'{default[10]:.1f}')
        mousecalibratemenu.add_cascade(label="SD: "+f'{default[11]:.1f}')
        if cur_input_mode.get()=="Mouse Tracking":
            measuring=0
            track_dis.config(text="Face pos X, Press F9")
            track_angle=(track_move/default[10]*90)%360
            c2_dis.config(text="Angle: "+str(round(track_angle))+" Deg")
    if calibrating==0 and cur_input_mode.get()=="Mouse Tracking" and measuring==2 and default[12]>0:
        track_move=sum_move
        track_angle=(track_move/default[10]*90)%360
        c2_dis.config(text="Angle: "+str(round(track_angle))+" Deg")
        measuring=0
        track_dis.config(text="Face pos X, Press F9")
def key_press5(event):
    stop_track()
    clear_input_buffer()

# Iconify
def key_press6(event):
    if win.state()=="iconic":
        win.state("normal")
    else:
        win.state("iconic")

# Keybind help
hotkey_desc=["Paste coord 1","Paste coord 2","Add data","Start mouse tracking","End mouse tracking","Minimize window",
             "Pixel shift +0.5","Pixel shift -0.5","Pixel shift +0.1","Pixel shift -0.1","Stronghold dig spot",
             "Buried treasure dig spot","Hide dig spot","Save coordinate","Display saved coordinate","Change input mode"]
def keybind_help():
    nhelp=hotkeylist.index("end")
    if isinstance(nhelp,int):
        for i in range(nhelp+1):
            hotkeylist.delete(0,nhelp)
    for i in range(len(hotkey_desc)):
        curkey=cur_hotkey[i].split(" ")
        if len(curkey)==1:
            curkeycode=curkey[0].upper()
        else:
            curkey[1]=curkey[1].upper()
            if curkey[0]=="s":
                curkeycode="Shift+"+curkey[1]
            elif curkey[0]=="d":
                curkeycode=curkey[1]+"×2"
            else:
                curkeycode=curkey[1]
        hotkeylist.add_cascade(label="{}: {}".format(curkeycode,hotkey_desc[i]))
keybind_help()

# Keybind
key_press=[]
for i in range(len(hotkey_desc)):
    exec("key_press.append(key_press{})".format(i+1))

bindglobal=[]
def applyhotkey():
    global bindglobal
    bindglobal=[]
    for i in range(len(hotkey_desc)):
        bg=BG()
        bindglobal.append(bg)
    for i in range(len(hotkey_desc)):
        bindglobal[i].start()
        curkey=cur_hotkey[i].split(" ")
        curkeycode=""
        if len(curkey)==1:
            curkeycode=curkey[0]
        else:
            if curkey[0]=="s":
                if curkey[1] in string.ascii_lowercase:
                    curkeycode=curkey[1].upper()
                else:
                    curkeycode="Shift-"+curkey[1]
            elif curkey[0]=="d":
                curkeycode="Double-KeyRelease-"+curkey[1]
        bindglobal[i].gbind("<{}>".format(curkeycode),key_press[i])
applyhotkey()

# Valid keybind
valid_key=[]
valid_code=[]
valid_mod=[]
for i in range(10):
    valid_key.append(str(i))
    valid_code.append(48+i)
    valid_mod.append(0)
for i in range(26):
    valid_key.append(string.ascii_lowercase[i])
    valid_code.append(65+i)
    valid_mod.append(1)
for i in range(10):
    valid_key.append("F"+str(i+1))
    valid_code.append(112+i)
    valid_mod.append(1)
    
valid_key=valid_key+["F12","[","]",";","'",",",".","/","-","="]
valid_code=valid_code+[123,219,221,186,222,188,190,191,189,187]
valid_mod=valid_mod+[0]*10

# Change keybind
curkey=""
def changehotkey():
    global curkey, calibrating_align
    print("CHANGE HOTKEY")
    # unplace
    c1_but.place_forget()
    c2_but.place_forget()
    x1_inp.place_forget()
    x2_inp.place_forget()
    z1_inp.place_forget()
    z2_inp.place_forget()
    facing_dir.place_forget()
    pixel_inp.place_forget()
    pixel_dis.place_forget()
    track_dis.place_forget()
    c1_dis.place_forget()
    c2_dis.place_forget()
    add_but.place_forget()

    next_but.place_forget()
    calibration_label1.place_forget()
    calibration_label2.place_forget()
    calibration_label3.place_forget()
    cal_c2_but.place_forget()
    cal_add_but.place_forget()
    cal_return.place_forget()
    cal_clear.place_forget()
    cal_cancel.place_forget()
    calibrating_align=0
    
    for i in range(len(hotkey_desc)):
        bindglobal[i].stop()

    changehotkeylist.place(x=15,y=10)
    changehotkeylist.set("Hotkey action")
    changehotkeymod.place(x=15,y=40)
    changehotkeymod.set("Modifier")
    changehotkeylabel.place(x=100,y=40)
    changehotkeylabel.config(text="Key: "+curkey)
    changehotkeybut.place(x=190,y=22)
    changehotkeyreset.place(x=270,y=22)
    changehotkeyreturn.place(x=330,y=22)
    win.bind("<Key>",hotkeylisten)
    curkey=""
    
def hotkeylisten(event):
    global curkey
    if event.keycode in valid_code:
        curmod=changehotkeymod.get()
        valid=True
        if curmod=="Shift" and valid_mod[valid_code.index(event.keycode)]==0:
            valid=False

        if valid:
            curkey=valid_key[valid_code.index(event.keycode)]
            changehotkeylabel.config(text="Key: "+curkey)
            set_infobar()
        else:
            option_info.config(text="Invalid key. Try other keys.",fg="#AA0000")
    else:
        option_info.config(text="Invalid key. Try other keys.",fg="#AA0000")

def hotkeychange():
    print("CHANGE")
    global curkey
    if curkey=="":
        option_info.config(text="No key was input",fg="#AA0000")
        return()
    if  changehotkeylist.get()=="Hotkey action":
        option_info.config(text="Choose which hotkey action to change",fg="#AA0000")
        return()
    if changehotkeymod.get()=="Shift" and valid_mod[valid_key.index(curkey)]==0:
        option_info.config(text="Invalid key. Try other keys. Hotkey didn't changed.",fg="#AA0000")
        curkey=""
        return()
    keyind=hotkey_desc.index(changehotkeylist.get())
    if changehotkeymod.get()=="Shift":
        new_code="s "+curkey
    elif changehotkeymod.get()=="Double":
        new_code="d "+curkey
    else:
        new_code=curkey

    if new_code not in cur_hotkey:
        cur_hotkey[keyind]=new_code
        keybind_help()
        changehotkeylist.set("Hotkey action")
        changehotkeymod.set("Modifier")
        curkey=""
        changehotkeylabel.config(text="Key: "+curkey)
        set_infobar()
    else:
        option_info.config(text="Duplicate hotkey. Hotkey didn't changed.",fg="#AA0000")

def hotkeyreset():
    global cur_hotkey
    for i in range(len(hotkey_desc)):
        cur_hotkey[i]=default_hotkey[i]
        keybind_help()
        changehotkeylist.set("Hotkey action")
        changehotkeymod.set("Modifier")
        curkey=""
        changehotkeylabel.config(text="Key: "+curkey)
    keybind_help()

def returncalc():
    changehotkeylist.place_forget()
    changehotkeymod.place_forget()
    changehotkeylabel.place_forget()
    changehotkeybut.place_forget()
    changehotkeyreturn.place_forget()
    changehotkeyreset.place_forget()
    win.unbind("<Key>")
    applyhotkey()
    set_mode()
    
hotkeybar.add_command(label="Change hotkeys",command=changehotkey)
changehotkeylist=ttk.Combobox(win,values=hotkey_desc,width=20,state="readonly")
changehotkeylist.set("Hotkey action")
changehotkeymod=ttk.Combobox(win,values=["None","Shift","Double"],width=8,state="readonly")
changehotkeymod.set("Modifier")
changehotkeylabel=tk.Label(text="Key: "+curkey)
changehotkeybut=tk.Button(text="APPLY",padx=3,pady=2,command=hotkeychange)
changehotkeyreturn=tk.Button(text="RETURN",padx=3,pady=2,command=returncalc)
changehotkeyreset=tk.Button(text="RESET",padx=3,pady=2,command=hotkeyreset)

# Calibrate align error
calibrating_align=0
stronghold_x=0
stronghold_z=0
calibrate_list=[]
error_precision_list=[]
def calibtrate_align_error():
    global calibrate_list
    print("CALIBRATE ALIGN ERROR")
    # unplace
    c1_but.place_forget()
    c2_but.place_forget()
    x2_inp.place_forget()
    z2_inp.place_forget()
    facing_dir.place_forget()
    pixel_inp.place_forget()
    pixel_dis.place_forget()
    track_dis.place_forget()
    c2_dis.place_forget()
    add_but.place_forget()

    changehotkeylist.place_forget()
    changehotkeymod.place_forget()
    changehotkeylabel.place_forget()
    changehotkeybut.place_forget()
    changehotkeyreturn.place_forget()
    changehotkeyreset.place_forget()

    next_but.place_forget()
    calibration_label1.place_forget()
    calibration_label2.place_forget()
    calibration_label3.place_forget()
    cal_c2_but.place_forget()
    cal_add_but.place_forget()
    cal_return.place_forget()
    cal_clear.place_forget()

    c1_dis.config(text="Stronghold:")
    c1_dis.place(x=10,y=25)
    x1_inp.place(x=100,y=25)
    z1_inp.place(x=180,y=25)
    next_but.place(x=250,y=20)
    cal_cancel.place(x=310,y=20)

    calibration_label1.config(text="Use version 1.19.10+")
    calibration_label1.place(x=250,y=125,anchor=tk.CENTER)
    calibration_label1.lift()
    calibration_label2.config(text="Create world in creative, activate cheat")
    calibration_label2.place(x=250,y=150,anchor=tk.CENTER)
    calibration_label2.lift()
    calibration_label3.config(text="/locate command copied to clipboard")
    calibration_label3.place(x=250,y=175,anchor=tk.CENTER)
    calibration_label3.lift()
    pyperclip.copy("locate structure stronghold")
    calibrate_list=[]
    error_precision_list=[]

    for i in range(len(hotkey_desc)):
        bindglobal[i].stop()

    for i in range(9):
        for j in range(4):
            labels[i][j].config(text="")

def first_calibration():
    global calibrating_align, stronghold_x, stronghold_z, x1, x2, z1, z2
    valid=True
    try:
        stronghold_x=int(x1_inp.get())
    except:
        valid=False
        stronghold_x=0
    try:
        stronghold_z=int(z1_inp.get())
    except:
        valid=False
        stronghold_z=0
        
    if valid:
        calibrating_align=1
        x1_inp.place_forget()
        z1_inp.place_forget()
        x1_inp.place_forget()
        next_but.place_forget()
        cal_cancel.place_forget()
        
        c1_dis.place(x=5,y=7)
        c2_dis.place(x=5,y=37)
        cal_add_but.place(x=265,y=19)
        cal_c2_but.place(x=200,y=35)
        cal_return.place(x=360,y=18,anchor=tk.CENTER)
        cal_clear.place(x=360,y=55,anchor=tk.CENTER)

        x2,z2=0,0
        angle=random.random()*math.pi*2
        x1=round(stronghold_x+100*math.cos(angle),2)
        z1=round(stronghold_z+100*math.sin(angle),2)
        c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
        c2_dis.config(text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")

        calibration_label1.config(text="/tp command copied to clipboard")
        calibration_label2.config(text="Throw eye, align to the center")
        calibration_label3.config(text="Copy+Paste coord 2 and add data")
        pyperclip.copy("tp @s {} 200 {}".format(x1,z1))

        bindglobal[1].start()
        bindglobal[2].start()
        set_infobar()
    else:
        option_info.config(text="Invalid stronghold coordinate",fg="#AA0000")

ANGLEDIF=dll2.angle_dif_cal
ANGLEDIF.argtypes=[ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double]
ANGLEDIF.restype=ctypes.c_double

def add_align_calibration():
    global calibrate_list, x1, x2, z1, z2, error_precision_list
    print("ADD CALIBRATION")
    if (x1,z1)!=(x2,z1):
        angledif=ANGLEDIF(x1,z1,x2,z2,float(stronghold_x),float(stronghold_z))

        dist=((x1-z1)**2+(x2-z2)**2)**0.5
        error_precision=0.01/dist*0.2339
        calibrate_list.append(angledif)
        error_precision_list.append(error_precision)

        cur_error=max(0,angledif**2-error_precision**2)**0.5*12*16
        total_error=sum(calibrate_list[i]**2 for i in range(len(calibrate_list)))/len(calibrate_list)
        mean_error_precision=sum(error_precision_list)/len(error_precision_list)
        std_error=max(0,total_error-mean_error_precision**2)**0.5*12*16

        calibration_label2.config(text="Previous error: {}".format(f'{cur_error:.2f}'))
        calibration_label3.config(text="Standard error: {}".format(f'{std_error:.2f}'))

        x2,z2=0,0
        angle=random.random()*math.pi*2
        x1=round(stronghold_x+100*math.cos(angle),2)
        z1=round(stronghold_z+100*math.sin(angle),2)
        c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
        c2_dis.config(text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")
        pyperclip.copy("tp @s {} 200 {}".format(x1,z1))
        set_infobar()
    else:
        option_info.config(text="Coord 1 and Coord 2 should be different",fg="#AA0000")

def set_cal_c2():
    print("CALIBRATION COORD2")
    global x2,z2
    try:
        inp=pyperclip.paste()
        inp=inp.split(" ")
        x2=float(inp[0])
        z2=float(inp[2])
        c2_dis.config(text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")
    except:
        x2,z2=0,0
        c2_dis.config(text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")

def returncalc2():
    global calibrating_align, x1, x2, z1, z2
    
    next_but.place_forget()
    calibration_label1.place_forget()
    calibration_label2.place_forget()
    calibration_label3.place_forget()
    cal_c2_but.place_forget()
    cal_add_but.place_forget()
    cal_return.place_forget()
    cal_clear.place_forget()
    cal_cancel.place_forget()

    if len(calibrate_list)>0:
        total_error=sum(calibrate_list[i]**2 for i in range(len(calibrate_list)))/len(calibrate_list)
        mean_error_precision=sum(error_precision_list)/len(error_precision_list)
        std_error=max(0,total_error-mean_error_precision**2)**0.5*12*16
        acc_list_dif=[(acc_list[i]-std_error)**2 for i in range(len(acc_list))]
        cur_error_angle.set(acc_list[acc_list_dif.index(min(acc_list_dif))])

    bindglobal[1].stop()
    bindglobal[2].stop()
        
    applyhotkey()
    set_mode()
    display()
    calibrating_align=0
    x1, x2, z1, z2=0,0,0,0
    c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")

def cal_clear_list():
    global calibrate_list, error_precision_list
    calibrate_list=[]
    error_precision_list=[]
    calibration_label2.config(text="Throw eye, align to the center")
    calibration_label3.config(text="Copy+Paste coord 2 and add data")
    pyperclip.copy("tp @s {} 200 {}".format(x1,z1))

def cancel_calibration():
    global x1, x2, z1, z2
    next_but.place_forget()
    calibration_label1.place_forget()
    calibration_label2.place_forget()
    calibration_label3.place_forget()
    cal_c2_but.place_forget()
    cal_add_but.place_forget()
    cal_return.place_forget()
    cal_clear.place_forget()
    cal_cancel.place_forget()

    applyhotkey()
    set_mode()
    display()
    calibrating_align=0
    x1, x2, z1, z2=0,0,0,0
    c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")

calibrationbar.add_command(label="Calibrate eye align error",command=calibtrate_align_error)
next_but=tk.Button(win,text="NEXT",command=first_calibration,padx=5,pady=2)
cal_cancel=tk.Button(text="CANCEL",padx=5,pady=2,command=cancel_calibration)
calibration_label1=tk.Label(win,text="")
calibration_label2=tk.Label(win,text="")
calibration_label3=tk.Label(win,text="")
cal_add_but=tk.Button(win,text="ADD",command=add_align_calibration,padx=8,pady=3)
cal_c2_but=tk.Button(win,text="PASTE",command=set_cal_c2,padx=5,pady=1)
cal_return=tk.Button(text="APPLY",padx=4,pady=1,command=returncalc2)
cal_clear=tk.Button(text="CLEAR",padx=4,pady=1,command=cal_clear_list)

# Calibration option help
calibrationbar.add_separator()
calibrationhelp=tk.Menu(calibrationbar,tearoff=False)
calibrationbar.add_cascade(label="Help",menu=calibrationhelp)

helpeye=tk.Menu(calibrationhelp,tearoff=False)
calibrationhelp.add_cascade(label="Eye allign error",menu=helpeye)
helpeye.add_cascade(label="(Affects all mode)")
helpeye.add_cascade(label="(How accurate you can allign cursor to the eye)")
helpeye.add_cascade(label="(Pre-1.21.100)")
helpeye.add_cascade(label="0.03: Monitor pixel perfect")
helpeye.add_cascade(label="0.3: Minecraft pixel perfect")
helpeye.add_cascade(label="1: Within center third of the eye")
helpeye.add_cascade(label="4: Within the eye")
helpeye.add_cascade(label="(1.21.100+)")
helpeye.add_cascade(label="0.03: Monitor pixel perfect")
helpeye.add_cascade(label="0.15: Minecraft pixel perfect")
helpeye.add_cascade(label="0.5: Within center third of the eye")
helpeye.add_cascade(label="2: Within the eye")

helppixel=tk.Menu(calibrationhelp,tearoff=False)
calibrationhelp.add_cascade(label="Pixel count error",menu=helppixel)
helppixel.add_cascade(label="(Affects corner+facing mode)")
helppixel.add_cascade(label="(How accurate you can measure distance between cursor and vertex)")
helppixel.add_cascade(label="0.01: Count monitor pixel")
helppixel.add_cascade(label="0.03: Count minecraft pixel")
helppixel.add_cascade(label="0.3: Count pixels to nearest integer")

helppf=tk.Menu(calibrationhelp,tearoff=False)
calibrationhelp.add_cascade(label="Pixel perfect error",menu=helppf)
helppf.add_cascade(label="(Affects pixel perfect mode)")
helppf.add_cascade(label="(How accurate you can measure pixel shift)")
helppf.add_cascade(label="(Pre-1.21.100)")
helppf.add_cascade(label="0.03: Count pixel shift to one decimal place")
helppf.add_cascade(label="0.075: Count pixel shift to nearest quarter")
helppf.add_cascade(label="0.3: Count pixel shift to nearest integer")
helppf.add_cascade(label="(1.21.100+)")
helppf.add_cascade(label="0.03: Count pixel shift to monitor pixel perfect")
helppf.add_cascade(label="0.075: Count pixel shift to nearest half")
helppf.add_cascade(label="0.15: Count pixel shift to nearest integer")

# Input Coordinate
add_but=tk.Button(win,text="ADD",command=add_point,padx=8,pady=3)
add_but.place(x=265,y=19)
x1_inp=tk.Entry(win,width=8)
z1_inp=tk.Entry(win,width=8)
x2_inp=tk.Entry(win,width=8)
z2_inp=tk.Entry(win,width=8)
pixel_inp=tk.Entry(win,width=8)
set_mode()

# Datas
tk.Label(win,text="DATA").place(x=23,y=83,anchor=tk.CENTER)
listdata=tk.Listbox(win,height=8,width=15)
listdata.place(x=5,y=94)

del_but=tk.Button(win,text="DELETE",command=del_point,padx=2,pady=1)
del_but.place(x=5,y=243)
clear_but=tk.Button(win,text="CLEAR",command=clear,padx=2,pady=1)
clear_but.place(x=63,y=243)

# Visualization
labels=[[] for i in range(9)]
for i in range(9):
    R=tk.Label(win,text="")
    R.place(x=160,y=102+20*i,anchor=tk.CENTER)
    labels[i].append(R)
    R=tk.Label(win,text="")
    R.place(x=240,y=102+20*i,anchor=tk.CENTER)
    labels[i].append(R)
    R=tk.Label(win,text="")
    R.place(x=308,y=102+20*i,anchor=tk.CENTER)
    labels[i].append(R)
    R=tk.Label(win,text="")
    R.place(x=360,y=102+20*i,anchor=tk.CENTER)
    labels[i].append(R)

# C++ functions
dll1=ctypes.CDLL(path("resource/prior.dll"))
PRIOR=dll1.calculate_prior
PRIOR.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,
                ctypes.POINTER(ctypes.c_double),ctypes.c_int,ctypes.POINTER(Result),
                ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.c_int]
PRIOR.restype=ctypes.c_int

UPDATE=dll2.update_prob
UPDATE.argtypes=[ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double,
                 ctypes.POINTER(ctypes.c_double),ctypes.c_int,ctypes.POINTER(Result),ctypes.c_int,
                 ctypes.POINTER(ctypes.c_double)]
UPDATE.restype=ctypes.c_int

OutputArrayType=ctypes.c_double*100
info=OutputArrayType()

UPDATEPF=dll2.update_prob_pf
UPDATEPF.argtypes=[ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double,
                 ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_int,
                 ctypes.POINTER(ctypes.c_double),ctypes.c_int,ctypes.POINTER(Result),ctypes.c_int,
                   ctypes.POINTER(ctypes.c_double)]
UPDATEPF.restype=ctypes.c_int

PROBWITHIN=dll2.prob_within
PROBWITHIN.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.POINTER(Result),ctypes.c_int]
PROBWITHIN.restype=ctypes.c_double

PROBWITHIN2=dll2.prob_within2
PROBWITHIN2.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.POINTER(Result),ctypes.c_int]
PROBWITHIN2.restype=ctypes.c_double

PROBWITHIN3=dll2.prob_within3
PROBWITHIN3.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.POINTER(Result),ctypes.c_int,ctypes.POINTER(Result),ctypes.POINTER(ctypes.c_double)]
PROBWITHIN3.restype=ctypes.c_int


VILLAGEGRID=dll2.village_grid
VILLAGEGRID.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.POINTER(Result),ctypes.c_int,ctypes.POINTER(Result),ctypes.POINTER(ctypes.c_double)]
VILLAGEGRID.restype=ctypes.c_int

# precalculated lists
DoubleArrayType=ctypes.c_double*len(vilprob16)
a_vilprob16=DoubleArrayType(*vilprob16)
DoubleArrayType=ctypes.c_double*len(vilprob)
a_vilprob=DoubleArrayType(*vilprob)
DoubleArrayType=ctypes.c_double*len(pdf)
a_pdf=DoubleArrayType(*pdf)

DoubleArrayType=ctypes.c_double*len(distprob)
a_distprob=DoubleArrayType(*distprob)
DoubleArrayType=ctypes.c_double*len(distprob16)
a_distprob16=DoubleArrayType(*distprob16)

# Calculate
def calculate_prior(x1,z1):
    global res, lencand
    
    prev_layout=(game_version.get()=="Pre 1.18.30")
    limit=int(cur_within.get()/16)
    maxchunk=(limit*2)**2
    OutputArrayType=Result*maxchunk
    res=OutputArrayType()

    based_on_simul=int(cur_prior.get()=="Simulation")
    
    if prev_layout:
        lencand=PRIOR(int(x1),int(z1),limit,1,based_on_simul,a_vilprob16,len(vilprob16),res,info,a_distprob16,len(distprob16))
    else:
        lencand=PRIOR(int(x1),int(z1),limit,0,based_on_simul,a_vilprob,len(vilprob),res,info,a_distprob,len(distprob))
    
def add_prob(n,prior):
    start_time=time.time()
    global res, lencand
    x1=pt[n][0]
    z1=pt[n][1]
    x2=pt[n][2]
    z2=pt[n][3]

    # prior probability
    if prior:
        calculate_prior(x1,z1)
        print("PRIOR")

    # estimating error
    dist=((x1-x2)**2+(z1-z2)**2)**0.5
    error_precision=-1000
    if game_version.get()=="1.21.100+":
        error_angle=math.atan(max(0.06,pt_err[n])/12/16)
    else:
        error_angle=math.atan(pt_err[n]/12/16)
    if pt_mode[n]=="Pixel Perfect":
        error_angle=error_angle+0.01
    elif pt_mode[n]=="Corner+Facing":
        error_precision=math.atan(pt_prec[n]/16/0.3)
        error_dist=0
    elif pt_mode[n]=="Mouse Tracking":
        error_angle=error_angle+0.01
        error_prec1=math.pi/2/pt[n][3]*0.3
        ndata=int(default[12])
        k=min(0.05,max(0.02/int(default[12]),pt[n][4]/pt[n][3]))
        error_prec2=pt[n][5]/pt[n][3]*k*math.pi/2
        error_precision=(error_prec1**2+error_prec2**2)**0.5
    if error_precision==-1000:
        if pt_coord[n]=="Copy+Paste":
            error_precision=0.01/dist*0.2339
            error_dist=0.3/100
        elif pt_coord[n]=="Copy+Paste (Corner)":
            error_precision=0.01/dist*0.1654
            error_dist=0.212/100
        elif pt_coord[n]=="Show Coordinate":
            error_precision=1/dist*0.2339
            error_dist=0.3
        else:
            if pt_manual[n]=="Show coordinate":
                error_precision=1/dist*0.2339
                error_dist=0.3
            elif pt_manual[n]=="Count minecraft pixel":
                error_precision=(1/16)/dist*0.2339
                error_dist=0.01875
            elif pt_manual[n]=="Copy coordinate UI":
                error_precision=0.01/dist*0.2339
                error_dist=0.3/100
            else:
                error_precision=(1/1500)/dist*0.2339
                error_dist=0.0002
    error_combine=(error_angle**2+error_precision**2)**0.5
    print(["error",error_angle,error_precision,error_combine])

    # update
    if pt_mode[n]=="Coord+Coord" or pt_mode[n]=="Corner+Facing":
        lencand=UPDATE(x1,z1,x2,z2,error_combine,a_pdf,len(pdf),res,lencand,info)
    elif pt_mode[n]=="Pixel Perfect":
        newver=int(game_version.get()=="1.21.100+")
        if newver:
            lencand=UPDATEPF(x1,z1,x2,z2,pt_pixel[n],error_combine,pt_pixel_err[n],error_dist,1,a_pdf,len(pdf),res,lencand,info)
        else:
            lencand=UPDATEPF(x1,z1,x2,z2,pt_pixel[n],error_combine,pt_pixel_err[n]*2,error_dist,0,a_pdf,len(pdf),res,lencand,info)
        print(["PF ERROR",info[19],info[20],info[21],info[22]])
    elif pt_mode[n]=="Mouse Tracking":
        x2=x1+math.cos(pt[n][2]/pt[n][3]*math.pi/2)*10
        z2=z1+math.sin(pt[n][2]/pt[n][3]*math.pi/2)*10
        lencand=UPDATE(x1,z1,x2,z2,error_combine,a_pdf,len(pdf),res,lencand,info)

    end_time=time.time()
    print(["CALCULATION TIME",end_time-start_time])
    print(["info",lencand]+info[:4])

# Display
def display():
    global gridres, lengrid, prob2, withinres
    
    a=time.time()
    global prob_dis
    show_stronghold_dig=0
    show_bt_dig=0
    
    cur_pc_value=cur_pc.get()
    pc2=int((cur_pc_value*16)**2)
    pc2_chunk=int(cur_pc_value**2)

    # initial state
    if len(pt)==0:
        for i in range(len(labels)):
            for j in range(4):
                labels[i][j].config(text="")
        return()

    # Village grid
    if cur_pc_value==-1:
        prev_layout=(game_version.get()=="Pre 1.18.30")
        limit=int(cur_within.get()/16)
        if prev_layout:
            gridlimit=math.ceil(limit/27)+3
        else:
            gridlimit=math.ceil(limit/34)+3
        maxchunk=(gridlimit*2+1)**2
        OutputArrayType=Result*maxchunk
        gridres=OutputArrayType()

        lengrid=VILLAGEGRID(int(pt[-1][0]),int(pt[-1][1]),gridlimit,int(prev_layout),res,lencand,gridres,info)

        if cur_dismean.get()=="Show":
            ndis=min(8,lengrid)
        else:
            ndis=min(9,lengrid)

        prob_dis=[]
        for i in range(ndis):
            prob_dis.append([gridres[i].prob,i,gridres[i].x,gridres[i].z,0,0])
    else:
        if cur_dismean.get()=="Show":
            ndis=min(8,lencand)
        else:
            ndis=min(9,lencand)

        prob_dis=[]
        for i in range(ndis):
            prob_dis.append([res[i].prob,i,res[i].x*16+4,res[i].z*16+4,res[i].x*8,res[i].z*8])

    # prob within
    ind=[i for i in range(ndis)]
    prob2=[]
    if cur_pc_value>0:
        OutputArrayType=Result*100
        withinres=OutputArrayType()
        max_ind=PROBWITHIN3(int(pt[-1][0]),int(pt[-1][1]),cur_within.get(),pc2_chunk,res,lencand,withinres,info)
        if max_ind>=ndis:
            ind[-1]=max_ind
            i=max_ind
            prob_dis[-1]=[res[i].prob,i,res[i].x*16+4,res[i].z*16+4,res[i].x*8,res[i].z*8]
        for i in range(len(ind)):
            prob2.append(withinres[ind[i]].prob)
    
    # Display
    for i in range(9):
        for j in range(4):
            labels[i][j].config(text="")
        
    for i in range(ndis):
        if cur_pc_value==-1:
            labels[i][0].config(text="("+str(prob_dis[i][2])+","+str(prob_dis[i][3])+")")
            labels[i][1].config(text="("+str(prob_dis[i][2]//8)+","+str(prob_dis[i][3]//8)+")")
            k=prob_dis[i][0]
        else:
            j=prob_dis[i][1]
            labels[i][0].config(text="("+str(prob_dis[i][2])+","+str(prob_dis[i][3])+")")
            labels[i][1].config(text="("+str((prob_dis[i][2]//8))+","+str((prob_dis[i][3]//8))+")")
            k=prob_dis[i][0]
            
        if k<0.05:
            k2=k*(1/0.05)
            col_code=[int(max_col[j]*(k2/2)) for j in range(3)]
        else:
            k2=(k-0.05)*(1/0.95)
            col_code=[int(max_col[j]*(0.5+k2/2)) for j in range(3)]
        if i==0 and prob_dis[i][0]>2/lencand:
            labels[i][2].config(text=disprob2(prob_dis[i][0]),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft2)
        else:
            labels[i][2].config(text=disprob2(prob_dis[i][0]),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft)

        if cur_pc_value>0:
            col_code=[int(max_col[j]*(prob2[i])) for j in range(3)]
            if max(prob2)==prob2[i] and prob2[i]>0.1:
                labels[i][3].config(text=disprob2(prob2[i]),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft2)
            else:
                labels[i][3].config(text=disprob2(prob2[i]),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft)
        else:
            labels[i][3].config(text="")

    if cur_dismean.get()=="Show":
        if len(pt)==0:
            mean_x,mean_z,mean_net_x,mean_net_z=0,0,0,0
        else:
            mean_x=round(info[1])
            mean_z=round(info[2])
            mean_net_x=mean_x//8
            mean_net_z=mean_z//8
        col_code=max_col
        labels[8][0].config(text="("+str(mean_x)+","+str(mean_z)+")")
        labels[8][1].config(text="("+str(mean_net_x)+","+str(mean_net_z)+")")
        labels[8][2].config(text="Mean",fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft)

        if cur_pc_value>0:
            p2=PROBWITHIN2(mean_x,mean_z,pc2,res,lencand)
            col_code=[int(max_col[i]*p2) for i in range(3)]
            labels[8][3].config(text=disprob2(p2),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft)
        else:
            labels[i][3].config(text="")

    print(["DISPLAY TIME",time.time()-a])
        
# Result
tk.Label(win,text="OVERWORLD").place(x=160,y=83,anchor=tk.CENTER)
tk.Label(win,text="NETHER").place(x=240,y=83,anchor=tk.CENTER)
PROB_Label=tk.Label(win,text="PROB")
PROB_Label.place(x=308,y=83,anchor=tk.CENTER)
if cur_pc.get()<0:
        PROB_Label.config(text="PROB(Grid)")
else:
    PROB_Label.config(text="PROB")
        
if cur_pc.get()>0:
    pc_lab=tk.Label(win,text="≤"+str(12)+"C")
else:
    pc_lab=tk.Label(win,text="")
pc_lab.place(x=360,y=83,anchor=tk.CENTER)
set_version()

# Close
def close():
    # Save setting
    new_default=[str(cur_error_angle.get()),str(cur_error_pixel.get()),str(cur_pixel_perfect.get())]
    new_default=new_default+[cur_input_mode.get(),cur_cinp.get(),str(cur_pc.get()),cur_dismean.get()]
    new_default=new_default+[game_version.get(),cur_prior.get(),str(cur_within.get())]
    new_default=new_default+[str(default[10]),str(default[11]),str(default[12]),str(default[13]),cur_manual_input.get()]
    f=open("StroCate_setting.csv","w",newline="")
    a=csv.writer(f)
    a.writerow(new_default)
    a.writerow(cur_hotkey)
    a.writerow(["preset","align","pixel","pixper","mode","coordinate","str within","mean","version","prior","search rad","manual input"])
    for i in range(len(preset_name)):
        a.writerow([preset_name[i]]+preset_default[i])
    f.close()

    # Undo keybind
    for i in range(len(hotkey_desc)):
        bindglobal[i].stop()

    # Close window
    win.quit()
    win.destroy()
    os._exit(0)
win.protocol("WM_DELETE_WINDOW",close)

# Display
win.config(menu=menubar)
win.mainloop()
