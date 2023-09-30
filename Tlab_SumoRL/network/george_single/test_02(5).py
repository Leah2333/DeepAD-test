import os
import sys

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

# import dijkstra

import optparse
import random
from sumolib import checkBinary
import sumolib
import traci
import traci.constants as tc


# 1. 物理最短路
# 2. 考虑路段最短通行时间的最短路
# 3. 考虑 Travel time 的最短路
# 4. 无权最短路
# 5-20. 随机路径


def get_plans(veh_id, start, dest, network):
    plans = []

    net = sumolib.net.readNet(network, withInternal=True)
    plan_sp = [
        i._id for i in net.getShortestPath(net.getEdge(start), net.getEdge(dest))[0]
    ]
    plans.append(plan_sp)

    plan_sp2 = traci.simulation.findRoute(
        start, dest, vType="", depart=-1.0, routingMode=0
    )
    plans.append(list(plan_sp2.edges))

    traci.vehicle.setRoutingMode(veh_id, tc.ROUTING_MODE_AGGREGATED)
    traci.vehicle.rerouteTraveltime(veh_id)
    plans.append(list(traci.vehicle.getRoute(veh_id)))
    for edge in net.getEdges(withInternal=True):
        traci.edge.setEffort(edge._id, 1)
    traci.vehicle.rerouteTraveltime(veh_id)
    plans.append(list(traci.vehicle.getRoute(veh_id)))
    # reset
    for edge in net.getEdges(withInternal=True):
        traci.edge.setEffort(edge._id, -1)

    for i in range(16):
        plans.append(random_plan(veh_id, start, dest, net))
    return plans


def random_plan(veh_id, start, dest, net):
    length = 7
    route_red = [net.getEdge(start)]
    route = [net.getEdge(start)]
    next_edge = None
    c = 0
    while len(route) < length:
        next_edge = random.choice(route_red[c].getToNode().getOutgoing())
        if next_edge._id.startswith(":") == False:
            route.append(next_edge)
        route_red.append(next_edge)
        c = c + 1
    st = route.pop()
    route = route + list(net.getShortestPath(st, net.getEdge(dest))[0])
    route = [i._id for i in drop_turn_around(route)]
    return route


def drop_turn_around(route):
    ed = None
    tmp = None
    route_new = []
    ix = -1
    for edge in route:
        route_new.append(edge)
        ix = ix + 1
        ed = edge.getToNode()
        if ed == tmp:
            del route_new[ix]
            del route_new[ix - 1]
            ix = ix - 2
            if ix == -1:
                tmp = None
                ed = None
                continue
        tmp = route_new[ix].getFromNode()
    return route_new

def add_new_vehicle(veh_id, start, dest, depart): 
    route_origin = []
    route_origin = get_plans(veh_id, "Oto0/2", "3.0toD", "net.net.xml")[1]
    traci.vehicle.addLegacy(veh_id, route_origin, depart)
    
def get_current_lane(vehicle_id):
    """
    获取车辆当前step所在的lane。
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    lane_id : str
    """
    current_lane = traci.vehicle.getLaneID(vehicle_id)
    return current_lane

def get_lateral_position(vehicle_id):
    """
    获取车辆当前step所在车道。
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    lateral_position: float
    {0, 1, 2, ...}
    """
    lane_ID = get_current_lane(vehicle_id)
    lateral_position = lane_ID[len(lane_ID)-1]
    return lateral_position
import re

def getDownStreamEdge(current_edge):

    net = sumolib.net.readNet("net.net.xml")
    Edge_test = net.getEdge(current_edge).getOutgoing()
    Edge_test_list=[]
    for key in Edge_test:
        Edge_test_list.append(str(key))   
    pre_answer=[]
    answer=[]
    for i in Edge_test_list:
        pattern = re.compile(".*id=(.*)from.*")
        pre_answer=pattern.findall(i)
        for j in pre_answer:
            answer.append(eval(j))
    return answer


# def read_all_edges(net):
#     '''
#     从sumolib中读取所有相关信息
#     '''
#     connection_dict = {'connetions':[],'fromNodeID':[],'toNodeID':[],'fromlane':[],'tolane':[]}
#     connections = net.get
#     for edge in connections:
#         edgeID = edge.getID()
#         fromNode = edge.getFromNode()
#         toNode = edge.getToNode()
#         fromNodeID = fromNode.getID()
#         toNodeID = toNode.getID()
#         fromlane = net.connection.get
#         edge_dict['edgeID'].append(edgeID)
#         edge_dict['fromNodeID'].append(fromNodeID)
#         edge_dict['toNodeID'].append(toNodeID)
#         edge_dict['length'].append(length)
#     edge_df = pd.DataFrame(edge_dict)
#     return edge_df

import pandas as pd
'''
net = sumolib.net.readNet("net.net.xml")
connection_dict = {'fromNodeID':[],'toNodeID':[],'fromlane':[],'tolane':[]}
edges = net.getEdges()
for i in edges:
    lanes = i.getLanes()
    for l in lanes:
        out = net.getLane(l.getID()).getOutgoing()
        if out:
            for i in out:
                connection_dict['fromNodeID'].append(i.getFrom().getID())
                connection_dict['toNodeID'].append(i.getTo().getID())
                connection_dict['fromlane'].append(i.getFromLane().getIndex())
                connection_dict['tolane'].append(i.getToLane().getIndex())
                # connection_dict = {'fromNodeID':[i.getFrom().getID()],'toNodeID':[i.getTo().getID()],'fromlane':[i.getFromLane().getIndex()],'tolane':[i.getToLane().getIndex()]}
connection_dataframe = pd.DataFrame(connection_dict).reset_index(drop = True)
print(connection_dataframe)
'''             

#print(getDownStreamEdge('1/1to2/1'))
'''
edges = net.getEdges()
for i in edges:
    lanes = i.getLanes()
    for l in lanes:
        out = net.getLane(l.getID()).getOutgoing()
        if out:
            for i in out:
                print(i, i.getDirection())
'''
def get_current_edge(vehicle_id):
    """
    获取车辆当前step所在的edge。
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    edge_id : str
    """
    current_edge = traci.vehicle.getRoadID(vehicle_id)
    return current_edge

def get_current_lane(vehicle_id):
    """
    获取车辆当前step所在的lane。
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    lane_id : str
    """
    current_lane = traci.vehicle.getLaneID(vehicle_id)
    return current_lane

def get_target_lane(vehicle_id):
    """
    获取车辆当前step的目标车道。
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    target_lane: str
    
    """
    net = sumolib.net.readNet("net.net.xml")
    connection_dict = {'fromNodeID':[],'toNodeID':[],'fromlane':[],'tolane':[]}
    edges = net.getEdges()
    for i in edges:
        lanes = i.getLanes()
        for l in lanes:
            out = net.getLane(l.getID()).getOutgoing()
            if out:
                for i in out:
                    connection_dict['fromNodeID'].append(i.getFrom().getID())
                    connection_dict['toNodeID'].append(i.getTo().getID())
                    connection_dict['fromlane'].append(i.getFromLane().getIndex())
                    connection_dict['tolane'].append(i.getToLane().getIndex())
    connection_dataframe = pd.DataFrame(connection_dict).reset_index(drop = True)
    route = traci.vehicle.getRoute(vehicle_id)
    route_temp = route[route.index(get_current_edge(vehicle_id)):route.index(get_current_edge(vehicle_id))+2]
    targetlane_ID =connection_dataframe.loc[(connection_dataframe['fromNodeID'] == route_temp[0]) & (connection_dataframe['toNodeID'] == route_temp[1])]['fromlane']
    targetlane = []
    targetlane_answer = []
    for i in targetlane_ID:
        targetlane.append(i)
    for j in targetlane:
        targetlane_answer.append(get_current_edge(vehicle_id) + '_' + str(j))
    return targetlane_answer
    

def get_longitudinal_speed(vehicle_id):
    """
    获取车辆当前step所在的纵向速度。
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    longitudinal_speed : float
    """
    longitudinal_speed = traci.vehicle.getSpeed(vehicle_id)
    return longitudinal_speed

def get_acceleration(vehicle_id):
    """
    获取车辆当前step所在的加速度。
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    Acceleration : float
    """
    acceleration = traci.vehicle.getAcceleration(vehicle_id)
    return acceleration

def get_leader_info(vehicle_id):
    """
    获取车辆当前step同一车道前方车辆的信息，包括ID，距离，速度，加速度。
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    leader_info: list
    'ID','distance','speed','accelaration'
    
    """
    leader_info = traci.vehicle.getLeader(vehicle_id)
    if leader_info is None:
        return []
    else:
        leader_info = list(leader_info)
        leader_info.append(get_longitudinal_speed(leader_info[0]))
        leader_info.append(get_acceleration(leader_info[0]))
        return leader_info

def get_follower_info(vehicle_id):
    """
    获取车辆当前step同一车道后方车辆的信息，包括ID，距离，速度，加速度。
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    follower_info: list
    'ID','distance','speed','accelaration'
    
    """
    follower_info = traci.vehicle.getFollower(vehicle_id)
    follower_list = []
    for i in follower_info:
        follower_list.append(i)
    if follower_list[0] == '':
        return []
    else:
        follower_list.append(get_longitudinal_speed(follower_list[0]))
        follower_list.append(get_acceleration(follower_list[0]))
        return follower_list

def get_left_follower_info(vehicle_id):
    """
    获取车辆当前step左边车道后方第一台车辆的信息，包括ID，距离，速度，加速度。
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    left_follower_info: list
    'ID','distance','speed','accelaration'
    
    """
    left_follower_info = traci.vehicle.getLeftFollowers(vehicle_id)
    left_follower_list = []
    for i in left_follower_info:
        for j in i:
            left_follower_list.append(j)
    if len(left_follower_list)== 0:
        return left_follower_list
    else:    
        if float(left_follower_list[1]) > 0:
            left_follower_list[1] = float(left_follower_list[1]) - 2.5
        if float(left_follower_list[1]) < 0:
            left_follower_list[1] = float(left_follower_list[1]) + 2.5
        else:
            pass
        left_follower_list.append(get_longitudinal_speed(left_follower_list[0]))
        left_follower_list.append(get_acceleration(left_follower_list[0]))
        return left_follower_list

def get_left_leader_info(vehicle_id):
    """
    获取车辆当前step左边车道前方第一台车辆的信息，包括ID，距离，速度，加速度。
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    right_left_info: list
    'ID','distance','speed','accelaration'
    
    """
    left_leader_info = traci.vehicle.getLeftLeaders(vehicle_id)
    left_leader_list = []
    for i in left_leader_info:
        for j in i:
            left_leader_list.append(j)
    if len(left_leader_list)== 0:
        return left_leader_list
    else:    
        if float(left_leader_list[1]) > 0:
            left_leader_list[1] = float(left_leader_list[1]) - 2.5
        if float(left_leader_list[1]) < 0:
            left_leader_list[1] = float(left_leader_list[1]) + 2.5
        else:
            pass
        left_leader_list.append(get_longitudinal_speed(left_leader_list[0]))
        left_leader_list.append(get_acceleration(left_leader_list[0]))
        return left_leader_list

def get_right_follower_info(vehicle_id):
    """
    获取车辆当前step右边车道后方第一台车辆的信息，包括ID，距离，速度，加速度。
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    right_follower_info: list
    'ID','distance','speed','accelaration'
    
    """
    right_follower_info = traci.vehicle.getRightFollowers(vehicle_id)
    right_follower_list = []
    for i in right_follower_info:
        for j in i:
            right_follower_list.append(j)
    if len(right_follower_list)== 0:
        return right_follower_list
    else:    
        if float(right_follower_list[1]) > 0:
            right_follower_list[1] = float(right_follower_list[1]) - 2.5
        if float(right_follower_list[1]) < 0:
            right_follower_list[1] = float(right_follower_list[1]) + 2.5
        else:
            pass
        right_follower_list.append(get_longitudinal_speed(right_follower_list[0]))
        right_follower_list.append(get_acceleration(right_follower_list[0]))
        return right_follower_list

def get_right_leader_info(vehicle_id):
    """
    获取车辆当前step右边车道前方第一台车辆的信息，包括ID，距离，速度，加速度。
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    right_leader_info: list
    'ID','distance','speed','accelaration'
    
    """
    right_leader_info = traci.vehicle.getRightLeaders(vehicle_id)
    right_leader_list = []
    for i in right_leader_info:
        for j in i:
            right_leader_list.append(j)
    if len(right_leader_list)== 0:
        return right_leader_list
    else:    
        if float(right_leader_list[1]) > 0:
            right_leader_list[1] = float(right_leader_list[1]) - 2.5
        if float(right_leader_list[1]) < 0:
            right_leader_list[1] = float(right_leader_list[1]) + 2.5
        else:
            pass
        right_leader_list.append(get_longitudinal_speed(right_leader_list[0]))
        right_leader_list.append(get_acceleration(right_leader_list[0]))
        return right_leader_list

def if_collision(vehicle_id):
    if abs(get_profile(get_right_leader_info(vehicle_id)[0])[1] - get_profile(vehicle_id)[0] )<= 0.1 and abs(get_profile(get_right_leader_info(vehicle_id)[0])[2] - get_profile(vehicle_id)[3]) <=0.1 :
        return 'collision with rightleadercar'
    elif get_left_leader_info(vehicle_id)[1] <= 0.5:
        return 'collision with leftleadercar'
    elif get_leader_info(vehicle_id)[1] <= 0.5:
        return 'collision with leadercar'
    elif get_left_follower_info(vehicle_id)[1] <= 0.5:
        return 'collision with leftfollowercar'
    elif get_right_follower_info(vehicle_id)[1] <= 0.5:
        return 'collision with rightfollowercar'
    elif get_follower_info(vehicle_id)[1] <= 0.5:
        return 'collision with followercar'
    else:    
        return 'safe' 

def get_profile(vehicle_id):
    center = traci.vehicle.getPosition(vehicle_id)
    front = center[0] + traci.vehicle.getLength(vehicle_id)/2
    back = center[0] - traci.vehicle.getLength(vehicle_id)/2
    above = center[1] + traci.vehicle.getWidth(vehicle_id)/2
    below = center[1] - traci.vehicle.getWidth(vehicle_id)/2
    shapelist = []
    shapelist.extend([front,back,above,below])
    return shapelist

def run():
    step = 0
    for step in range(3600):
        print("Now,step=",step)
        # print(int(connection_dataframe.loc[(connection_dataframe['fromNodeID'] == '0/0to0/1') & (connection_dataframe['toNodeID'] == '0/1to1/1')]['fromlane']))
        if step == 145:
            print(get_target_lane('test'))


        
        if step >=148:
            traci.vehicle.changeLane('test', laneIndex=1, duration=0)
            traci.vehicle.rerouteEffort('test')
            
            print("*************************************************",traci.vehicle.getPosition('test'))
            print("*************************************************",get_profile('test'))
            print('*******************Leader**********************',get_leader_info('test'))
            print('*******************follower**********************', get_follower_info('test'))
            print('*******************leftfollower**********************',get_left_follower_info('test'))
            print('*******************leftLeader**********************',get_left_leader_info('test'))          
            print('*******************rightLeader**********************',get_right_leader_info('test'))
            print('*******************rightfollower**********************',get_right_follower_info('test'))
            print(if_collision('test'))
            # print(get_lateral_position('test'))
            # if step >=50:
                # traci.vehicle.changeLane('test', laneIndex=1, duration=10)
            # traci.vehicle.rerouteEffort('test')
            # traci.vehicle.changeSublane('test', 10)
            # print(traci.lane.getLength(traci.vehicle.getLaneID('test'))-traci.vehicle.getLanePosition('test'))
            # print(traci.vehicle.getLateralAlignment('test'))
            # print(traci.vehicle.getPosition('test'))

        traci.simulationStep()
        
        #print(getDownStreamEdge('1/1to2/1'))
        #print(net.getDownstreamEdges(edge='0/1to1/1',distance=200,stopOnTLS='1/1'))
        #print(net.Net.getTLSID())
        #if step % 2 == 0:
            #for i in get_plans(vehID, "Oto0/2", "3.0toD", "net.net.xml"):
                #print(i)
                #add_new_vehicle(veh_id='test', start="Oto0/2", dest="3.0toD" , depart=1)
            #break
        
    traci.close()


if __name__ == "__main__":
    sumoBinary = checkBinary("sumo-gui")
   
    traci.start([sumoBinary, "-c", "test.sumocfg"],label='default',port=8813)
    # traci.setOrder(order=3)
    # print(traci.getLabel())
    
    
    # traci.start([sumoBinary, "-c", "C:/Users/12611/Desktop/RL_pathrecommandation/RL_test1015/Tlab_SumoRL/network/test_14/test.sumocfg"], label="sim1")
    # traci.start([sumoBinary, "-c", "C:/Users/12611/Desktop/RL_pathrecommandation/RL_test1015/Tlab_SumoRL/network/test_14/test.sumocfg"], label="sim2")
    # traci.switch("sim1")
    # run()
    # traci.switch("sim2")
    # run()
    

    run()
