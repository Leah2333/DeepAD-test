from Tlab_SumoRL.kernel.environment.micro_env import MicroEnv
import os
import sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

import traci
from Tlab_SumoRL.kernel.sumo.interaction import check_sumo_binary, sumo_step
from Tlab_SumoRL.kernel.sumo.network import get_next_edge, is_junction_edge
from Tlab_SumoRL.utils.config import CFG
import seaborn as sns
import tensorflow as tf
from tensorforce.agents import Agent
import numpy as np
import pandas as pd

def check(length,data):
    while len(data)<length:
        try:
            data.append(-999)
        except:
            data.append('-999')
    return data

tf.config.set_visible_devices(tf.config.get_visible_devices('CPU'))
tf.random.set_seed(1)
np.random.seed(1)

micro_agent = Agent.load(
    filename='micro_v9_newlanechange_newnet-20000', 
    directory='checkpoints', format='numpy'
)

terminal = 0
dailyroute_states = None
micro_states = None

micro_env = MicroEnv()

# read basic information
today_route = ['0/1to1/1', '1/1to1/4' ,'1/4to1/2'] # TODO:  change route!!!!
# today_route = ['3/0to0/1','0/1to1/1','1/1to1/4','1/4to1/2']
# today_route = ['Oto0/2','0/2to1/2','1/2to1/1','1/1to2/1','2/1to3/1','3/1to3/0','3.0toD']
# today_route = ["47@365#0","365@511#0","511@464#0","464@39#0","39@320#0","320@448#0","448@314#0","314@497#0","497@336#0","336@498#0","498@313#0","313@309#0","309@48#0"]
today_entrance_time = CFG.vehicle.entrance_time
today_origin = today_route[0]
today_destination = today_route[-1]

micro_env.soft_reset(origin=today_route[0], destination=today_route[2])
# micro_env.reset()
print(check_sumo_binary(CFG.env.use_gui))
traci.start([
    check_sumo_binary(CFG.env.use_gui), '-c', CFG.path.sumocfg, 
    '--lateral-resolution', '0.8'
])

# add vehicle to network
traci.route.add(routeID=f"test_route", edges=today_route)
# print(traci.vehicle.getRoute(CFG.vehicle.vehicle_id))
traci.vehicle.add(CFG.vehicle.vehicle_id, f"test_route", depart=today_entrance_time)
traci.vehicle.setColor(CFG.vehicle.vehicle_id, (255, 0, 0))
print('vehicle added!!!')

while not micro_env.vehicle.in_network:
    sumo_step()
    total_vehicle_list = traci.simulation.getLoadedIDList()

while micro_env.vehicle.current_edge != micro_env.vehicle.origin:
    sumo_step()


lane_list = []
pos_list = []
lanechange_count = 0
speed_list=[]
accelation_list=[]
#
#for i in range(500):
#    print('********step***********',sumo_step())
#    #if traci.vehicle.vehicle_in_network("outright_11")==1:
#        #print(traci.vehicle.get_current_edge("outright_11"))
#        #print(traci.vehicle.getSpeed("outright_11"))
#    #else:
#        #print("nocar!")
#    total_vehicle_list = traci.simulation.getLoadedIDList()
#    print(total_vehicle_list)

# 各路段微观行为

AV=0
if AV==1:
    write='av.csv'
else:
    write='hdv.csv'
count=0
while len(pos_list) == 0 or pos_list[-1]<1200: #原来是1200
    if micro_env.vehicle.current_edge == today_destination:
        count+=1
    current_edge = micro_env.vehicle.current_edge
    #print(current_edge)
    if is_junction_edge(current_edge):
        # 跳过不换道部分（离交叉口过远或在交叉口内）
        micro_env.vehicle.change_lane("stay")
        sumo_step()
        continue
    #next_edge = get_next_edge(current_edge, today_route)
    #micro_env.vehicle.set_origin(current_edge)
    #micro_env.vehicle.set_destination(next_edge)
    #micro_env.vehicle.set_plans([current_edge, next_edge])
    if AV:
        micro_states = micro_env.state
        micro_action = micro_agent.act(
            states=micro_states, independent=True, deterministic=True
        )
        acc, lc_left, lc_stay, lc_right = micro_env.inverse_transform_action(micro_action)
        lanechange_action = np.argmax([lc_left, lc_stay, lc_right])
        
        # record actions
        if lanechange_action != 1:
            lanechange_count += 1
        
        # state, reward, terminal, info = micro_env.step(micro_action)
        # 执行换道
        micro_env.vehicle.accelerate(acc)
        if (micro_env.vehicle.pos_lat == 0 and lanechange_action == 2) or \
               (micro_env.vehicle.pos_lat == micro_env.vehicle.current_edge_lanes - 1 and \
                   lanechange_action == 0):
                   lanechange_action = 1
        if lanechange_action == 0:    # left
            micro_env.vehicle.change_lane("left")
        elif lanechange_action == 2:  # right
            micro_env.vehicle.change_lane("right")
        else:                         # stay
            micro_env.vehicle.change_lane("stay")
    

    speed_list.append(traci.vehicle.getSpeed('test'))
    accelation_list.append(traci.vehicle.getAcceleration('test'))
    lane_list.append(current_edge)
    pos_list.append(traci.vehicle.getDistance('test'))

    print('=======================')
    print('********step***********',sumo_step())
    print('**********speed*********',speed_list)
    print('**********acc*********',accelation_list) 
    print('**********lane*********',lane_list) 
    print('**********pos*********',pos_list) 
    print('=======================')

    #sumo_step()
    
    # print(acc_list)
    # print(micro_env.vehicle.target_lane)
    # print(micro_env.vehicle.target_lane_number)
    # print(lanechange_action)
    
print("time:",sumo_step()-CFG.vehicle.entrance_time)

jia=[]
jian=[]
sp=[30,40,60,80,100,120]
jian.append([-2,-3.5,-4.5])
jian.append([-1.7,-3.1,-3.9])
jian.append([-1.6,-2.8,-3.7])
jian.append([-1.4,-2.6,-3.4])
jian.append([-1.2,-2.2,-2.8])
jian.append([-0.9,-1.7,-2.3])
jianavg=[-3,-2.6,-2.4,-2.2,-1.8,-1.4]
jiaavg=[3.5,3.1,2.9,2.7,2.3,1.9]
jia.append([2.5,4,5])
jia.append([2.2,3.6,4.4])
jia.append([2.1,3.3,4.2])
jia.append([1.9,3.1,3.9])
jia.append([1.7,2.7,3.3])
jia.append([1.4,2.2,2.8])

print("accelation_list:%.1f"%np.mean(np.array(accelation_list)))
print("speed_list:%.1f"%np.mean(np.array(speed_list)))
avg_point=[]
point=[]
vmula=[]
adivv=[]
minus=[]
smooth_minus=[]
for i in range(min(len(speed_list),len(accelation_list))):
    vmula.append(abs(3.6*speed_list[i]*accelation_list[i]))
    if speed_list[i]==0:
        adivv.append(0)
    else:
        adivv.append(abs(accelation_list[i]/(3.6*speed_list[i])))
    now=5
    for j in range(len(sp)):
        if speed_list[i]*3.6<sp[j]:
            now=j
            break
    p=0
    if accelation_list[i]>0:
        p=4
        for k in range(len(jia[j])):
            
            if accelation_list[i]<jia[j][k]:
                p=k
                break
    elif accelation_list[i]<0:
        p=-4
        for k in range(len(jian[j])):
            if accelation_list[i]>jian[j][k]:
                p=-k
                break     
    point.append(p)    
    if i>1:
        avg=(accelation_list[i]+accelation_list[i-1]+accelation_list[i-2])/3
        if avg>0:
            
            if avg>jiaavg[j]:
                avg_point.append(1)
            else:
                avg_point.append(0)
        else:
            if avg<jianavg[j]:
                avg_point.append(-1)
            else:
                avg_point.append(0)            
    
    if i>0:
        minus.append(abs(speed_list[i]-speed_list[i-1]))
    if i>9:
        smooth_minus.append(np.mean(minus[-10:]))

max_length=max(len(speed_list),len(accelation_list),len(lane_list),len(pos_list),len(smooth_minus),len(point),len(avg_point),len(vmula))

save={'speed':check(max_length,speed_list),'acc':check(max_length,accelation_list),'lane':check(max_length,lane_list),'pos':check(max_length,pos_list),'speed_stability':check(max_length,smooth_minus),'acc_point':check(max_length,point),'acc_avg_point':check(max_length,avg_point),'a*v':check(max_length,vmula),'a/v':check(max_length,adivv)}
data=pd.DataFrame(save)
data.to_csv(write)