# Import modules
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
import pyperclip, math, csv, os, webbrowser
from functools import partial

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

pt=[]
pt_mode=[]
pt_prec=[]
pt_err=[]
pt_coord=[]

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
def rgb_to_hex(r, g, b):
  return '#{:02X}{:02X}{:02X}'.format(r, g, b)

# Window
win=tk.Tk()
win.title("/StroCate: Bedrock Stronghold Calculator")
win.geometry("400x320+0+100")
win.resizable(False,False)
win.attributes("-topmost",True)
win.iconbitmap(path("icon.ico"))
ft=font.Font(family="Malgun Gothic",size=10)
ft2=font.Font(family="Malgun Gothic",size=10,underline=True)
ft_small=font.Font(family="Malgun Gothic",size=8)
win.option_add("*Font",ft)

# Info bar
def set_infobar():
    dis="AlignE: "+str(cur_error_angle.get())+" / "
    dis=dis+"PixelE: "+str(cur_error_pixel.get())+" / "
    dis=dis+"Coord: "+cur_cinp.get()+" / "
    dis=dis+game_version.get()+" / "
    dis=dis+"~"+str(cur_within.get())
    option_info.config(text=dis)
option_info=tk.Label(win,text="AlignE: 0.3 / PixelE: 0.1 / Coord: Copy+Paste / 1.18.30+ / ~4000",font=ft_small,fg="#888888")
option_info.place(x=0,y=278)

# Menu bar
menubar=tk.Menu(win)
options=tk.Menu(menubar,tearoff=False)
menubar.add_cascade(label="Options",menu=options)
about=tk.Menu(menubar,tearoff=False)
menubar.add_cascade(label="About",menu=about)

# About
about.add_cascade(label="/StroCate: Bedrock Stronghold Calculator")
about.add_cascade(label="Made by LHS1219")
about.add_cascade(label="Version 2.1 (2025.09.13)")
about.add_separator()
def open_github():
    webbrowser.open("https://github.com/pf1219/StroCate-MCBE_Stronghold_Calculator")
def open_youtube():
    webbrowser.open("https://www.youtube.com/@lhs1219")
about.add_cascade(label="Open Github",command=open_github)
about.add_cascade(label="Open Youtube",command=open_youtube)

# Error options
## Align
acc_list=[0.03,0.05,0.075,0.1,0.2,0.3,0.4,0.5,0.75,1,1.5,2,4]
cur_error_angle=tk.DoubleVar()
cur_error_angle.set(0.3)
alignerrormenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Eye Align Error",menu=alignerrormenu)
for i in range(len(acc_list)):
    alignerrormenu.add_radiobutton(label=acc_list[i],variable=cur_error_angle,value=acc_list[i],command=set_infobar)

## Pixel
pixel_list=[0.01,0.03,0.05,0.075,0.1,0.15,0.2,0.3]
cur_error_pixel=tk.DoubleVar()
cur_error_pixel.set(0.1)
pixelerrormenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Pixel Count Error",menu=pixelerrormenu)
for i in range(len(pixel_list)):
    pixelerrormenu.add_radiobutton(label=pixel_list[i],variable=cur_error_pixel,value=pixel_list[i],command=set_infobar)

# Input options
## Mode
def set_mode():
    global x1,x2,z1,z2
    c1_but.place_forget()
    c2_but.place_forget()
    x1_inp.place_forget()
    x2_inp.place_forget()
    z1_inp.place_forget()
    z2_inp.place_forget()
    facing_dir.place_forget()
    pixel_inp.place_forget()
    if cur_cinp.get()=="Copy+Paste" or cur_cinp.get()=="Copy+Paste (Corner)":
        c1_but.place(x=200,y=5)
        c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
        if cur_input_mode.get()=="Coord+Coord":
            x2,z2=0,0
            c2_dis.config(text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")
            c2_but.place(x=200,y=35)
        else:
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
        if cur_input_mode.get()=="Coord+Coord":
            c2_dis.config(text="Coord 2:")
            x2_inp.place(x=80,y=38)
            z2_inp.place(x=160,y=38)
        else:
            c2_dis.config(text="Direction:")
            facing_dir.set("Facing")
            facing_dir.place(x=90,y=37)
            pixel_inp.delete(0,tk.END)
            pixel_inp.insert(0,"Pixel")
            pixel_inp.place(x=175,y=38)
    set_infobar()

cur_input_mode=tk.StringVar()
cur_input_mode.set("Coord+Coord")
inputmodemenu=tk.Menu(options,tearoff=False)
options.add_separator()
options.add_cascade(label="Input Mode",menu=inputmodemenu)
inputmodemenu.add_radiobutton(label="Coord+Coord",value="Coord+Coord",variable=cur_input_mode,command=set_mode)
inputmodemenu.add_radiobutton(label="Corner+Facing",value="Corner+Facing",variable=cur_input_mode,command=set_mode)

## Coordinate
cur_cinp=tk.StringVar()
cur_cinp.set("Copy+Paste")
cinpmenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Coordinate Input",menu=cinpmenu)
cinpmenu.add_radiobutton(label="Copy+Paste",value="Copy+Paste",variable=cur_cinp,command=set_mode)
cinpmenu.add_radiobutton(label="Copy+Paste (Corner)",value="Copy+Paste (Corner)",variable=cur_cinp,command=set_mode)
cinpmenu.add_radiobutton(label="Show Coordinate",value="Show Coordinate",variable=cur_cinp,command=set_mode)
cinpmenu.add_radiobutton(label="Count Block Pixels",value="Block Pixel",variable=cur_cinp,command=set_mode)
cinpmenu.add_radiobutton(label="Count Monitor Pixels",value="Monitor Pixel",variable=cur_cinp,command=set_mode)

# Display options
pc_list=[0,6,8,10,12,14,16,18,20]
cur_pc=tk.IntVar()
cur_pc.set(12)
pcmenu=tk.Menu(options,tearoff=False)
options.add_separator()
options.add_cascade(label="Probability Within",menu=pcmenu)
def set_pc(inp):
    if inp==0:
        pc_lab.config(text="")
    else:
        pc_lab.config(text="≤"+str(inp)+"C")
    update()
pcmenu.add_radiobutton(label="Off",value=0,variable=cur_pc,command=partial(set_pc,0))
for i in range(1,len(pc_list)):
    pcmenu.add_radiobutton(label=str(pc_list[i])+" Chunks",value=pc_list[i],variable=cur_pc,command=partial(set_pc,pc_list[i]))

cur_dismean=tk.StringVar()
cur_dismean.set("Hide")
dismeanmenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Display Mean",menu=dismeanmenu)
def set_dismean():
    update()
dismeanmenu.add_radiobutton(label="Show",value="Show",variable=cur_dismean,command=set_dismean)
dismeanmenu.add_radiobutton(label="Hide",value="Hide",variable=cur_dismean,command=set_dismean)

# Load data
def set_version():
    global chunk_x,chunk_z,prob,cand_x,cand_z,stair_x,stair_z,net_x,net_z,lencand, prob_init
    if game_version.get()=="1.18.30+":
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
    update()
    set_infobar()
    
# Game version
game_version=tk.StringVar()
game_version.set("1.18.30+")
gameversionmenu=tk.Menu(options,tearoff=False)
options.add_separator()
options.add_cascade(label="Game Version",menu=gameversionmenu)
gameversionmenu.add_radiobutton(label="1.18.30+",value="1.18.30+",variable=game_version,command=set_version)
gameversionmenu.add_radiobutton(label="Pre 1.18.30",value="Pre 1.18.30",variable=game_version,command=set_version)

cur_prior=tk.StringVar()
cur_prior.set("Simulation")
priormenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Prior Probability",menu=priormenu)
def set_prior():
    update()
priormenu.add_radiobutton(label="Based on Simulation",value="Simulation",variable=cur_prior,command=set_prior)
priormenu.add_radiobutton(label="Uniform Probability",value="Uniform",variable=cur_prior,command=set_prior)

# Stronghold within
cur_within=tk.IntVar()
cur_within.set(4000)
withinmenu=tk.Menu(options,tearoff=False)
options.add_cascade(label="Stronghold Within",menu=withinmenu)
withinmenu.add_radiobutton(label="2000",value=2000,variable=cur_within,command=set_version)
withinmenu.add_radiobutton(label="3000",value=3000,variable=cur_within,command=set_version)
withinmenu.add_radiobutton(label="4000",value=4000,variable=cur_within,command=set_version)

# Add coordinate
x1,z1,x2,z2=0,0,0,0

def set_c1():
    global x1, z1
    try:
        inp=pyperclip.paste()
        inp=inp.split(" ")
        x1=float(inp[0])
        z1=float(inp[2])
        if cur_input_mode.get()=="Corner+Facing" or cur_cinp.get()=="Copy+Paste (Corner)":
            if round(x1%1,1) not in [0.3,0.7] or round(z1%1,1) not in [0.3,0.7]:
                x1,z1=0,0
    except:
        pass
    c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")

def set_c2():
    global x2, z2
    try:
        inp=pyperclip.paste()
        inp=inp.split(" ")
        x2=float(inp[0])
        z2=float(inp[2])
    except:
        pass
    c2_dis.config(text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")

def add_point():
    global pt, x1, x2, z1, z2, pt_mode, pt_prec, pt_err, pt_coord
    if cur_cinp.get()=="Show Coordinate" and cur_input_mode.get()=="Coord+Coord":
        try:
            x1=int(x1_inp.get())+0.5
            x2=int(x2_inp.get())+0.5
            z1=int(z1_inp.get())+0.5
            z2=int(z2_inp.get())+0.5
        except:
            x1,x2,z1,z2=0,0,0,0
    elif cur_cinp.get()=="Show Coordinate":
        try:
            x1=float(x1_inp.get())
            z1=float(z1_inp.get())
        except:
            x1,z1=0,0
    elif (cur_cinp.get()=="Block Pixel" or cur_cinp.get()=="Monitor Pixel") and cur_input_mode.get()=="Coord+Coord":
        try:
            x1=float(x1_inp.get())
            x2=float(x2_inp.get())
            z1=float(z1_inp.get())
            z2=float(z2_inp.get())
        except:
            x1,x2,z1,z2=0,0,0,0
    elif (cur_cinp.get()=="Block Pixel" or cur_cinp.get()=="Monitor Pixel"):
        try:
            x1=float(x1_inp.get())
            z1=float(z1_inp.get())
        except:
            x1,z1=0,0
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
            listdata.insert(0,str(cur_error_angle.get())+'/'+f'{x1:.0f}'+","+f'{z1:.0f}'+"/"+f'{x2:.0f}'+","+f'{z2:.0f}')
            x1,x2,z1,z2=0,0,0,0
            if cur_cinp.get()=="Copy+Paste" or cur_cinp.get()=="Copy+Paste (Corner)":
                c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
                c2_dis.config(text="Coord 2: ("+f'{x2:.2f}'+","+f'{z2:.2f}'+")")
            else:
                x1_inp.delete(0,tk.END)
                x2_inp.delete(0,tk.END)
                z1_inp.delete(0,tk.END)
                z2_inp.delete(0,tk.END)
            update()
    else:
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
                x1,x2,z1,z2=0,0,0,0
                if cur_cinp.get()=="Copy+Paste" or cur_cinp.get()=="Copy+Paste (Corner)":
                    c1_dis.config(text="Coord 1: ("+f'{x1:.2f}'+","+f'{z1:.2f}'+")")
                else:
                    x1_inp.delete(0,tk.END)
                    x2_inp.delete(0,tk.END)
                    z1_inp.delete(0,tk.END)
                    z2_inp.delete(0,tk.END)
                update()
        
def del_point():
    global pt, pt_mode, pt_prec, pt_err, pt_coord
    try:
        ind=listdata.curselection()[0]
        listdata.delete(ind)
        pt.pop(ind)
        pt_prec.pop(ind)
        pt_mode.pop(ind)
        pt_err.pop(ind)
        pt_coord.pop(ind)
        update()
    except:
        pass

def error_plus():
    global pt_err
    try:
        ind=listdata.curselection()[0]
        acc_ind=acc_list.index(pt_err[ind])
        if acc_ind<(len(acc_list)-1):
            acc_ind=acc_ind+1
            pt_err[ind]=acc_list[acc_ind]
            listdata.delete(ind)
            if pt_mode=="Coord+Coord":
                listdata.insert(ind,str(pt_err[ind])+'/'+f'{pt[ind][0]:.0f}'+","+f'{pt[ind][1]:.0f}'+"/"+f'{pt[ind][2]:.0f}'+","+f'{pt[ind][3]:.0f}')
            else:
                listdata.insert(ind,str(pt_err[ind])+'/'+f'{pt[ind][0]:.0f}'+","+f'{pt[ind][1]:.0f}'+"/"+f'{pt[ind][2]-pt[ind][0]:.2f}'+"/"+f'{pt[ind][3]-pt[ind][1]:.2f}')
            update()
            listdata.select_set(ind)
    except:
        pass

def error_minus():
    global pt_err
    try:
        ind=listdata.curselection()[0]
        acc_ind=acc_list.index(pt_err[ind])
        if acc_ind>0:
            acc_ind=acc_ind-1
            pt_err[ind]=acc_list[acc_ind]
            listdata.delete(ind)
            if pt_mode=="Coord+Coord":
                listdata.insert(ind,str(pt_err[ind])+'/'+f'{pt[ind][0]:.0f}'+","+f'{pt[ind][1]:.0f}'+"/"+f'{pt[ind][2]:.0f}'+","+f'{pt[ind][3]:.0f}')
            else:
                listdata.insert(ind,str(pt_err[ind])+'/'+f'{pt[ind][0]:.0f}'+","+f'{pt[ind][1]:.0f}'+"/"+f'{pt[ind][2]-pt[ind][0]:.2f}'+"/"+f'{pt[ind][3]-pt[ind][1]:.2f}')
            update()
            listdata.select_set(ind)
    except:
        pass

def clear():
    global pt, pt_mode, pt_prec, pt_err, pt_coord
    pt=[]
    pt_mode=[]
    pt_prec=[]
    pt_err=[]
    pt_coord=[]
    listdata.delete(0,tk.END)
    update()

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

add_but=tk.Button(win,text="ADD",command=add_point,padx=8,pady=3)
add_but.place(x=265,y=19)

# Input Coordinate
x1_inp=tk.Entry(win,width=8)
z1_inp=tk.Entry(win,width=8)
x2_inp=tk.Entry(win,width=8)
z2_inp=tk.Entry(win,width=8)

# Datas
tk.Label(win,text="DATA").place(x=23,y=83,anchor=tk.CENTER)
listdata=tk.Listbox(win,height=8,width=15)
listdata.place(x=5,y=94)

del_but=tk.Button(win,text="DELETE",command=del_point,padx=2,pady=1)
del_but.place(x=5,y=243)
clear_but=tk.Button(win,text="CLEAR",command=clear,padx=2,pady=1)
clear_but.place(x=63,y=243)
pl_but=tk.Button(win,text="ER+",command=error_plus,padx=2,pady=1)
# pl_but.place(x=42,y=304)
mn_but=tk.Button(win,text="ER-",command=error_minus,padx=2,pady=1)
# mn_but.place(x=81,y=304)

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
def update():
    global prob, prob_dis
    if cur_prior.get()=="Simulation":
        prob=prob_init.copy()
    else:
        prob=[1/lencand for i in range(len(cand_x))]
    for iteration in range(len(pt)):
        x1=pt[iteration][0]
        z1=pt[iteration][1]
        x2=pt[iteration][2]
        z2=pt[iteration][3]

        dist=((x1-x2)**2+(z1-z2)**2)**0.5
        error_angle=math.atan(pt_err[iteration]/12/16)
        if pt_mode[iteration]=="Corner+Facing":
            error_precision=math.atan(pt_prec[iteration]/16/0.3)
        elif pt_coord[iteration]=="Copy+Paste":
            error_precision=math.atan(0.01*math.sqrt(2)/dist)*0.25
        elif pt_coord[iteration]=="Copy+Paste (Corner)":
            error_precision=math.atan(0.01*math.sqrt(2)/dist)*0.177
        elif pt_coord[iteration]=="Show Coordinate":
            error_precision=math.atan(1*math.sqrt(2)/dist)*0.25
        elif pt_coord[iteration]=="Block Pixel":
            error_precision=math.atan(1/16*math.sqrt(2)/dist)*0.25
        else:
            error_precision=math.atan(1/16/72*math.sqrt(2)/dist)*0.2
        error_combine=(error_angle**2+error_precision**2)**0.5
        print([error_angle,error_precision,error_combine])
        
        a=x1+0.5
        b=z1+0.5
        if x1==x2:
            p=1e100
            q=x1
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

        angle=cal_angle(a,xeye,b,zeye)
        cand_angle=[cal_angle(a,cand_x[i],b,cand_z[i]) for i in range(len(cand_x))]
        angle_dif=[min(abs(cand_angle[i]-angle),abs(cand_angle[i]-angle+2*math.pi),abs(cand_angle[i]-angle-2*math.pi)) for i in range(len(cand_x))]
        prob_mult=[PDF(angle_dif[i]/(error_precision+error_angle)) for i in range(len(cand_x))]
        prob=[prob[i]*prob_mult[i] for i in range(len(cand_x))]
        sumprob=sum(prob)
        if sumprob>0:
            prob=[prob[i]/sumprob for i in range(len(cand_x))]
        else:
            prob=[1/lencand for i in range(len(cand_x))]

    prob_dis=sorted([[prob[i],i] for i in range(len(cand_x))],reverse=True)
    rec_x=round(sum(stair_x[i]*prob[i] for i in range(len(cand_x))))
    rec_z=round(sum(stair_z[i]*prob[i] for i in range(len(cand_x))))
    dist=[(rec_x-stair_x[j])**2+(rec_z-stair_z[j])**2 for j in range(len(cand_x))]
    rec_net_x=rec_x//8
    rec_net_z=rec_z//8

    cur_pc_value=cur_pc.get()
    pc2=(cur_pc_value*16)**2

    if cur_dismean.get()=="Show":
        ndis=8
    else:
        ndis=9

    if cur_pc_value>0:
        prob2=[]
        for i in range(ndis):
            j=prob_dis[i][1]
            p2=sum(prob[l] for l in range(len(cand_x)) if (cand_x[l]-cand_x[j])**2+(cand_z[l]-cand_z[j])**2<pc2)
            prob2.append(p2)
        
    for i in range(ndis):
        j=prob_dis[i][1]
        labels[i][0].config(text="("+str(stair_x[j])+","+str(stair_z[j])+")")
        labels[i][1].config(text="("+str(net_x[j])+","+str(net_z[j])+")")
        k=prob_dis[i][0]
        if k<0.05:
            k2=k*(1/0.05)
            col_code=(math.floor(k2*127),0,0)
        else:
            k2=(k-0.05)*(1/0.95)
            col_code=(math.floor(127+k2*127),0,0)
        if i==0 and prob_dis[i][0]>2/lencand:
            labels[i][2].config(text=disprob2(prob_dis[i][0]),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft2)
        else:
            labels[i][2].config(text=disprob2(prob_dis[i][0]),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft)

        if cur_pc_value>0:
            col_code=(math.floor(255*prob2[i]),0,0)
            if max(prob2)==prob2[i] and prob2[i]>0.1:
                labels[i][3].config(text=disprob2(prob2[i]),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft2)
            else:
                labels[i][3].config(text=disprob2(prob2[i]),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft)
        else:
            labels[i][3].config(text="")

    if ndis==8:
        mean_x=round(sum(cand_x[l]*prob[l] for l in range(len(cand_x))))
        mean_z=round(sum(cand_z[l]*prob[l] for l in range(len(cand_x))))
        mean_net_x=mean_x//8
        mean_net_z=mean_z//8
        labels[8][0].config(text="("+str(mean_x)+","+str(mean_z)+")")
        labels[8][1].config(text="("+str(mean_net_x)+","+str(mean_net_z)+")")
        labels[8][2].config(text="Mean")

        if cur_pc_value>0:
            p2=sum(prob[l] for l in range(len(cand_x)) if (mean_x-cand_x[j])**2+(mean_z-cand_z[j])**2<pc2)
            col_code=(math.floor(255*p2),0,0)
            labels[8][3].config(text=disprob2(p2),fg=rgb_to_hex(col_code[0],col_code[1],col_code[2]),font=ft)
        else:
            labels[i][3].config(text="")

# Result
tk.Label(win,text="OVERWORLD").place(x=160,y=83,anchor=tk.CENTER)
tk.Label(win,text="NETHER").place(x=240,y=83,anchor=tk.CENTER)
tk.Label(win,text="PROB").place(x=308,y=83,anchor=tk.CENTER)
pc_lab=tk.Label(win,text="<"+str(12)+"C")
pc_lab.place(x=360,y=83,anchor=tk.CENTER)
update()

# Display
win.config(menu=menubar)
win.mainloop()
