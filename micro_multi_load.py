from Tlab_SumoRL.kernel.environment.micro_multi_env import MicroEnv
import os
import sys
import pandas as pd
from lxml import etree
import random

def remove_items(lst, n):
    indices = set(random.sample(range(len(lst)), n))
    lst[:] = [x for i, x in enumerate(lst) if i not in indices]
    return lst

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

import traci
from Tlab_SumoRL.kernel.sumo.interaction import check_sumo_binary, sumo_step
from Tlab_SumoRL.kernel.sumo.network import get_next_edge, is_junction_edge
from Tlab_SumoRL.utils.config import CFG

import tensorflow as tf
from tensorforce.agents import Agent
import numpy as np

tf.config.set_visible_devices(tf.config.get_visible_devices('CPU'))
tf.random.set_seed(1)
np.random.seed(1)

today_route=[]
# read basic information
today_route.append(["47@365#0","365@511#0","511@464#0","464@39#0","39@320#0","320@448#0","448@314#0","314@497#0","497@336#0","336@498#0","498@313#0","313@309#0","309@48#0"]) # 三条路径

path='D:/temp/k/RL_AV/micro_RL/output/80'
percent=0.8
HDV=0

veh_name=[]
my_vehicle=etree.parse("D:/temp/k/RL_AV/micro_RL/Tlab_SumoRL/network/qls/qls_RL.rou.xml")
trips = my_vehicle.xpath("//trip")
for trip in trips:
    ID = trip.get("id")
    f = trip.get("from")
    t = trip.get("to")
    d = trip.get("depart")
    if f==today_route[0][0] and t==today_route[0][-1]:
        veh_name.append([ID,d])
        
terminal = 0
dailyroute_states = None
micro_states = None
if percent<1:
    veh_name=remove_items(veh_name, int((1-percent)*len(veh_name)))

volume=len(veh_name)
micro_env = MicroEnv(volume)



# micro_env.reset()
    
#traci.route.add(routeID=f"test_route_0", edges=today_route[0])
#traci.route.add(routeID=f"test_route_1", edges=today_route[1])
#traci.route.add(routeID=f"test_route_2", edges=today_route[2])


# add vehicle to network
print(veh_name)
for i in veh_name:
    micro_env.soft_reset(today_route[0][0], today_route[0][-1] , i[0], int(i[1]))

#while not micro_env.vehicle.in_network:
#    sumo_step()
#while micro_env.vehicle.current_edge != micro_env.vehicle.origin:
#    sumo_step()

acc_list = []*volume
lanechange_count = [0]*volume
speed_list=[]
accelation_list=[]
lane_list=[]
dist_list=[]

micro_agent = [Agent.load(
    filename='micro_v9_newlanechange_newnet-20000', 
    directory='checkpoints', format='numpy'
)] *volume

# 各路段微观行为
    
traci.start([
    check_sumo_binary(CFG.env.use_gui), '-c', CFG.path.sumocfg, 
    '--lateral-resolution', '0.8'
])
    
#for i in range(500):
#    print('********step***********',sumo_step())
#    #if traci.vehicle.vehicle_in_network("outright_11")==1:
#        #print(traci.vehicle.get_current_edge("outright_11"))
#        #print(traci.vehicle.getSpeed("outright_11"))
#    #else:
#        #print("nocar!")
#    micro_env.vehicle[0].in_network
#for i in micro_env.vehicle:
#    print(i.vehicle_id)
now=0
act=0

for i in micro_env.vehicle:
    print(i.vehicle_id)
while now < 4500:
    
    now=sumo_step()
    print('=======================')
    print('********step***********',now,' ',act)
    act=0
    now_acc=[]
    now_speed=[]
    now_lane=[]
    now_dist=[]
    micro_statess = micro_env.state
    
    for i in range(volume):
#        if i<10:
#            print("-->",i)
        micro_states = micro_statess[i]
        if sum(micro_states)==0 or HDV:   
            try: micro_env.vehicle[i].current_edge
            except: 
                now_speed.append(0)
                now_acc.append(0)
                now_lane.append("nocar!")
                now_dist.append(-1)
            else:
                if traci.vehicle.getSpeed(micro_env.vehicle[i].vehicle_id)<-100:
                    now_speed.append(0)
                    now_acc.append(0)
                    now_dist.append(-1)
                else:
                    now_speed.append(traci.vehicle.getSpeed(micro_env.vehicle[i].vehicle_id))
                    now_acc.append(traci.vehicle.getAcceleration(micro_env.vehicle[i].vehicle_id))
                    now_dist.append(traci.vehicle.getDistance(micro_env.vehicle[i].vehicle_id))
                now_lane.append(micro_env.vehicle[i].current_edge)
#            if i<10:
#                print(micro_env.vehicle[i].current_edge)
#                print(micro_env.vehicle[i].origin)
#                print("out of edge")
            continue
        current_edge = micro_env.vehicle[i].current_edge
        
        
        
        
        if is_junction_edge(current_edge):
            # 跳过不换道部分（离交叉口过远或在交叉口内）
            micro_env.vehicle[i].change_lane("stay")
            
        elif current_edge not in today_route[0]:
            pass
        else:
            next_edge = get_next_edge(current_edge, today_route[0])
            micro_env.vehicle[i].set_origin(current_edge)
            micro_env.vehicle[i].set_destination(next_edge)
            micro_env.vehicle[i].set_plans([current_edge, next_edge]) 
            micro_action = micro_agent[i].act(
                states=micro_states, independent=True, deterministic=True
            )
            acc, lc_left, lc_stay, lc_right = micro_env.inverse_transform_action(micro_action)
            lanechange_action = np.argmax([lc_left, lc_stay, lc_right])
            act+=1
            # record actions
            # acc_list.append(acc)
            if lanechange_action != 1:
                lanechange_count[i] += 1
            
            # state, reward, terminal, info = micro_env.step(micro_action)
            # 执行换道
            micro_env.vehicle[i].accelerate(acc)
            if (micro_env.vehicle[i].pos_lat == 0 and lanechange_action == 2) or \
                   (micro_env.vehicle[i].pos_lat == micro_env.vehicle[i].current_edge_lanes - 1 and \
                       lanechange_action == 0):
                       lanechange_action = 1
            if lanechange_action == 0:    # left
                micro_env.vehicle[i].change_lane("left")
            elif lanechange_action == 2:  # right
                micro_env.vehicle[i].change_lane("right")
            else:                         # stay
                micro_env.vehicle[i].change_lane("stay")
        
        now_lane.append(current_edge)
        now_dist.append(traci.vehicle.getDistance(micro_env.vehicle[i].vehicle_id))
        now_speed.append(traci.vehicle.getSpeed(micro_env.vehicle[i].vehicle_id))
        now_acc.append(traci.vehicle.getAcceleration(micro_env.vehicle[i].vehicle_id))

    speed_list.append(now_speed)
    accelation_list.append(now_acc)
    lane_list.append(now_lane)
    dist_list.append(now_dist)
    #print('**********speed*********',now_speed)
    #print('**********acc*********',now_acc) 
    #print('**********edge*********',now_lane) 
    #print(micro_env.infram)
    print('=======================')
     


    #sumo_step()
    
    # print(acc_list)
    # print(micro_env.vehicle.target_lane)
    # print(micro_env.vehicle.target_lane_number)
    # print(lanechange_action)


if HDV==1:
    a=pd.DataFrame(speed_list)
    a.to_csv(path+"/speed_list_HDV.csv",index=False)
    b=pd.DataFrame(accelation_list)
    b.to_csv(path+"/accelation_list_HDV.csv",index=False)
    v=pd.DataFrame(lane_list)
    v.to_csv(path+"/lane_list_HDV.csv",index=False)
    m=pd.DataFrame(dist_list)
    m.to_csv(path+"/dist_list_HDV.csv",index=False)
else:
    a=pd.DataFrame(speed_list)
    a.to_csv(path+"/speed_list.csv",index=False)
    b=pd.DataFrame(accelation_list)
    b.to_csv(path+"/accelation_list.csv",index=False)
    v=pd.DataFrame(lane_list)
    v.to_csv(path+"/lane_list.csv",index=False)
    m=pd.DataFrame(dist_list)
    m.to_csv(path+"/dist_list.csv",index=False)