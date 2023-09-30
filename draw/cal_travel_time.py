# -*- coding: utf-8 -*-
"""
Created on Sat Oct  8 19:39:12 2022

@author: Surface
"""

import pandas as pd
import numpy as np
path='D:/temp/k/RL_AV/micro_RL/output/20/'
pre = np.array(pd.read_csv(path+'lane_list.csv')).tolist()
pre2 = np.array(pd.read_csv(path+'lane_list_d.csv')).tolist()
time=[0]*len(pre[0])
time2=[0]*len(pre2[0])
today_route=["47@365#0","365@511#0","511@464#0","464@39#0","39@320#0","320@448#0","448@314#0","314@497#0","497@336#0","336@498#0","498@313#0","313@309#0","309@48#0"]
ok=[0]*len(pre[0])
auth=[1]*len(pre[0])
for j in range(len(pre[0])):
    for i in range(len(pre)):
        if pre[i][j] in today_route:
            ok[j]=1
        if ok[j]==1:
            time[j]+=1
            if pre[i][j]=='nocar!':
                if pre[i-1][j]!=today_route[-1]:
                    auth[j]=0
                ok[j]=0
                break
ok=[0]*len(pre2[0])
for j in range(len(pre2[0])):
    for i in range(len(pre2)):
        if pre2[i][j] in today_route:
            ok[j]=1
        if ok[j]==1:
            time2[j]+=1
            if pre2[i][j]=='nocar!':
                ok[j]=0
                break
su=0
print(time)
print(auth)
for i in range(len(pre[0])):
    if auth[i]==1:
        su+=time[i]

print(su/sum(auth))
print(sum(time2)/len(time2))
time.append(su/sum(auth))
time2.append(sum(time2)/len(time2))
v = pd.DataFrame([time])
v = v.append(pd.DataFrame([time2]), ignore_index = True)
v.to_csv(path+"travel_time.csv",index=False)