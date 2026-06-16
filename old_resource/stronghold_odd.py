# Import Modules
import random, math
import pickle

if True:
    data=pickle.load(open("stronghold.p","rb"))
    record_stronghold=data["a"]
    record_status=data["b"]
    record_grid=data["c"]
else:
    record_stronghold=[]
    record_status=[]
    record_grid=[]

village_list=[]
stronghold_list=[]

for iteration in range(50000):
    if (iteration+1)%100==0:
        print(iteration+1)
        
    # Generate Village
    village=[]
    for i in range(-15,16):
        for j in range(-15,16):
            x1=34*i
            x2=34*i+27
            z1=34*j
            z2=34*j+27
            if random.random()<0.267:
                village.append([random.randint(x1,x2),random.randint(z1,z2)])

    # Generate Scattered Stronghold
    stronghold=[1000,1000]
    distance=1000**2*2
    scatter_grid=[]
    for i in range(-3,3):
        for j in range(-3,3):
            x1=200*i+50
            x2=200*i+150
            z1=200*j+50
            z2=200*j+150
            if random.random()<0.25:
                candidate=[random.randint(x1,x2),random.randint(z1,z2)]
                if candidate[0]**2+candidate[1]**2<distance:
                    stronghold=candidate
                    distance=candidate[0]**2+candidate[1]**2
                    scatter_grid=[i,j]
    if stronghold==[1000,1000]:
        status="Fail"
    else:
        status="Scatter"

    # Generate Village Stronghold
    angle=random.random()*math.pi*2
    radius=random.randint(40,55)
    village_ind=-1
    while True:
        cx=math.floor(radius*math.cos(angle))
        cy=math.floor(radius*math.sin(angle))
        generated=False
        candidate=[]
        for x in range(cx-8,cx+8):
            for y in range(cy-8,cy+8):
                if [x,y] in village:
                    village_ind=village.index([x,y])
                    candidate=[x,y]
                    generated=True
                    break
            if generated:
                break
        if generated:
            if candidate[0]**2+candidate[1]**2<distance:
                stronghold=candidate
                distance=candidate[0]**2+candidate[1]**2
                status="Village"
                scatter_grid=[]
            break
        else:
            angle=angle+0.25*math.pi
            radius=radius+4

        if radius>525:
            break

    village_list=village_list+village
    stronghold_save=[0 for i in range(len(village))]
    if village_ind!=-1:
        stronghold_save[village_ind]=1
    stronghold_list=stronghold_list+stronghold_save

    # Save
    record_stronghold.append(stronghold)
    record_status.append(status)
    record_grid.append(scatter_grid)

dist=[(village_list[i][0]**2+village_list[i][1]**2)**0.5*16 for i in range(len(village_list))]
import csv
f=open("by_dist.csv","w",newline=None)
wr=csv.writer(f)
for i in range(100):
    mind=i*25
    maxd=i*25+25
    search=[j for j in range(len(stronghold_list)) if dist[j]>mind and dist[j]<maxd]
    find=sum([stronghold_list[j] for j in search])
    if(len(search)>0):
        p=find/len(search)
    else:
        p=0
    k=[mind,maxd,find,len(search),p]
    print(k)
    wr.writerow(k)

data=dict(a=record_stronghold,b=record_status,c=record_grid)
pickle.dump(data,open("stronghold.p","wb"))
