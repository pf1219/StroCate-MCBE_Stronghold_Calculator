# Import modules
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
import pyperclip, math, csv, os, webbrowser, heapq
from functools import partial
from bindglobal import BindGlobal as BG
from pyautogui import screenshot
from numpy import array, uint8, array_equal

# Pyinstaller setting
def path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, "resource/"+relative_path)

# Import data
data=list(csv.reader(open(path("pdf.csv"))))
pdf=[float(data[i][0]) for i in range(len(data))]

data=list(csv.reader(open(path("pre_prob.csv"))))
chunk_x=[int(data[i][0]) for i in range(len(data))]
chunk_z=[int(data[i][1]) for i in range(len(data))]
prob_init=[float(data[i][2]) for i in range(len(data))]
cand_x=[chunk_x[i]*16+2 for i in range(len(data))]
cand_z=[chunk_z[i]*16+2 for i in range(len(data))]
stair_x=[chunk_x[i]*16+4 for i in range(len(data))]
stair_z=[chunk_z[i]*16+4 for i in range(len(data))]
net_x=[chunk_x[i]*2 for i in range(len(data))]
net_z=[chunk_z[i]*2 for i in range(len(data))]
lencand=len(data)

exec(open(path("screen.py")).read())

# Import setting
if "StroCate_setting.csv" in os.listdir():
    default=list(csv.reader(open("StroCate_setting.csv")))[0]
else:
    default=["0.3","0.1","0.1","Coord+Coord","Copy+Paste","12","Hide","1.18.30+","Simulation","4000",0,0,0,0,"Show coordinate"]
while len(default)<14:
    default.append(0)
for i in range(10,14):
    default[i]=float(default[i])
if len(default)<15:
    default.append("Show coordinate")

pt=[]
pt_mode=[]
pt_prec=[]
pt_err=[]
pt_coord=[]
pt_pixel=[]
pt_pixel_err=[]
pt_manual=[]

# Functions
def PDF(x):
    if x>40:
        return(0)
    else:
        return(pdf[round(x*1000)])
def disprob(x):
    a=100*x
    return(f'{a:.2f}'+"%")
def disprob2(x):
    a=100*x
    return(f'{a:.1f}'+"%")
def cal_angle(x1,x2,z1,z2):
    xvec=x2-x1
    zvec=z2-z1
    diagvec=((zvec**2)+(xvec**2))**0.5
    if zvec>0:
        return(math.acos(xvec/diagvec))
    else:
        return(2*math.pi-math.acos(xvec/diagvec))
def vec_angle(vec1,dis1,p3,p4):
    vec2=[p4[0]-p3[0],p4[1]-p3[1]]
    denom=vec1[0]*vec2[0]+vec1[1]*vec2[1]
    nom=dis1*(vec2[0]**2+vec2[1]**2)**0.5
    if nom==0:
        return(1000)
    else:
        return(math.acos(denom/nom))

def rgb_to_hex(r, g, b):
  return '#{:02X}{:02X}{:02X}'.format(r, g, b)

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
win.iconbitmap(path("icon.ico"))
ft=font.Font(family="Malgun Gothic",size=10)
ft2=font.Font(family="Malgun Gothic",size=10,underline=True)
ft_small=font.Font(family="Malgun Gothic",size=8)
win.option_add("*Font",ft)

# Angle measurement setup
exec(open(path("mouse_track.py")).read())

# Info bar
def set_infobar():
    if calibrating==1:
        dis="Calibrating mouse tracking. Press F9, turn 90 degree and press F10"
    elif calibrating==2:
        dis="Calibrating mouse tracking (F9 pressed). Turn 90 degree and press F10"
    else:
        dis="Align: "+str(cur_error_angle.get())+" / "
        dis=dis+"Pixel: "+str(cur_error_pixel.get())+" / "
        dis=dis+"PixPer: "+str(cur_pixel_perfect.get())+" / "
        dis=dis+cur_cinp.get()+" / "
        dis=dis+game_version.get()+" / "
        dis=dis+"~"+str(cur_within.get())
    option_info.config(text=dis)
option_info=tk.Label(win,text="Align: 0.3 / Pixel: 0.1 / PixPer: 0.1 / Copy+Paste / 1.18.30+ / ~4000",font=ft_small,fg="#888888")
option_info.place(x=0,y=278)

# Menu bar
menubar=tk.Menu(win)
options=tk.Menu(menubar,tearoff=False)
menubar.add_cascade(label="Options",menu=options)
helpbar=tk.Menu(menubar,tearoff=False)
menubar.add_cascade(label="Help",menu=helpbar)
about=tk.Menu(menubar,tearoff=False)
menubar.add_cascade(label="About",menu=about)

# Help
hotkeylist=tk.Menu(helpbar,tearoff=False)
helpbar.add_cascade(label="Hotkeys",menu=hotkeylist)
hotkeylist.add_cascade(label="[ : Paste coord 1")
hotkeylist.add_cascade(label="] : Paste coord 2")
hotkeylist.add_cascade(label="= : Add data")
hotkeylist.add_cascade(label="F8 : Minimize window")
hotkeylist.add_cascade(label="F9 : Start mouse tracking")
hotkeylist.add_cascade(label="F10 : End mouse tracking")
helpbar.add_separator()

helpeye=tk.Menu(helpbar,tearoff=False)
helpbar.add_cascade(label="Eye allign error",menu=helpeye)
helpeye.add_cascade(label="(Affects all mode)")
helpeye.add_cascade(label="(How accurate you can allign cursor to the eye)")
helpeye.add_cascade(label="0.03: Monitor pixel perfect")
helpeye.add_cascade(label="0.3: Minecraft pixel perfect")
helpeye.add_cascade(label="1: Within center third of the eye")
helpeye.add_cascade(label="4: Within the eye")

helppixel=tk.Menu(helpbar,tearoff=False)
helpbar.add_cascade(label="Pixel count error",menu=helppixel)
helppixel.add_cascade(label="(Affects corner+facing mode)")
helppixel.add_cascade(label="(How accurate you can measure distance between cursor and vertex)")
helppixel.add_cascade(label="0.01: Count monitor pixel")
helppixel.add_cascade(label="0.03: Count minecraft pixel")
helppixel.add_cascade(label="0.3: Count pixels to nearest integer")

helppf=tk.Menu(helpbar,tearoff=False)
helpbar.add_cascade(label="Pixel perfect error",menu=helppf)
helppf.add_cascade(label="(Affects pixel perfect mode)")
helppf.add_cascade(label="(How accurate you can measure pixel shift)")
helppf.add_cascade(label="0.03: Count pixel shift to one decimal place")
helppf.add_cascade(label="0.3: Count pixel shift to nearest integer")

# About
about.add_cascade(label="/StroCate: Bedrock Stronghold Calculator")
about.add_cascade(label="Made by LHS1219")
about.add_cascade(label="Version 2.43 (2026.01.01.)")
about.add_separator()
def open_github():
    webbrowser.open("https://github.com/pf1219/StroCate-MCBE_Stronghold_Calculator")
def open_youtube():
    webbrowser.open("https://www.youtube.com/@lhs1219")
about.add_cascade(label="Open Github",command=open_github)
about.add_cascade(label="Open Youtube",command=open_youtube)

# Error options
## Align
acc_list=[0.03,0.05,0.075,0.1,0.2,0.3,0.4,0.5,0.75,1.0,1.5,2.0,4.0]
cur_error_angle=tk.DoubleVar()
cur_error_angle.set(float(default[0]))
alignerrormenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Eye align error",menu=alignerrormenu)
for i in range(len(acc_list)):
    alignerrormenu.add_radiobutton(label=acc_list[i],variable=cur_error_angle,value=acc_list[i],command=set_infobar)

## Pixel
pixel_list=[0.01,0.03,0.05,0.075,0.1,0.15,0.2,0.3]
cur_error_pixel=tk.DoubleVar()
cur_error_pixel.set(float(default[1]))
pixelerrormenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Pixel count error",menu=pixelerrormenu)
for i in range(len(pixel_list)):
    pixelerrormenu.add_radiobutton(label=pixel_list[i],variable=cur_error_pixel,value=pixel_list[i],command=set_infobar)

## Pixel Perfect
pixel_perfect_list=[0.03,0.06,0.1,0.2,0.3]
cur_pixel_perfect=tk.DoubleVar()
cur_pixel_perfect.set(float(default[2]))
pixelperfectmenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Pixel perfect error",menu=pixelperfectmenu)
for i in range(len(pixel_perfect_list)):
    pixelperfectmenu.add_radiobutton(label=pixel_perfect_list[i],variable=cur_pixel_perfect,value=pixel_perfect_list[i],command=set_infobar)

## Manual Input
manual_input_list=["Count monitor pixel","Count minecraft pixel","Show coordinate"]
cur_manual_input=tk.StringVar()
cur_manual_input.set(manual_input_list[2])
if cur_manual_input not in manual_input_list:
    cur_manual_input.set(manual_input_list[2])
manualinputmenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Manual coord input",menu=manualinputmenu)
for i in range(len(manual_input_list)):
    manualinputmenu.add_radiobutton(label=manual_input_list[i],variable=cur_manual_input,value=manual_input_list[i],command=set_infobar)

## Mouse Tracking
def start_calibration():
    print(1)
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

mousecalibratemenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Mouse tracking",menu=mousecalibratemenu)
mousecalibratemenu.add_cascade(label="Add calibration data",command=start_calibration)
mousecalibratemenu.add_cascade(label="Clear calibration data",command=clear_calibration)
mousecalibratemenu.add_cascade(label="Mean: "+f'{default[10]:.1f}')
mousecalibratemenu.add_cascade(label="SD: "+f'{default[11]:.1f}')
measuring=0
track_angle=0

# Input options
## Mode
def set_mode():
    global x1,x2,z1,z2, measuring, track_move, track_angle
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
inputmodemenu=tk.Menu(options,tearoff=False)
options.add_separator()
options.add_cascade(label="Input mode",menu=inputmodemenu)
inputmodemenu.add_radiobutton(label="Coord+Coord",value="Coord+Coord",variable=cur_input_mode,command=set_mode)
inputmodemenu.add_radiobutton(label="Corner+Facing",value="Corner+Facing",variable=cur_input_mode,command=set_mode)
inputmodemenu.add_radiobutton(label="Pixel perfect",value="Pixel Perfect",variable=cur_input_mode,command=set_mode)
inputmodemenu.add_radiobutton(label="Mouse tracking",value="Mouse Tracking",variable=cur_input_mode,command=set_mode)

## Coordinate
cur_cinp=tk.StringVar()
cur_cinp.set(default[4])
cinpmenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Coordinate input",menu=cinpmenu)
cinpmenu.add_radiobutton(label="Copy+Paste",value="Copy+Paste",variable=cur_cinp,command=set_mode)
cinpmenu.add_radiobutton(label="Copy+Paste (corner)",value="Copy+Paste (Corner)",variable=cur_cinp,command=set_mode)
cinpmenu.add_radiobutton(label="Show coordinate",value="Show Coordinate",variable=cur_cinp,command=set_mode)
cinpmenu.add_radiobutton(label="Maunal input",value="Manual Input",variable=cur_cinp,command=set_mode)

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
pcmenu=tk.Menu(options,tearoff=False)
options.add_separator()
options.add_cascade(label="Probability within",menu=pcmenu)
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
dismeanmenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Display mean",menu=dismeanmenu)
def set_dismean():
    display()
dismeanmenu.add_radiobutton(label="Show",value="Show",variable=cur_dismean,command=set_dismean)
dismeanmenu.add_radiobutton(label="Hide",value="Hide",variable=cur_dismean,command=set_dismean)

high_col=tk.IntVar()
high_col.set(int(default[13]))
highcolmenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Highlight color",menu=highcolmenu)
def set_highcol():
    display()
highcolmenu.add_radiobutton(label="Red",value=0,variable=high_col,command=set_highcol)
highcolmenu.add_radiobutton(label="Green",value=1,variable=high_col,command=set_highcol)
highcolmenu.add_radiobutton(label="Blue",value=2,variable=high_col,command=set_highcol)

# Load data
def set_version():
    global chunk_x,chunk_z,prob,cand_x,cand_z,stair_x,stair_z,net_x,net_z,lencand, prob_init
    if game_version.get()!="Pre 1.18.30":
        print("1.18.30+")
        data=list(csv.reader(open(path("pre_prob.csv"))))
    else:
        print("Pre 1.18.30")
        data=list(csv.reader(open(path("pre_prob16.csv"))))
    distance=[16*((int(data[i][0]))**2+(int(data[i][1]))**2)**0.5 for i in range(len(data))]
    ind=[i for i in range(len(distance)) if distance[i]<=cur_within.get()]
    chunk_x=[int(data[i][0]) for i in ind]
    chunk_z=[int(data[i][1]) for i in ind]
    prob_init=[float(data[i][2]) for i in ind]
    lencand=len(chunk_x)
    cand_x=[chunk_x[i]*16+2 for i in range(lencand)]
    cand_z=[chunk_z[i]*16+2 for i in range(lencand)]
    stair_x=[chunk_x[i]*16+4 for i in range(lencand)]
    stair_z=[chunk_z[i]*16+4 for i in range(lencand)]
    net_x=[chunk_x[i]*2 for i in range(lencand)]
    net_z=[chunk_z[i]*2 for i in range(lencand)]
    print(lencand)
    load_prob()
    for i in range(len(pt)):
        add_prob(i)
    display()
    set_infobar()
    
# Game version
game_version=tk.StringVar()
game_version.set(default[7])
gameversionmenu=tk.Menu(options,tearoff=False)
options.add_separator()
options.add_cascade(label="Game version",menu=gameversionmenu)
gameversionmenu.add_radiobutton(label="1.21.100+",value="1.21.100+",variable=game_version,command=set_version)
gameversionmenu.add_radiobutton(label="1.18.30+",value="1.18.30+",variable=game_version,command=set_version)
gameversionmenu.add_radiobutton(label="Pre 1.18.30",value="Pre 1.18.30",variable=game_version,command=set_version)

cur_prior=tk.StringVar()
cur_prior.set(default[8])
priormenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Prior probability",menu=priormenu)
def set_prior():
    load_prob()
    for i in range(len(pt)):
        add_prob(i)
    display()
priormenu.add_radiobutton(label="Based on simulation",value="Simulation",variable=cur_prior,command=set_prior)
priormenu.add_radiobutton(label="Uniform probability",value="Uniform",variable=cur_prior,command=set_prior)

# Stronghold within
cur_within=tk.IntVar()
cur_within.set(int(default[9]))
withinmenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Stronghold within",menu=withinmenu)
withinmenu.add_radiobutton(label="2000",value=2000,variable=cur_within,command=set_version)
withinmenu.add_radiobutton(label="3000",value=3000,variable=cur_within,command=set_version)
withinmenu.add_radiobutton(label="4000",value=4000,variable=cur_within,command=set_version)

# Initialize infobar
calibrating=0
set_infobar()

# Add coordinate
x1,z1,x2,z2=0,0,0,0

def set_c1():
    global x1, z1, coords
    try:
        if cur_cinp.get()=="Show Coordinate":
            coords=read_coords()
            print(coords)
            if coords!=-1:
                x1=coords[0]+0.5
                z1=coords[2]+0.5
        else:
            inp=pyperclip.paste()
            inp=inp.split(" ")
            x1=float(inp[0])
            z1=float(inp[2])
            if cur_input_mode.get()=="Corner+Facing" or cur_cinp.get()=="Copy+Paste (Corner)":
                if round(x1%1,1) not in [0.3,0.7] or round(z1%1,1) not in [0.3,0.7]:
                    x1,z1=0,0
    except:
        x2,z2=0,0
    c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")

def set_c2():
    global x2, z2, coords
    try:
        if cur_cinp.get()=="Show Coordinate":
            coords=read_coords()
            print(coords)
            if coords!=-1:
                x2=coords[0]+0.5
                z2=coords[2]+0.5
        else:
            inp=pyperclip.paste()
            inp=inp.split(" ")
            x2=float(inp[0])
            z2=float(inp[2])
    except:
        x2,z2=0,0
    c2_dis.config(text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")

def add_point():
    global pt, x1, x2, z1, z2, pt_mode, pt_prec, pt_err, pt_coord, pt_pixel, pt_pixel_err, pt_manual, track_angle, track_move, sum_abs
    print(x1_inp.get())
    print(z1_inp.get())
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
    print([x1,z1,x2,z2])
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
            listdata.insert(0,str(cur_error_angle.get())+'/'+f'{x1:.0f}'+","+f'{z1:.0f}'+"/"+f'{x2:.0f}'+","+f'{z2:.0f}')
            x1,x2,z1,z2=0,0,0,0
            if cur_cinp.get()=="Copy+Paste" or cur_cinp.get()=="Copy+Paste (Corner)" or cur_cinp.get()=="Show Coordinate":
                c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
                c2_dis.config(text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")
            else:
                x1_inp.delete(0,tk.END)
                x2_inp.delete(0,tk.END)
                z1_inp.delete(0,tk.END)
                z2_inp.delete(0,tk.END)
            add_prob(0)
            display()
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
                listdata.insert(0,str(cur_error_angle.get())+'/'+f'{x1:.0f}'+","+f'{z1:.0f}'+"/"+f'{x2-x1:.2f}'+"/"+f'{z2-z1:.2f}')
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
                add_prob(0)
                display()
    elif cur_input_mode.get()=="Pixel Perfect":
        valid=True
        if cur_cinp.get()=="Copy+Paste (Corner)":
            mod1=round(x1%1,2)
            mod2=round(z1%1,2)
            if (mod1==0.3 or mod1==0.7) and (mod2==0.3 or mod2==0.7):
                valid=True
            else:
                valid=False
        try:
            npixel=float(pixel_inp.get())
            if npixel<=0:
                valid=False
        except:
            valid=False
        if (x1,z1)!=(x2,z2) and valid:
            pt.insert(0,[x1,z1,x2,z2])
            pt_mode.insert(0,cur_input_mode.get())
            pt_err.insert(0,cur_error_angle.get())
            pt_prec.insert(0,0)
            pt_coord.insert(0,cur_cinp.get())
            pt_pixel.insert(0,npixel)
            pt_pixel_err.insert(0,cur_pixel_perfect.get())
            pt_manual.insert(0,cur_manual_input.get())
            listdata.insert(0,str(cur_error_angle.get())+'/'+f'{x1:.0f}'+","+f'{z1:.0f}'+"/"+f'{x2:.0f}'+","+f'{z2:.0f}')
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
            add_prob(0)
            display()
    else:
        valid=True
        if cur_cinp.get()=="Copy+Paste (Corner)":
            mod1=round(x1%1,2)
            mod2=round(z1%1,2)
            if (mod1==0.3 or mod1==0.7) and (mod2==0.3 or mod2==0.7):
                valid=True
            else:
                valid=False
        if valid:
            print([x1,z1])
            pt.insert(0,[x1,z1,track_move,default[10],default[11],sum_abs])
            print([track_move,sum_abs])
            pt_mode.insert(0,cur_input_mode.get())
            pt_err.insert(0,cur_error_angle.get())
            pt_prec.insert(0,0)
            pt_coord.insert(0,cur_cinp.get())
            pt_pixel.insert(0,0)
            pt_pixel_err.insert(0,cur_pixel_perfect.get())
            pt_manual.insert(0,cur_manual_input.get())
            listdata.insert(0,str(cur_error_angle.get())+'/'+f'{x1:.0f}'+","+f'{z1:.0f}'+"/"+str(round(track_angle)))
            x1,x2,z1,z2,track_move,track_angle,sum_abs=0,0,0,0,0,0,0
            if cur_cinp.get()=="Copy+Paste" or cur_cinp.get()=="Copy+Paste (Corner)" or cur_cinp.get()=="Show Coordinate":
                c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
            else:
                x1_inp.delete(0,tk.END)
                x2_inp.delete(0,tk.END)
                z1_inp.delete(0,tk.END)
                z2_inp.delete(0,tk.END)
            c2_dis.config(text="Angle: 0 Deg")
            add_prob(0)
            display()

def del_point():
    global pt, pt_mode, pt_prec, pt_err, pt_coord, pt_pixel, pt_pixel_err, pt_manual
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
        load_prob()
        for i in range(len(pt)):
            add_prob(i)
        display()
    except:
        pass

def clear():
    global pt, pt_mode, pt_prec, pt_err, pt_coord, pt_pixel, pt_pixel_err, pt_manual
    pt=[]
    pt_mode=[]
    pt_prec=[]
    pt_err=[]
    pt_coord=[]
    pt_pixel=[]
    pt_pixel_err=[]
    pt_manual=[]
    listdata.delete(0,tk.END)
    load_prob()
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
def key_press1(event):
    set_c1()
bg=BG()
bg.start()
bg.gbind("<[>",key_press1)

def key_press2(event):
    if cur_input_mode.get()=="Coord+Coord" or cur_input_mode.get()=="Pixel Perfect":
        set_c2()
bg2=BG()
bg2.start()
bg2.gbind("<]>",key_press2)

def key_press3(event):
    add_point()
bg3=BG()
bg3.start()
bg3.gbind("<=>",key_press3)

# Mouse track
sum_move=0
sum_abs=0
def start_track():
    global sum_move, calibrating, measuring, sum_abs
    print("START TRACKING")
    rid = RAWINPUTDEVICE(HID_USAGE_PAGE_GENERIC, HID_USAGE_GENERIC_MOUSE, RIDEV_INPUTSINK, hwnd)
    RegisterRawInputDevices(ct.byref(rid), 1, ct.sizeof(rid))
    sum_move=0
    sum_abs=0
    if calibrating==1:
        calibrating=2
        set_infobar()
    if calibrating==0 and cur_input_mode.get()=="Mouse Tracking" and default[12]>0:
        track_dis.config(text="Align and press F10")
        measuring=2
def key_press4(event):
    start_track()
bg4=BG()
bg4.start()
bg4.gbind("<F9>",key_press4)

def stop_track():
    global sum_move, default, calibrating, track_angle, measuring, track_move, sum_abs
    print("STOP TRACKING")
    rid = RAWINPUTDEVICE(HID_USAGE_PAGE_GENERIC, HID_USAGE_GENERIC_MOUSE, RIDEV_REMOVE, None)
    RegisterRawInputDevices(ct.byref(rid), 1, ct.sizeof(rid))
    print(sum_move)
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
bg5=BG()
bg5.start()
bg5.gbind("<F10>",key_press5)

add_but=tk.Button(win,text="ADD",command=add_point,padx=8,pady=3)
add_but.place(x=265,y=19)

# Iconify
def key_press6(event):
    if win.state()=="iconic":
        win.state("normal")
    else:
        win.state("iconic")
bg6=BG()
bg6.start()
bg6.gbind("<F8>",key_press6)

# Input Coordinate
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

# Calculate
def load_prob():
    global prob
    if cur_prior.get()=="Simulation":
        prob=[[prob_init[i],i,cand_x[i],cand_z[i]] for i in range(len(cand_x))]
    else:
        prob_common=1/lencand
        prob=[[prob_common,i,cand_x[i],cand_z[i]] for i in range(len(cand_x))]

def add_prob(n):
    global prob
    x1=pt[n][0]
    z1=pt[n][1]
    x2=pt[n][2]
    z2=pt[n][3]

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
        error_prec1=math.pi/2/pt[n][3]*0.3
        k=min(0.05,max(0.02,pt[n][4]/pt[n][3]))
        error_prec2=k/(2**0.5)*pt[n][5]/pt[n][3]*math.pi/2
        error_precision=(error_prec1**2+error_prec2**2)**0.5
    if error_precision==-1000:
        if pt_coord[n]=="Copy+Paste":
            error_precision=math.atan(0.01*math.sqrt(2)/dist)*0.25
            error_dist=0.3/100
        elif pt_coord[n]=="Copy+Paste (Corner)":
            error_precision=math.atan(0.01*math.sqrt(2)/dist)*0.177
            error_dist=0.3/100
        elif pt_coord[n]=="Show Coordinate":
            error_precision=math.atan(1*math.sqrt(2)/dist)*0.25
            error_dist=0.3
        else:
            if pt_manual[n]=="Show coordinate":
                error_precision=math.atan(0.3*math.sqrt(2)/dist)*0.2
                error_dist=0.3
            elif pt_manual[n]=="Count minecraft pixel":
                error_precision=math.atan(0.01875*math.sqrt(2)/dist)*0.2
                error_dist=0.01875
            else:
                error_precision=math.atan(0.0002*math.sqrt(2)/dist)*0.2
                error_dist=0.0002
    error_combine=(error_angle**2+error_precision**2)**0.5
    print([error_angle,error_precision,error_combine])

    # Coord+Coord
    if pt_mode[n]=="Coord+Coord" or pt_mode[n]=="Corner+Facing":
        # Line
        a=x1+0.5
        b=z1+0.5
        if x1==x2:
            xeye1=x1
            xeye2=x1
            zeye1=b+143.75**0.5
            zeye2=b-143.75**0.5
        else:
            p=(z2-z1)/(x2-x1)
            q=z1-p*x1
            r=12

            denom1=-1*a*a*p*p+2*a*b*p-2*a*p*q-b*b+2*b*q+p*p*r*r-q*q+r*r
            denom2=a+b*p-p*q
            nom=p*p+1
            xeye1=(denom1**0.5+denom2)/nom
            xeye2=(-1*denom1**0.5+denom2)/nom
            zeye1=p*xeye1+q
            zeye2=p*xeye2+q

        dir_vec=(x2-x1,z2-z1)
        vec1=(xeye1-a,zeye1-b)
        vec2=(xeye2-a,zeye2-b)
        cos1=dir_vec[0]*vec1[0]+dir_vec[1]*vec1[1]
        cos2=dir_vec[0]*vec2[0]+dir_vec[1]*vec2[1]
        if cos1>cos2:
            xeye=xeye1
            zeye=zeye1
        else:
            xeye=xeye2
            zeye=zeye2

        vec_eye=[xeye-a,zeye-b]
        print(vec_eye)
        vec_dist=(vec_eye[0]**2+vec_eye[1]**2)**0.5
        angle_dif=[vec_angle(vec_eye,vec_dist,[a,b],[prob[i][2],prob[i][3]]) for i in range(len(prob))]
        new_prob=[prob[i][0]*PDF(angle_dif[i]/error_combine) for i in range(len(prob))]
        prob=[[new_prob[i],prob[i][1],prob[i][2],prob[i][3]] for i in range(len(prob)) if new_prob[i]>0]
        sumprob=sum(prob[i][0] for i in range(len(prob)))
        if sumprob>0:
            for i in range(len(prob)):
                prob[i][0]=prob[i][0]/sumprob
        else:
            prob_common=1/lencand
            prob=[[prob_common,i,cand_x[i],cand_z[i]] for i in range(len(cand_x))]
    elif pt_mode[n]=="Pixel Perfect":
        # Pixel Perfect
        if game_version.get()=="1.21.100+":
            shift=0.196
        else:
            shift=0.4032
        print(shift)
        vector=[x2-x1,z2-z1]
        new_x1=x1+vector[0]*shift/dist
        new_z1=z1+vector[1]*shift/dist

        a=new_x1+0.5
        b=new_z1+0.5
        if new_z1==z2:
            xeye1=new_x1
            xeye2=new_x1
            zeye1=new_z1+143.75**0.5
            zeye2=new_z1-143.75**0.5
        else:
            p=(x2-new_x1)/(z2-new_z1)*-1
            q=new_z1-p*new_x1
            r=12

            denom1=-1*a*a*p*p+2*a*b*p-2*a*p*q-b*b+2*b*q+p*p*r*r-q*q+r*r
            denom2=a+b*p-p*q
            nom=p*p+1
            xeye1=(denom1**0.5+denom2)/nom
            xeye2=(-1*denom1**0.5+denom2)/nom
            zeye1=p*xeye1+q
            zeye2=p*xeye2+q

        dir_vec=[x2-new_x1,z2-new_z1]
        dir_vec=[dir_vec[1],dir_vec[0]*-1]
        vec1=(xeye1-a,zeye1-b)
        vec2=(xeye2-a,zeye2-b)
        cos1=dir_vec[0]*vec1[0]+dir_vec[1]*vec1[1]
        cos2=dir_vec[0]*vec2[0]+dir_vec[1]*vec2[1]
        if cos1>cos2:
            xeye=xeye1
            zeye=zeye1
        else:
            xeye=xeye2
            zeye=zeye2

        vec_eye=[xeye-a,zeye-b]
        vec_dist=(vec_eye[0]**2+vec_eye[1]**2)**0.5
        angle_dif=[vec_angle(vec_eye,vec_dist,[a,b],[prob[i][2],prob[i][3]]) for i in range(len(prob))]
        new_prob=[prob[i][0]*PDF(angle_dif[i]/error_combine) for i in range(len(prob))]
        prob=[[new_prob[i],prob[i][1],prob[i][2],prob[i][3]] for i in range(len(prob)) if new_prob[i]>0]
        sumprob=sum(prob[i][0] for i in range(len(prob)))
        if sumprob>0:
            for i in range(len(prob)):
                prob[i][0]=prob[i][0]/sumprob
        else:
            prob_common=1/lencand
            prob=[[prob_common,i,cand_x[i],cand_z[i]] for i in range(len(cand_x))]

        pf=pt_pixel[n]
        if game_version.get()=="1.21.100+":
            error_coef=pf/15.604
        else:
            error_coef=pf/47.739
        error_measurement=pt_pixel_err[n]
        error_dist2=pf*error_dist/dist
        error_pf=(error_coef**2+error_measurement**2+error_dist2**2)**0.5
        if game_version.get()=="1.21.100+":
            k=dist*391.857
        else:
            k=dist*185.468
        cand_pf=[k/((prob[i][2]-a)**2+(prob[i][3]-b)**2)**0.5 for i in range(len(prob))]
        pf_dif=[abs(cand_pf[i]-pf) for i in range(len(prob))]
        new_prob=[prob[i][0]*PDF(pf_dif[i]/error_pf) for i in range(len(prob))]
        prob=[[new_prob[i],prob[i][1],prob[i][2],prob[i][3]] for i in range(len(prob)) if new_prob[i]>0]
        sumprob=sum(prob[i][0] for i in range(len(prob)))
        if sumprob>0:
            for i in range(len(prob)):
                prob[i][0]=prob[i][0]/sumprob
        else:
            prob_common=1/lencand
            prob=[[prob_common,i,cand_x[i],cand_z[i]] for i in range(len(cand_x))]
    elif pt_mode[n]=="Mouse Tracking":
        # Mouse tracking
        x2=x1+math.cos(pt[n][2]/pt[n][3]*math.pi/2)*10
        z2=z1+math.sin(pt[n][2]/pt[n][3]*math.pi/2)*10
        a=x1+0.5
        b=z1+0.5
        if x1==x2:
            xeye1=x1
            xeye2=x1
            zeye1=b+143.75**0.5
            zeye2=b-143.75**0.5
        else:
            p=(z2-z1)/(x2-x1)
            q=z1-p*x1
            r=12

            denom1=-1*a*a*p*p+2*a*b*p-2*a*p*q-b*b+2*b*q+p*p*r*r-q*q+r*r
            denom2=a+b*p-p*q
            nom=p*p+1
            xeye1=(denom1**0.5+denom2)/nom
            xeye2=(-1*denom1**0.5+denom2)/nom
            zeye1=p*xeye1+q
            zeye2=p*xeye2+q

        dir_vec=(x2-x1,z2-z1)
        vec1=(xeye1-a,zeye1-b)
        vec2=(xeye2-a,zeye2-b)
        cos1=dir_vec[0]*vec1[0]+dir_vec[1]*vec1[1]
        cos2=dir_vec[0]*vec2[0]+dir_vec[1]*vec2[1]
        if cos1>cos2:
            xeye=xeye1
            zeye=zeye1
        else:
            xeye=xeye2
            zeye=zeye2

        vec_eye=[xeye-a,zeye-b]
        print(vec_eye)
        vec_dist=(vec_eye[0]**2+vec_eye[1]**2)**0.5
        angle_dif=[vec_angle(vec_eye,vec_dist,[a,b],[prob[i][2],prob[i][3]]) for i in range(len(prob))]
        new_prob=[prob[i][0]*PDF(angle_dif[i]/error_combine)**0.5 for i in range(len(prob))]
        prob=[[new_prob[i],prob[i][1],prob[i][2],prob[i][3]] for i in range(len(prob)) if new_prob[i]>0]
        sumprob=sum(prob[i][0] for i in range(len(prob)))
        if sumprob>0:
            for i in range(len(prob)):
                prob[i][0]=prob[i][0]/sumprob
        else:
            prob_common=1/lencand
            prob=[[prob_common,i,cand_x[i],cand_z[i]] for i in range(len(cand_x))]

def display():
    global prob, prob_dis
    cur_pc_value=cur_pc.get()
    pc2=(cur_pc_value*16)**2

    # Village grid
    if cur_pc_value==-1:
        if game_version.get()!="Pre 1.18.30":
            vil_grid=[]
            vil_list=[]
            vil_prob_list=[]
            for i in range(-8,8):
                for j in range(-8,8):
                    vil_grid.append([i,j])
                    vil_list.append([])
                    vil_prob_list.append([])
            for i in range(len(prob)):
                k=prob[i][1]
                if chunk_x[k]%34<28 and chunk_z[k]%34<28:
                    xgrid=chunk_x[k]//34
                    zgrid=chunk_z[k]//34
                    grid_ind=(xgrid+8)*16+(zgrid+8)
                    vil_list[grid_ind].append(k)
                    vil_prob_list[grid_ind].append(prob[i][0])
        else:
            vil_grid=[]
            vil_list=[]
            vil_prob_list=[]
            for i in range(-10,10):
                for j in range(-10,10):
                    vil_grid.append([i,j])
                    vil_list.append([])
                    vil_prob_list.append([])
            for i in range(len(prob)):
                k=prob[i][1]
                if chunk_x[k]%27<18 and chunk_z[k]%27<18:
                    xgrid=chunk_x[k]//27
                    zgrid=chunk_z[k]//27
                    grid_ind=(xgrid+10)*20+(zgrid+10)
                    vil_list[grid_ind].append(k)
                    vil_prob_list[grid_ind].append(prob[i][0])
        prob_dis=[]
        for i in range(len(vil_grid)):
            grid_len=len(vil_prob_list[i])
            if grid_len>0:
                k=[]
                grid_prob=sum(vil_prob_list[i])
                k.append(grid_prob)
                grid_x=round(sum(stair_x[vil_list[i][j]]*vil_prob_list[i][j] for j in range(grid_len))/grid_prob)
                grid_z=round(sum(stair_z[vil_list[i][j]]*vil_prob_list[i][j] for j in range(grid_len))/grid_prob)
                k=k+[grid_x,grid_z,grid_x//8,grid_z//8,vil_grid[i][0],vil_grid[i][1]]
                prob_dis.append(k)
    else:
        prob_dis=[]
        for i in range(len(prob)):
            k=prob[i][1]
            prob_dis.append([prob[i][0],prob[i][1],stair_x[k],stair_z[k],net_x[k],net_z[k]])

    # Sort
    if cur_dismean.get()=="Show":
        ndis=min(8,len(prob_dis))
    else:
        ndis=min(9,len(prob_dis))
    prob_dis=heapq.nlargest(ndis,prob_dis)

    if cur_pc_value>0:
        prob2=[]
        for i in range(ndis):
            j=prob_dis[i][1]
            p2=0
            for l in range(len(prob)):
                if (cand_x[j]-prob[l][2])**2+(cand_z[j]-prob[l][3])**2 < pc2:
                    p2=p2+prob[l][0]
            prob2.append(p2)

    # Display
    for i in range(9):
        for j in range(4):
            labels[i][j].config(text="")
        
    for i in range(ndis):
        if cur_pc_value==-1:
            labels[i][0].config(text="("+str(prob_dis[i][1])+","+str(prob_dis[i][2])+")")
            labels[i][1].config(text="("+str(prob_dis[i][3])+","+str(prob_dis[i][4])+")")
            k=prob_dis[i][0]
        else:
            j=prob_dis[i][1]
            labels[i][0].config(text="("+str(stair_x[j])+","+str(stair_z[j])+")")
            labels[i][1].config(text="("+str(net_x[j])+","+str(net_z[j])+")")
            k=prob_dis[i][0]
            
        if k<0.05:
            k2=k*(1/0.05)
            col_code=[0,0,0]
            col_code[high_col.get()]=math.floor(k2*127)
        else:
            k2=(k-0.05)*(1/0.95)
            col_code=[0,0,0]
            col_code[high_col.get()]=math.floor(127+k2*127)
        if i==0 and prob_dis[i][0]>2/lencand:
            labels[i][2].config(text=disprob2(prob_dis[i][0]),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft2)
        else:
            labels[i][2].config(text=disprob2(prob_dis[i][0]),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft)

        if cur_pc_value>0:
            col_code=[0,0,0]
            col_code[high_col.get()]=math.floor(255*prob2[i])
            if max(prob2)==prob2[i] and prob2[i]>0.1:
                labels[i][3].config(text=disprob2(prob2[i]),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft2)
            else:
                labels[i][3].config(text=disprob2(prob2[i]),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft)
        else:
            labels[i][3].config(text="")

    if cur_dismean.get()=="Show":
        mean_x=round(sum(prob[l][2]*prob[l][0] for l in range(len(prob))))+2
        mean_z=round(sum(prob[l][3]*prob[l][0] for l in range(len(prob))))+2
        mean_net_x=mean_x//8
        mean_net_z=mean_z//8
        labels[8][0].config(text="("+str(mean_x)+","+str(mean_z)+")")
        labels[8][1].config(text="("+str(mean_net_x)+","+str(mean_net_z)+")")
        labels[8][2].config(text="Mean")

        if cur_pc_value>0:
            p2=0
            for l in range(len(prob)):
                if (prob[l][2]-mean_x)**2+(prob[l][3]-mean_z)**2 < pc2:
                    p2=p2+prob[l][0]
            col_code=[0,0,0]
            col_code[high_col.get()]=math.floor(255*p2)
            labels[8][3].config(text=disprob2(p2),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft)
        else:
            labels[i][3].config(text="")

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
    pc_lab=tk.Label(win,text="<"+str(12)+"C")
else:
    pc_lab=tk.Label(win,text="")
pc_lab.place(x=360,y=83,anchor=tk.CENTER)
set_version()
load_prob()
display()

# Close
def close():
    # Stop global binding
    bg.stop()
    bg2.stop()
    bg3.stop()
    bg4.stop()
    bg5.stop()

    # Save setting
    new_default=[str(cur_error_angle.get()),str(cur_error_pixel.get()),str(cur_pixel_perfect.get())]
    new_default=new_default+[cur_input_mode.get(),cur_cinp.get(),str(cur_pc.get()),cur_dismean.get()]
    new_default=new_default+[game_version.get(),cur_prior.get(),str(cur_within.get())]
    new_default=new_default+[str(default[10]),str(default[11]),str(default[12]),str(default[13])]
    f=open("StroCate_setting.csv","w")
    a=csv.writer(f)
    a.writerow(new_default)
    f.close()

    # Close window
    win.destroy()
win.protocol("WM_DELETE_WINDOW",close)

# Display
win.config(menu=menubar)
win.mainloop()
