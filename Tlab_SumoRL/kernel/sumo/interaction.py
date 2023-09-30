from logging import Logger
from Tlab_SumoRL.utils.config import CFG
import pandas as pd
import traci
from traci.exceptions import TraCIException
import sumolib
import os
import sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")
    
    
def check_sumo_binary(use_gui=True):
    """
    Get SUMO binary executable.
    
    Paramters
    ---------
    use_gui : boolean
        Whether to launch GUI of SUMO.
    
    Returns
    -------
    sumo_binary : str
        Path to SUMO binary executable.
    """
    if use_gui:
        return sumolib.checkBinary('sumo-gui')
    else:
        return sumolib.checkBinary('sumo')


def sumo_step():
    """
    SUMO运行一仿真步。
    Returns
    -------
    sim_clock : float
        Current simulation second.
    """
    traci.simulationStep()
    return get_episode_timestep()


def get_episode_timestep():
    """
    Return current simulation second on SUMO
    """
    return traci.simulation.getTime()


#########################################################
################# vehicle information ###################
#########################################################

def get_current_edge(vehicle_id):
    """
    获取车辆当前step所在的edgeID。
    
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    edge_id : str
    """
    current_edge = traci.vehicle.getRoadID(vehicle_id)
    # try:
    # except TraCIException as e:
    #     error_msg = str(e)
    #     if 'not known' in error_msg:
    #         current_edge = ''
    #     else:
    #         raise e
    return current_edge


def get_current_lane(vehicle_id):
    """
    获取车辆当前step所在的laneID。

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


def get_total_lane_num(vehicle_id):
    """
    获取车辆当前step所在edge的lane总数。

    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    total_lane_num : str
    """
    total_lane_num = traci.edge.getLaneNumber(get_current_edge(vehicle_id))
    return total_lane_num

def get_lateral_speed(vehicle_id):
    """
    获取车辆当前step所在的横向速度。

    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    lateral_speed : float
    """
    lateral_speed = traci.vehicle.getLateralSpeed(vehicle_id)
    return lateral_speed


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


def get_longitudinal_acceleration(vehicle_id):
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


def get_lateral_acceleration(vehicle_id):
    """
    TODO: implement this
    """
    return 0


def get_min_dist_nbr(vehicle_id):
    return 0


def is_collision(vehicle_id):
    """
    判断主车是否与周围车辆发生碰撞
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    collision_list: list
    [0,0,0,1,0,0]
    0：无碰撞
    1：碰撞
    [右前,左前,前,左后,右后,后]
    """
    collision_list=[]
    if len(get_right_leader_info(vehicle_id)) != 0:
        "**********whether collision with rightleadercar*******"
        if abs(get_shape_position(get_right_leader_info(vehicle_id)[0])[1] - get_shape_position(vehicle_id)[0] )<= 0.2 and abs(get_shape_position(get_right_leader_info(vehicle_id)[0])[2] - get_shape_position(vehicle_id)[3]) <= 0.5 :
            collision_list.append(1)
        else :
            collision_list.append(0) 
    else:
        collision_list.append(0) 
    if len(get_left_leader_info(vehicle_id)) != 0:
        "**********whether collision with leftleadercar*******"
        if abs(get_shape_position(get_left_leader_info(vehicle_id)[0])[1] - get_shape_position(vehicle_id)[0] )<= 0.2 and abs(get_shape_position(get_left_leader_info(vehicle_id)[0])[3] - get_shape_position(vehicle_id)[2]) <=0.5 :
            collision_list.append(1)
        else :
            collision_list.append(0) 
    else:
        collision_list.append(0)    
    if len(get_leader_info(vehicle_id)) != 0:
        "**********whether collision with leadercar*******"
        if abs(get_shape_position(get_leader_info(vehicle_id)[0])[1] - get_shape_position(vehicle_id)[0] )<= 0.5:
            collision_list.append(1)
        else :
            collision_list.append(0) 
    else:
        collision_list.append(0)  
    if len(get_left_follower_info(vehicle_id)) != 0:
        "**********whether collision with leftfollowercar*******"
        if abs(get_shape_position(get_left_follower_info(vehicle_id)[0])[0] - get_shape_position(vehicle_id)[1] )<= 0.2 and abs(get_shape_position(get_left_follower_info(vehicle_id)[0])[3] - get_shape_position(vehicle_id)[2]) <=0.2 :
            collision_list.append(1)
        else :
            collision_list.append(0) 
    else:
        collision_list.append(0)      
    if len(get_right_follower_info(vehicle_id)) != 0:
        "**********whether collision with rightfollowercar*******"
        if abs(get_shape_position(get_right_follower_info(vehicle_id)[0])[0] - get_shape_position(vehicle_id)[1] )<= 0.2 and abs(get_shape_position(get_right_follower_info(vehicle_id)[0])[2] - get_shape_position(vehicle_id)[3]) <=0.2 :
            collision_list.append(1)
        else :
            collision_list.append(0) 
    else:
        collision_list.append(0)      
    if len(get_follower_info(vehicle_id)) != 0:
        "**********whether collision with followercar*******"
        if abs(get_shape_position(get_follower_info(vehicle_id)[0])[0] - get_shape_position(vehicle_id)[1] )<= 0.5:
            collision_list.append(1)
        else :
            collision_list.append(0) 
    else:
        collision_list.append(0) 
    return collision_list


def get_shape_position(vehicle_id):
    """
    获取当前车辆的边缘坐标信息：车头x坐标值、车尾x坐标值、车左y坐标值、车y坐标值
    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    shape_list: list
    [50,45,110,105]
    [车头,车尾,左,右]
    """
    center = traci.vehicle.getPosition(vehicle_id)
    front = center[0] + traci.vehicle.getLength(vehicle_id)/2
    back = center[0] - traci.vehicle.getLength(vehicle_id)/2
    above = center[1] + traci.vehicle.getWidth(vehicle_id)/2
    below = center[1] - traci.vehicle.getWidth(vehicle_id)/2
    shape_list = []
    shape_list.extend([front,back,above,below])
    return shape_list


def vehicle_in_network(vehicle_id):
    """
    判断车辆是否在路网中
        
    Paramters
    ---------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    in_network : boolean
    """
    total_vehicle_list = []
    total_vehicle_list = traci.simulation.getLoadedIDList()
    if vehicle_id in total_vehicle_list:
        return True
    else:
        return False

def get_expected_speed(vehicle_id):
    """
    获取车辆的期望速度

    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    Expected_speed : float
    """
    expected_speed = traci.vehicle.getAllowedSpeed(vehicle_id)
    return expected_speed


def get_longitudinal_position(vehicle_id):
    """
    获取车辆当前step距离下一个交叉口的距离。

    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    longitudinal_position: float
    """
    lane_length = traci.lane.getLength(get_current_lane(vehicle_id))
    position_length = traci.vehicle.getLanePosition(vehicle_id)
    longitudinal_position = lane_length - position_length
    return longitudinal_position


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


def get_target_lane(vehicle_id):
    """
    获取车辆当前step的目标车道。

    Parameters
    ----------
    vehicle_id : str
        ID of a vehicle.
    
    Returns
    -------
    target_lane : array or list of str
    
    """
    net = sumolib.net.readNet(CFG.path.network)
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
    connection_dataframe = pd.DataFrame(connection_dict).reset_index(drop=True)
    route = traci.vehicle.getRoute(vehicle_id)
    current_edge = get_current_edge(vehicle_id)
    if current_edge in route:
        route_temp = route[route.index(current_edge):route.index(current_edge)+2]
        # print(f"route_temp: {route} - {current_edge} - {route_temp}")
        targetlane_ID = connection_dataframe.loc[
            (connection_dataframe['fromNodeID'] == route_temp[0]) & 
            (connection_dataframe['toNodeID'] == route_temp[1]), 'fromlane']
        targetlane = []
        targetlane_answer = []
        for i in targetlane_ID:
            targetlane.append(i)
        for j in targetlane:
            targetlane_answer.append(current_edge + '_' + str(j))
        return targetlane_answer
    else:
        return []


#########################################################
################## vehicle neighbours ###################
"""
- leader
- follower
- left leader
- left follower
- right leader
- right follower
----------------
ID, distance, speed, acceleration
"""
#########################################################

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
        'ID','distance','speed','acceleration'
    
    """
    leader_info = traci.vehicle.getLeader(vehicle_id)
    if leader_info is None:
        return []
    else:
        leader_info = list(leader_info)
        leader_info.append(get_longitudinal_speed(leader_info[0]))
        leader_info.append(get_longitudinal_acceleration(leader_info[0]))
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
    'ID','distance','speed','acceleration'
    
    """
    # return get_leader_info(vehicle_id) # TODO: remove this line
    follower_info = traci.vehicle.getFollower(vehicle_id)
    follower_list = []
    for i in follower_info:
        follower_list.append(i)
    if follower_list[0] == '':
        return []
    else:
        follower_list.append(get_longitudinal_speed(follower_list[0]))
        follower_list.append(get_longitudinal_acceleration(follower_list[0]))
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
    'ID','distance','speed','acceleration'
    
    """
    left_follower_info = traci.vehicle.getLeftFollowers(vehicle_id)
    left_follower_list = []
    if len(left_follower_info) > 0:
        for i in left_follower_info[0]:
            left_follower_list.append(i)
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
        left_follower_list.append(get_longitudinal_acceleration(left_follower_list[0]))
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
    'ID','distance','speed','acceleration'
    
    """
    left_leader_info = traci.vehicle.getLeftLeaders(vehicle_id)
    left_leader_list = []
    if len(left_leader_info) > 0:
        for i in left_leader_info[0]:
            left_leader_list.append(i)
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
        left_leader_list.append(get_longitudinal_acceleration(left_leader_list[0]))
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
    if len(right_follower_info) > 0:
        for i in right_follower_info[0]:
            right_follower_list.append(i)
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
        right_follower_list.append(get_longitudinal_acceleration(right_follower_list[0]))
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
    'ID','distance','speed','acceleration'
    
    """
    right_leader_info = traci.vehicle.getRightLeaders(vehicle_id)
    right_leader_list = []
    if len(right_leader_info) > 0:
        for i in right_leader_info[0]:
            right_leader_list.append(i)
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
        right_leader_list.append(get_longitudinal_acceleration(right_leader_list[0]))
        return right_leader_list


########################################################
def get_remain_time(plan, current_edge):
    """
    Get total remaining travel time of all plans.
    
    Parameters
    ----------
    plan : list
        A list of route plans.
    current_edge : str
        ID of current edge.
        
    Returns
    -------
    travel_time : float
    """
    travel_time = 0
    if current_edge in plan:
        index = plan.index(current_edge)
        plan_re = plan[index:]
    else:
        plan_re = plan
    travel_timelist = []
    for i in plan_re:
        travel_timelist.append(traci.edge.getTraveltime(i))
    for j in travel_timelist:
        travel_time = travel_time + j
    return travel_time


def get_occupancy(edgeid):
    """
    Get space occupancy of an edge.
    
    Parameters
    ----------
    edgeid : str
        ID of an edge.
        
    Returns
    -------
    occupancy : float
    """
    return traci.edge.getLastStepOccupancy(edgeid)


def get_remain_occupancy(plan, current_edge):
    """
    主车选择某个plan当前时刻剩余路段的车辆占用比之和。
    
    Parameters
    ----------
    plan : list
        A list of route plans.
    current_edge : str
        ID of current edge.
        
    Returns
    -------
    occupancy : float
    """
    occupancy = 0
    if current_edge in plan:
        index = plan.index(current_edge)
        plan_re = plan[index:]
    else:
        plan_re = plan
    occupancylist = []
    for i in plan_re:
        occupancylist.append(get_occupancy(i))
    for j in occupancylist:
        occupancy = occupancy + j
    return occupancy / (len(occupancylist))


##########################


def get_path_length(path):
    """
    Return the total length of the path.
    
    Parameters
    ----------
    path : array or list
    
    Returns
    -------
    path_length : int
    
    """
    edge_length = [traci.lane.getLength(edge + '_0') / 1000
                   for edge in path]
    return sum(edge_length)
    
    
def get_path_free_travel_time(path):
    """
    Return the free flow travel time of the path.
    
    Parameters
    ----------
    path : array or list
    
    Returns
    -------
    free_travel_time : int
    
    """
    # TODO: realize this function
    return 
    

##########################

def get_remain_vehiclenumber(plan, current_edge):
    """
    返回主车选择某个plan当前时刻剩余路段的车辆总数
    
    Parameters
    ----------
    plan : list
        A list of route plans.
    current_edge : str
        ID of current edge.
        
    Returns
    -------
    veh_num : int
    """
    if current_edge in plan:
        index = plan.index(current_edge)
        plan_re = plan[index:]
    else:
        plan_re = plan
        
    veh_num_list = [traci.edge.getLastStepVehicleNumber(edge) 
                    for edge in plan_re]
    veh_num = sum(veh_num_list)
    return veh_num


def get_remain_edgelength(plan, current_edge):
    """
    主车选择某个plan当前时刻剩余路段的路段总长度
    
    Parameters
    ----------
    plan : list
        A list of route plans.
    current_edge : str
        ID of current edge.
        
    Returns
    -------
    edge_len : float
    """
    if current_edge in plan:
        index = plan.index(current_edge)
        plan_re = plan[index:]
    else:
        plan_re = plan

    edge_len_list = [traci.lane.getLength(edge + '_0') / 1000
                     for edge in plan_re]
    edge_len = sum(edge_len_list)
    return edge_len


def get_remain_vehiclelength(plan, current_edge):
    """
    主车选择某个plan当前时刻剩余路段的车辆总长度
    
    Parameters
    ----------
    plan : list
        A list of route plans.
    current_edge : str
        ID of current edge.
        
    Returns
    -------
    veh_length : float
    """
    if current_edge in plan:
        index = plan.index(current_edge)
        plan_re = plan[index:]
    else:
        plan_re = plan
        
    veh_num_list = [traci.edge.getLastStepVehicleNumber(edge) 
                    for edge in plan_re]
    mean_veh_len_list = [traci.edge.getLastStepLength(edge) 
                         for edge in plan_re]
    
    veh_len_list = [a*b for a,b in zip(veh_num_list, mean_veh_len_list)]
    return sum(veh_len_list)


def get_remain_edgelength_vehnum(plan, current_edge):
    """
    主车选择某个plan当前时刻剩余路段的路段总长度/车辆总数
    
    Parameters
    ----------
    plan : list
        A list of route plans.
    current_edge : str
        ID of current edge.
        
    Returns
    -------
    edge_length : float

    veh_num : int

    """
    if current_edge in plan:
        index = plan.index(current_edge)
        plan_re = plan[index:]
    else:
        plan_re = plan
        
    edge_len_list = [traci.lane.getLength(edge + '_0') / 1000
                     for edge in plan_re]
    veh_num_list = [traci.edge.getLastStepVehicleNumber(edge) 
                    for edge in plan_re]
    
    return sum(edge_len_list), sum(veh_num_list)


def get_remain_edgelength_vehnum_vehlen(plan, current_edge):
    """
    主车选择某个plan当前时刻剩余路段的路段总长度/车辆总数/车辆总长度
    
    Parameters
    ----------
    plan : list
        A list of route plans.
    current_edge : str
        ID of current edge.
        
    Returns
    -------
    edge_length : float

    veh_num : int
    
    veh_length : float

    """
    if current_edge in plan:
        index = plan.index(current_edge)
        plan_re = plan[index:]
    else:
        plan_re = plan
        
    edge_len_list = [traci.lane.getLength(edge + '_0') / 1000
                     for edge in plan_re]
    veh_num_list = [traci.edge.getLastStepVehicleNumber(edge) 
                    for edge in plan_re]
    mean_veh_len_list = [traci.edge.getLastStepLength(edge) 
                         for edge in plan_re]
    
    veh_len_list = [a*b for a,b in zip(veh_num_list, mean_veh_len_list)]
    return sum(edge_len_list), sum(veh_num_list), sum(veh_len_list)
