import pickle

data=pickle.load(open("stronghold.p","rb"))
record_stronghold=data["a"]
record_status=data["b"]
record_grid=data["c"]

scatter_p=record_status.count("Scatter")/len(record_status)

# Candidate
cand=[]
for i in range(-250,251):
    for j in range(-250,251):
        if i**2+j**2<62500:
            cand.append([i,j])

# Scatter Prob
search=[i for i in range(len(record_status)) if record_status[i]=="Scatter"]
k=[round((record_stronghold[i][0]**2+record_stronghold[i][1]**2)**0.5) for i in search]
count=[k.count(i)/len(k) for i in range(0,251)]
count_av=[count[i]+count[i+1]+count[i+2] for i in range(249)]
count_av.insert(0,0)
count_av.append(count[-2]+count[-1])

dist_list=[]
for i in range(len(cand)):
    if cand[i][0] in range(50,151) or cand[i][0] in range(-150,-49):
        if cand[i][1] in range(50,151) or cand[i][1] in range(-150,-49):
            dist_list.append(round((cand[i][0]**2+cand[i][1]**2)**0.5))

adj_count=[]
for i in range(251):
    denom=count_av[i]
    nom=dist_list.count(i-1)+dist_list.count(i)+dist_list.count(i+1)
    if nom>0:
        adj_count.append(denom/nom)
    else:
        adj_count.append(0)

scatter=[0 for i in range(len(cand))]
for i in range(len(cand)):
    if cand[i][0] in range(50,151) or cand[i][0] in range(-150,-49):
        if cand[i][1] in range(50,151) or cand[i][1] in range(-150,-49):
            dist=round((cand[i][0]**2+cand[i][1]**2)**0.5)
            scatter[i]=adj_count[dist]
sumscatter=sum(scatter)
scatter=[scatter[i]/sumscatter*scatter_p for i in range(len(scatter))]
village_p=1-scatter_p

import matplotlib.pyplot as plt
plt.plot(range(251),adj_count,color='red')
plt.xticks([25*i for i in range(11)])
plt.show()

# Village Prob
search=[i for i in range(len(record_status)) if record_status[i]=="Village"]
k=[round((record_stronghold[i][0]**2+record_stronghold[i][1]**2)**0.5) for i in search]
count=[k.count(i)/len(k) for i in range(0,251)]
count_av=[count[i]+count[i+1]+count[i+2] for i in range(249)]
count_av.insert(0,0)
count_av.append(count[-2]+count[-1])

dist_list=[]
for i in range(len(cand)):
    if cand[i][0]%34<=27 and cand[i][1]%34<=27:
        dist_list.append(round((cand[i][0]**2+cand[i][1]**2)**0.5))

adj_count=[]
for i in range(251):
    denom=count_av[i]
    nom=dist_list.count(i-1)+dist_list.count(i)+dist_list.count(i+1)
    if nom>0:
        adj_count.append(denom/nom)
    else:
        adj_count.append(0)

village=[0 for i in range(len(cand))]
for i in range(len(cand)):
    if cand[i][0]%34<=27 and cand[i][1]%34<=27:
        dist=round((cand[i][0]**2+cand[i][1]**2)**0.5)
        village[i]=adj_count[dist]
sumvil=sum(village)
village=[village[i]/sumvil*village_p for i in range(len(village))]

# Process
prob=[scatter[i]+village[i] for i in range(len(village))]
search=[i for i in range(len(prob)) if prob[i]>0]
cand=[cand[i] for i in search]
prob=[prob[i] for i in search]

a=open("pre_prob.csv","w",newline="")
import csv
f=csv.writer(a)
for i in range(len(prob)):
    f.writerow([cand[i][0],cand[i][1],prob[i]])
a.close()
