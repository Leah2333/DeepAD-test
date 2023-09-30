from os import name
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
from scipy import stats
plt.rc('font',family='Times New Roman')

def check(length,data):
    while len(data)<length:
        data.append(data[-1])
    return data

def check2(data):
    while data[-1]==-999:
        del data[-1]
    return data

def check3(length,data):
    while len(data)<length:
        data.append(0)
    return data

returns = pd.read_csv('micro_ppo_v9_newlanechange_newnet_999.0_1.0_5.0_50.0_64.txt', names=['r'])
r = returns['r']
smooth_r = r.rolling(window=100, min_periods=1).mean()

plt.figure(figsize=(10, 4), dpi=200)
plt.plot(r.index + 1, r, label='Episode return')
plt.plot(r.index + 1, smooth_r, '--', label='Smoothed episode return')
plt.ylabel('Return')
plt.xlabel('Episode')
plt.legend(loc='right')
plt.show()

plt.clf() 

#new plot
plt.figure(figsize=(10, 4), dpi=200)
plt.plot(r.index + 1, smooth_r, '--', color='darkblue', label='episode return')
mean=[]
std=[]
r2=np.array(r)
for i in range(len(r)-100):
    mean.append(np.mean(r2[i:i+99], 0))
    std.append(np.std(r2[i:i+99], 0))#计算平均值和标准差
check(20009,mean)
check(20009,std)
conf_intveral = stats.norm.interval(0.95, loc=mean, scale=std)#计算95%的上下区间
plt.fill_between(r.index + 1, conf_intveral[0], conf_intveral[1], color='deepskyblue', alpha=1)#填充区间
plt.ylabel('Return')
plt.xlabel('Episode')
plt.legend(loc='lower right')
plt.show()

av = pd.read_csv('av.csv')
hdv = pd.read_csv('hdv.csv')

# draw speed
plt.figure(figsize=(10, 6), dpi=200)
speed_av = np.array(av['speed']).tolist()
speed_hdv = np.array(hdv['speed']).tolist()
plt.figure(figsize=(10, 4), dpi=200)
plt.plot(hdv['speed'].index + 1, check(len(speed_hdv),speed_av), label='AV speed')
plt.plot(hdv['speed'].index + 1, speed_hdv, '--', label='HDV speed')
plt.ylabel('Speed')
plt.xlabel('Time slice')
plt.legend(loc='right')
plt.show()

# draw acc
plt.figure(figsize=(10, 6), dpi=200)
acc_av = np.array(av['acc']).tolist()
acc_hdv = np.array(hdv['acc']).tolist()
plt.figure(figsize=(10, 4), dpi=200)
plt.plot(hdv['acc'].index + 1, check(len(acc_hdv),acc_av), label='AV acceleration')
plt.plot(hdv['acc'].index + 1, acc_hdv, '--', label='HDV acceleration')
plt.ylabel('Acceleration')
plt.xlabel('Time slice')
plt.legend(loc='lower right')
plt.show()

# draw dis
plt.figure(figsize=(10, 6), dpi=200)
pos_av = np.array(av['pos']).tolist()
pos_hdv = np.array(hdv['pos']).tolist()
plt.figure(figsize=(10, 4), dpi=200)
plt.plot(hdv['pos'].index + 1, check(len(pos_hdv),pos_av), label='AV position')
plt.plot(hdv['pos'].index + 1, pos_hdv, '--', label='HDV position')
plt.ylabel('Position')
plt.xlabel('Time slice')
plt.legend(loc='right')
plt.show()

# a*v
plt.figure(figsize=(10, 6), dpi=200)
labels = ['AV', 'HDV']#, 'exp obj_fun', 'real obj_fun']
#labels = ['exp obj_fun', 'real obj_fun']
plt.ylabel('|a*v|')
plt.boxplot([check2(np.array(av['a*v']).tolist()),check2(np.array(hdv['a*v']).tolist())], labels=labels,showmeans=True)
#plt.savefig("C:\\Users\\Surface\\Desktop\\test2.svg", format="svg")
plt.show()

# a/v
plt.figure(figsize=(10, 6), dpi=200)
labels = ['AV', 'HDV']#, 'exp obj_fun', 'real obj_fun']
#labels = ['exp obj_fun', 'real obj_fun']
plt.ylabel('|a/v|')
plt.boxplot([check2(np.array(av['a/v']).tolist()),check2(np.array(hdv['a/v']).tolist())], labels=labels,showmeans=True)
#plt.savefig("C:\\Users\\Surface\\Desktop\\test2.svg", format="svg")
plt.show()

# speed_stability
plt.figure(figsize=(10, 6), dpi=200)
speed_stability_av = np.array(av['speed_stability']).tolist()
speed_stability_hdv = np.array(hdv['speed_stability']).tolist()
plt.figure(figsize=(10, 4), dpi=200)
plt.plot(np.array(range(len(check2(speed_stability_hdv)))) + 1, check3(len(check2(speed_stability_hdv)),check2(speed_stability_av)), label='AV')
plt.plot(np.array(range(len(check2(speed_stability_hdv)))) + 1, check2(speed_stability_hdv), '--', label='HDV')
plt.ylabel('Driving Jerkiness')
plt.xlabel('Time slice')
plt.legend(loc='right')
plt.show()


# acc_points
plt.figure(figsize=(10, 6), dpi=200)
acc_point_av = np.array(av['acc_point']).tolist()
acc_point_hdv = np.array(hdv['acc_point']).tolist()
plt.figure(figsize=(10, 4), dpi=200)
plt.plot(np.array(range(len(check2(acc_point_hdv)))) + 1, check(len(check2(acc_point_hdv)),check2(acc_point_av)), label='AV')
plt.plot(np.array(range(len(check2(acc_point_hdv)))) + 1, check2(acc_point_hdv), '--', label='HDV')
plt.ylabel('Acceleration Points')
plt.xlabel('Time slice')
plt.legend(loc='right')
plt.show()

# acc_avg_points
plt.figure(figsize=(10, 6), dpi=200)
acc_avg_point_av = np.array(av['acc_avg_point']).tolist()
acc_avg_point_hdv = np.array(hdv['acc_avg_point']).tolist()
plt.figure(figsize=(10, 4), dpi=200)
plt.plot(np.array(range(len(check2(acc_avg_point_hdv)))) + 1, check(len(check2(acc_avg_point_hdv)),check2(acc_avg_point_av)), label='AV')
plt.plot(np.array(range(len(check2(acc_avg_point_hdv)))) + 1, check2(acc_avg_point_hdv), '--', label='HDV')
plt.ylabel('Acceleration Average Points')
plt.xlabel('Time slice')
plt.legend(loc='right')
plt.show()