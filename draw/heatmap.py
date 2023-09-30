# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 15:02:48 2023

@author: Surface
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import colorsys
import seaborn as sns
import random
from matplotlib.pyplot import MultipleLocator

plt.figure(figsize=(5, 5), dpi=200)

def man_cmap(cmap, value=1.):
    
    colors = cmap(np.arange(cmap.N))
    hls = np.array([colorsys.rgb_to_hls(*c) for c in colors[:,:3]])
    hls[:,1] *= value
    rgb = np.clip(np.array([colorsys.hls_to_rgb(*c) for c in hls]), 0,1)
    return mcolors.LinearSegmentedColormap.from_list("", rgb)


path='D:/temp/k/RL_AV/micro_RL/output/100/'
t="0% penetration rate"
pos = np.array(pd.read_csv(path+'dist_list_HDV.csv')).tolist()
speed = np.array(pd.read_csv(path+'speed_list_HDV.csv')).tolist()
total_time=4000
total_length=1800
time_piece=200
place_piece=200
time_interval=float(total_time/time_piece)
place_interval=float(total_length/place_piece)
table=np.array([[[0.0,0.0]]*time_piece]*place_piece)
time=[]
space=[]
speed1=[]
choose=[]
#while len(choose)<32:
#    choose.append(random.randint(0,len(pos[0])-1))
#    choose=list(set(choose))
for i in range(len(pos)):
    for j in range(len(pos[0])):
        if 1: #j in choose:
            if pos[i][j]!='' and pos[i][j]!=-1 and speed[i][j]!='':
                try:
                    counti=int(i/time_interval)
                    countj=int(float(pos[i][j])/place_interval)
                    table[counti][countj][0]+=(float(speed[i][j]))
                    table[counti][countj][1]+=1
                    #time.append(i)
                    #space.append(pos[i][j])
                    #speed1.append(speed[i][j])
                except:
                    pass
            
counti=0
countj=0
true_table=np.array([[0.0]*time_piece]*place_piece)
for i in table:
    for j in i:
        if j[1]==0:
            true_table[counti][countj]=15*3.6
        else:
            true_table[counti][countj]=j[0]/j[1]*3.6
        countj+=1
    counti+=1
    countj=0
v=pd.DataFrame(true_table)
v.to_csv(path+"place_time_table.csv",index=False)

#fig = plt.figure(figsize=(10,10))
plt.rc('font',family='Times New Roman')
#            
#norm = matplotlib.colors.Normalize(vmin=0, vmax=15)
cmap = plt.cm.get_cmap("jet_r")
#plt.scatter(time, space, marker = '.', s=0.01, c=speed1, cmap=man_cmap(cmap, 1.25), norm=norm)

#sns.set(font_scale=1)
hm = sns.heatmap(true_table,
                 cbar=True,
                 square=True,
                 vmin=0,             #刻度阈值
                 vmax=55,
                 cmap=man_cmap(cmap, 1.25),        #刻度颜色
                 xticklabels=20, yticklabels=20
                 )             #seaborn.heatmap相关属性
# 解决中文显示问题
#ax = plt.gca()
#x_space = MultipleLocator(25)
#ax.xaxis.set_major_locator(x_space)
#y_space = MultipleLocator(25)
#ax.yaxis.set_major_locator(y_space)
plt.ylabel('Space segment')
plt.xlabel('Time segment')
#label_y = plt.get_yticklabels()
#plt.setp(label_y , rotation = 360)
#label_x = plt.get_xticklabels()
#plt.setp(label_x , rotation = 360)
plt.title(t, fontsize=12)




