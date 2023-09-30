import numpy as np
from scipy.stats import rankdata
from copy import deepcopy

# from Tlab_SumoRL.kernel.agent.memory_travel_time import FixedMemoryTravelTime
from Tlab_SumoRL.kernel.sumo.interaction import *
from Tlab_SumoRL.kernel.sumo.routes import generate_target_routefile
# from Tlab_SumoRL.kernel.sumo.Kplans import get_kplans
from Tlab_SumoRL.utils.config import CFG


class VehicleAgent():
    """
    Agent of driving vehicles.
    
    Parameters
    ----------
    network : str
        path of network file.
    vehicle_id : str
        ID of the vehicle agent.
    origin : str
        ID of the origin edge.
    destination : str
        ID of the destination edge.
    entrance_time : float
        Entrance time of the agent in the network.
    tag : str
        Tag for this vehicle.
    plans : int or list or None
        Route plans of the agent.
        plans: [plan A, plan B, ...]
        plan X: [edge 0, edge 1, ..., edge n]
    random_state : int
        Seed of the random generator.
        
    Attributes
    ----------
    current_edge : str
        ID of the edge currently travelled by the agent.
    """
    def __init__(self, 
                 network, vehicle_id,
                 origin, destination, 
                 entrance_time,
                 passengers=[],
                 tag='default',
                 random_state=233):
        # print('initing vehicle agent!')
        self.network = network
        self.vehicle_id = vehicle_id
        self.origin = origin
        self.destination = destination
        self.entrance_time = entrance_time
        self.tag = tag
        self.random_state = random_state
        self.plans = None
        self.lanechange_duration = 10

        self.terminal = False
        self.passengers = passengers
        
    

    # def init_memory_travel_time(self):
    #     self.memory_travel_time = FixedMemoryTravelTime(self.plans)

    
    def set_origin(self, origin):
        self.origin = origin
    
    
    def set_destination(self, destination):
        self.destination = destination
    
    
    def set_plans(self, plans):
        # if plans is None:
        #     self.plans = get_kplans(
        #         self.origin, self.destination, k=10)
        # elif isinstance(plans, int):
        #     self.plans = get_kplans(
        #         self.origin, self.destination, k=plans)
        # else:
        self.plans = [plans]
        self.n_plans = len(self.plans)


    def set_color(self, color):
        traci.vehicle.setColor(self.vehicle_id, color)

    def set_type(self, type):
        traci.vehicle.setType(self.vehicle_id, type)

    def set_vclass(self, vclass):
        traci.vehicle.setVehicleClass(self.vehicle_id, vclass)

    def set_route(self, edge_list):
        traci.vehicle.setRoute(self.vehicle_id, edge_list)

    def accelerate(self, acc, time_length=1, smooth=False):
        new_speed = self.speed_lng + acc * time_length
        new_speed = max(new_speed, 0)
        if smooth:
            traci.vehicle.slowDown(self.vehicle_id, new_speed, time_length)
        else:
            traci.vehicle.setSpeed(self.vehicle_id, new_speed)

    def terminate(self):
        self.terminal = True

    def reset(self):
        self.terminal = False

    
    def add_to_network(self):
        route_id = f"route_{self.vehicle_id}"
        traci.route.add(
            routeID=route_id, 
            edges=self.plans[0])
        traci.vehicle.add(
            vehID=self.vehicle_id, 
            routeID=route_id, 
            depart=self.entrance_time)
        self.set_color((249, 40, 10))
        

    @property
    def current_edge(self):
        """
        Current edge of the vehicle.
        """
        return get_current_edge(self.vehicle_id)

    @property
    def current_edge_lanes(self):
        """
        Number of lanes of the current edge.
        """
        return get_total_lane_num(self.vehicle_id)
    
    @property
    def pos_lng(self):
        """
        Longitudinal position (distance to the following junction).
        """
        return get_longitudinal_position(self.vehicle_id)
    
    @property
    def speed_lng(self):
        """
        Logitudinal speed. (m/s)
        """
        return get_longitudinal_speed(self.vehicle_id)
    
    @property
    def acc_lng(self):
        """
        Logitudinal acceleration. (m/s^2)
        """
        return get_longitudinal_acceleration(self.vehicle_id)
    
    @property
    def acc_lat(self):
        """
        Lateral acceleration. (m/s^2)
        """
        return get_lateral_acceleration(self.vehicle_id)
    
    @property
    def pos_lat(self):
        """
        Lateral position (lane number from sidewalk).
        """
        return int(get_lateral_position(self.vehicle_id))
    
    @property
    def speed_lat(self):
        """
        Lateral speed. (m/s)
        """
        return get_lateral_speed(self.vehicle_id)
    
    @property
    def expected_speed(self):
        """
        Expected speed. (m/s)
        """
        return get_expected_speed(self.vehicle_id)
    
    @property
    def target_lane(self):
        """
        Lane names to which the vehicle will move.
        """
        # return get_target_lane(self.vehicle_id)
        return '1/4to1/2'
    
    @property
    def target_lane_number(self):
        """
        Lane number to which the vehicle will move.
        """
        target_lane = self.target_lane
        if len(target_lane) > 0:
            return int(target_lane[0][-1])
        else:
            return self.pos_lat
    
    @property
    def in_network(self):
        """
        Whether this vehicle is in network.
        """
        return vehicle_in_network(self.vehicle_id)

    
    def neighbour_info(self, kind="leader", return_id=False):
        """
        获取车辆邻居车辆的信息，包括ID、距离、速度、加速度。
        
        Parameters
        ----------
        kind : str
            Position of the neighbour: "leader", "follower", "leftleader", "leftfollower", "rightleader", "rightfollower"
        return_id : boolean
            Whether return the ID of the neighbour.
        
        Returns
        -------
        res : list
            ID(optional), distance, speed, acceleration
        
        """
        kind = kind.lower()
        if kind == "leader" or kind == "l":
            res = get_leader_info(self.vehicle_id)
        elif kind == "follower" or kind == "f":
            res = get_follower_info(self.vehicle_id)
        elif kind == "leftleader" or kind == "ll":
            res = get_left_leader_info(self.vehicle_id)
        elif kind == "leftfollower" or kind == "lf":
            res = get_left_follower_info(self.vehicle_id)
        elif kind == "rightleader" or kind == "rl":
            res = get_right_leader_info(self.vehicle_id)
        elif kind == "rightfollower" or kind == "rf":
            res = get_right_follower_info(self.vehicle_id)
        else:
            raise ValueError(f"Neighbour {kind} does not exist.")
        if res == []:
            res = ['', 2000, 0, 0]
        if return_id:
            return res
        else:
            return res[1:]
        
    
    def change_lane(self, direction="stay"):
        if direction == "left":
            traci.vehicle.changeLaneRelative(
                self.vehicle_id, 1, self.lanechange_duration)
        elif direction == "right":
            traci.vehicle.changeLaneRelative(
                self.vehicle_id, -1, self.lanechange_duration)
        elif direction == "stay":
            traci.vehicle.changeLaneRelative(
                self.vehicle_id, 0, 0)
        else:
            raise ValueError(f"Unknown direction {direction}.")
        
    
    def is_collision(self):
        return is_collision(self.vehicle_id)
    
    
    def shape_position(self):
        return get_shape_position(self.vehicle_id)


    @classmethod
    def from_config(cls, **kwargs):
        cfg_ = deepcopy(CFG)
        if 'entrance_time' in kwargs.keys():
            cfg_.vehicle.entrance_time = kwargs['entrance_time']
        if 'random_state' in kwargs.keys():
            cfg_.vehicle.random_state = kwargs['random_state']

        v = cls(
            vehicle_id=cfg_.vehicle.vehicle_id,
            network=cfg_.path.network,
            origin=cfg_.vehicle.origin,
            destination=cfg_.vehicle.destination,
            entrance_time=cfg_.vehicle.entrance_time,
            random_state=cfg_.env.random_state
        )
        v.set_plans([v.origin, v.destination])
        return v


def generate_vehicle_agent(
    entrance_time=None,
    random_state=233,
    _lc_training=False):
    """
    Generator of vehicle agents.
    
    Paramters
    ---------
    entrance_time : int
        The time when the vehicle agent enters the network.
    random_state : int
        Seed of the random generator.
    """
    if entrance_time is not None:
        entrance_time = entrance_time
    else:
        entrance_time = generate_target_routefile(random_state)
    vehicle = VehicleAgent(
        vehicle_id=CFG.vehicle.vehicle_id,
        network=CFG.path.network,
        origin=CFG.vehicle.origin,
        destination=CFG.vehicle.destination,
        entrance_time=entrance_time,
        random_state=random_state
    )

    # whether random destination for lane chaning env training
    if _lc_training:
        destinations = [
            '1/4to1/2', '1/4to2/1', '1/1to1/0'
        ]
        vehicle.set_destination(np.random.choice(destinations, 1)[0])
    return vehicle
