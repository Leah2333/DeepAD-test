import os
import sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

import gym
from gym import spaces
from gym.utils import seeding
from sklearn.preprocessing import MinMaxScaler
from tensorforce.environments import Environment
import numpy as np
import pandas as pd

import traci
from Tlab_SumoRL.kernel.agent.vehicle_agent import VehicleAgent
from Tlab_SumoRL.kernel.sumo.interaction import check_sumo_binary, sumo_step
from Tlab_SumoRL.utils.config import CFG
from Tlab_SumoRL.utils.logger import logger


ACTION_SPACE = spaces.Box(low=0, high=1, shape=(4,))
OBS_SPACE = spaces.Box(low=0, high=1, shape=(23,))
# action: acc, left, stay, right
ACC_MIN_ACTION = -2
ACC_MAX_ACTION = 2
TRANSFORM_ACTION = MinMaxScaler().fit([
    [ACC_MIN_ACTION, 0, 0, 0], 
    [ACC_MAX_ACTION, 1, 1, 1]
])
LANE_CHANGE = {0: 'left', 1: 'stay', 2: 'right'}
# obs: ego_x, ego_v, ego_a, ego_xlat
# + 6 * neighbours: [x, v, a]
DIST_MAX = 1000
V_MAX = 150 / 3.6
A_MIN = -3
A_MAX = 3
LANE_MAX = 5
DIST_SENSE_MAX = 200
TRANSFORM_OBS = MinMaxScaler().fit([
    [0, 0, A_MIN, 0, 0] + [0, 0, A_MIN] * 6, 
    [DIST_MAX, V_MAX, A_MAX, LANE_MAX, LANE_MAX] + \
        [DIST_SENSE_MAX, V_MAX, A_MAX] * 6
])


class MicroEnv(Environment):
    """
    An environment for Micro lane changing and car following.
    """
    def __init__(self, volume, training=False):
        super().__init__()
        
        self.sumocfg = CFG.path.sumocfg
        self.network = CFG.path.network
        self._sumo_binary = check_sumo_binary(CFG.env.use_gui)
        self.training = training
        self.seed()
        self.num=volume
        self.episode_timestep = 0
        self.n_episode = 0
        self.action_space = ACTION_SPACE
        self.observation_space = OBS_SPACE
        self.action_scaler = TRANSFORM_ACTION
        self.observation_scaler = TRANSFORM_OBS
        self.vehicle=[]
        self._last_edge=[]
        self.infram=[0]*volume
        

    def get_micro_state(self, vehicle, num, normalize=True):
        state = []
        if 1:
            try: vehicle.current_edge
            except: state = np.zeros(OBS_SPACE.shape[0])
            else:
                self.infram[num]=1
                if vehicle.current_edge!='':
                    ego_state = [
                        min(vehicle.pos_lng, 1000), 
                        vehicle.speed_lng,
                        vehicle.acc_lng, 
                        vehicle.pos_lat,
                        vehicle.target_lane_number
                    ]
                    other_states = vehicle.neighbour_info("l") + \
                        vehicle.neighbour_info("f") + \
                        vehicle.neighbour_info("ll") + \
                        vehicle.neighbour_info("lf") + \
                        vehicle.neighbour_info("rl") + \
                        vehicle.neighbour_info("rf")
                    
                    state = ego_state + other_states
                    if normalize:
                        state = np.array(state)[np.newaxis, ...]
                        state = self.observation_scaler.transform(state)
                        state = np.where(state < 1, state, 1)
                        state = np.where(state > 0, state, 0)
                        # sense_dist_indices = 0, np.arange(4, 22, 3)
                        # state[sense_dist_indices] = np.where(
                        #     state[sense_dist_indices] < 1, 
                        #     state[sense_dist_indices], 1
                        # )
                else:
                    state = np.zeros(OBS_SPACE.shape[0])
                
            
        return state.ravel()
    
    
    @property
    def state(self):
        finals = []
        for i in range(self.num):
            finals.append(self.get_micro_state(self.vehicle[i],i))
        return finals
    
    
    def inverse_transform_action(self, scaled_action):
        action = np.array(scaled_action)[np.newaxis, ...]
        action = self.action_scaler.inverse_transform(action).ravel()
        return action
    

    def step(self, action):
        i=-1
        rewards=[]
        termi=1
        for action_i in action:
            if self.terminal(i):
                rewards.append(200)
            elif self.vehicle[i].in_network==0:
                rewards.append(0)
            else:
                i+=1
                action_i = np.array(action_i)
                action_i = np.where(action_i < 1, action_i, 1)
                action_i = np.where(action_i > 0, action_i, 0)
                assert self.action_space.contains(action_i), f"Invalid action_i: {action_i}"
                action_i = self.inverse_transform_action(action_i)
                
                # change speed
                acc_action_i = action_i[0]
                self.vehicle[i].accelerate(acc=acc_action_i)
        
                # change lane
                u_lf = np.exp(action_i[1])
                u_st = np.exp(action_i[2])
                u_rt = np.exp(action_i[3])
                lane_action_i = np.argmax([u_lf, u_st, u_rt])
                if (self.vehicle[i].pos_lat == 0 and lane_action_i == 2) or \
                   (self.vehicle[i].pos_lat == self.vehicle[i].current_edge_lanes - 1 and \
                       lane_action_i == 0):
                    lane_action_i = 1
                self.vehicle[i].change_lane(LANE_CHANGE[lane_action_i])
                
                reward = self.compute_reward(acc_action_i, lane_action_i,i)
                
                self.episode_timestep = sumo_step()
                if acc_action_i > 0:
                    print(f">>> {self.episode_timestep} - {acc_action_i} - {lane_action_i}")
    
                if self.terminal(i):
                    reward += 200 # 终点额外奖励！
                    logger.info(f'******* terminated: {self.episode_timestep}')
                    
                else:
                    self._last_edge[i] = self.vehicle[i].current_edge
                    self._last_episode_timestep = self.episode_timestep
                    
                rewards.append(reward)
            ter=self.terminal(i)
            if ter==0:
                termi=0
        return self.state, rewards, termi, {}

    @property
    def terminal(self,i):
        return self.is_terminal(i)
    
    
    def is_terminal(self,i):
        if (self.vehicle[i].current_edge != self._last_edge[i]) and \
            (self._last_edge[i] is not None):
            return 1
        else:
            return 0


    def close(self):
        traci.close()
        super().close()
        

    def seed(self, seed=CFG.env.random_state):
        self.np_random, self.random_state = seeding.np_random(seed)
        return [self.random_state]


    def reset(self):
        logger.info('******* [reset] *******')
        try: self.close()
        except: pass
        
        self.episode_timestep = 0
        self._last_episode_timestep = 0
        self.n_episode += 1
        
        for i in range(self.num):
            vg_random_state = self.random_state + self.n_episode
            self.vehicle.append(VehicleAgent.from_config(random_state=vg_random_state))
        self.start_sumo()
        if self.training:
            self._alter_training_destination()
                
        for i in range(self.num):        
            
            self.vehicle[i].add_to_network()
            
            logger.info(f"origin::::::{i.origin}")
#            while not i.in_network:
#                self.episode_timestep = sumo_step()
#            while i.current_edge != i.origin:
#                self.episode_timestep = sumo_step()
#            while i.current_edge == i.origin:
#                self.episode_timestep = sumo_step()
                
            logger.info(f'target lane: {i.target_lane}')
            logger.info(f'******* entrance:  {self.episode_timestep}')
            self._last_edge[i] = None
            
        self.episode_timestep = sumo_step()
        self._last_episode_timestep = self.episode_timestep
        return self.state
    
    
    def soft_reset(self, origin, destination, vehicle_id , entrance_time):
        logger.info('******* [soft reset] *******')
        try: self.close()
        except: pass

        self.episode_timestep = 0
        self._last_episode_timestep = 0
        self.n_episode += 1
        
        
        vg_random_state = self.random_state + self.n_episode
        self.vehicle.append( VehicleAgent(
            network=self.network,
            vehicle_id=vehicle_id,
            origin=origin,
            destination=destination,
            entrance_time=entrance_time,
            random_state=vg_random_state
        ))
        self.vehicle[-1].set_plans([origin, destination])
        self._last_edge.append(None)
    
    
    def start_sumo(self):
        traci.start([
            self._sumo_binary, '-c', self.sumocfg, 
            '--lateral-resolution', '0.6'
        ])


    def compute_reward(self, acc_action, lane_action,i):
        reward =  self._comfort_reward(acc_action, lane_action, 0.5, 1)
        reward += self._safety_reward(i)
        reward += self._efficiency_reward(i)
        return reward

    
    def _comfort_reward(self, acc_action, lane_action, alpha=1, beta=1):
        r = -alpha * abs(lane_action - 1)
        r -= beta * acc_action**2
        return r

    
    def _safety_reward(self,i):
        if any(self.vehicle[i].is_collision()):
            return -200
        else:
            return 0

    
    def _efficiency_reward(self, i, alpha=1):
        r_cf = alpha * self.vehicle[i].speed_lng
        # r = -alpha * abs(self.vehicle.speed_lng - self.vehicle.expected_speed)
        ln = self.vehicle[i].pos_lat
        tl = self.vehicle[i].target_lane_number
        r_lc = - abs(tl - ln)
        return r_cf + r_lc


    def _alter_training_destination(self):
        for i in self.vehicle:
            destinations = ['1/4to1/2', '1/4to2/1', '1/4to1/0']
            o = i.origin
            d = self.np_random.choice(destinations, size=1)[0]
            i.set_destination(d)
            i.set_plans([o, d])
            # self.vehicle.set_route([o, d])
    
    
    def states(self):
        return dict(type="float", shape=self.observation_space.shape)
    
    
    def actions(self):
        return dict(type="float", shape=self.action_space.shape)
        
    
    def execute(self, actions):
        state, reward, terminal, _ = self.step(actions)
        return state, terminal, reward
    