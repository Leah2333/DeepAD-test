import os
import sys
import time
import joblib
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

import traci
import tensorflow as tf
from tensorforce.agents import Agent, agent
from tensorforce.environments import Environment
from Tlab_SumoRL.kernel.environment.micro_env import MicroEnv

import matplotlib.pyplot as plt
from Tlab_SumoRL.utils.logger import logger
import argparse


tf.config.set_visible_devices(tf.config.get_visible_devices('CPU'))
tf.random.set_seed(1)

parser = argparse.ArgumentParser(description='微观强化学习')
parser.add_argument('-d', '--discount', type=float, 
                    dest='discount', default=0.999)
parser.add_argument('-r', '--l2regular', type=float, 
                    dest='l2regular', default=0.001)
parser.add_argument('-l', '--lr', type=float, 
                    dest='lr', default=0.005)
parser.add_argument('-e', '--exploration', type=float, 
                    dest='exploration', default=0.05)
parser.add_argument('-b', '--batchsize', type=int, 
                    dest='batchsize', default=64)
_args = parser.parse_args()

time_start = time.time()


version = 'v12'
env = Environment.create(
    environment=MicroEnv, 
    max_episode_timesteps=10000, training=True
)

discount = _args.discount
l2_regularization = _args.l2regular
learning_rate = _args.lr
exploration = _args.exploration
batch_size = _args.batchsize
print(f"discount: {discount}.")
print(f"l2_regularization: {l2_regularization}.")
print(f"learning_rate: {learning_rate}.")
print(f"exploration: {exploration}.")
print(f"batch_size: {batch_size}.")
# agent = Agent.create(
#     agent='a2c', environment=env, learning_rate=0.01, discount=discount, exploration=0.1, batch_size=64, l2_regularization=0.001,
#     memory=1000
# )
agent = Agent.create(
    agent='ppo', environment=env, 
    learning_rate=learning_rate,
    discount=discount, 
    exploration=exploration, 
    batch_size=batch_size, 
    l2_regularization=l2_regularization
    # memory=3000
)

alg = "ppo"
v_info = f"{alg}_{version}_{discount*1000}_{l2_regularization*1000}_{learning_rate*1000}_{exploration*1000}_{batch_size}"
returns_log = open(f'micro_{v_info}.txt', mode='a')
all_returns = []
history = []

for episode in range(10):
    states = env.reset()
    print(f"------{episode}------")

    terminal = 0
    sum_reward = 0
    num_updates = 0
    i = 0
    episode_history = []

    while not terminal:
        actions = agent.act(states=states)
        raw_actions = env.inverse_transform_action(actions).tolist()
        states, terminal, reward = env.execute(actions=actions)
        raw_actions.append(reward)
        raw_actions.append(traci.vehicle.getSpeed('test'))
        episode_history.append(raw_actions)
        num_updates += agent.observe(terminal=terminal, reward=reward)
        sum_reward += reward * discount**i
        i += 1
    history.append(episode_history)
    all_returns.append(sum_reward)
    returns_log.write(f"{sum_reward}\n")
    returns_log.flush()
    print(f'Episode {episode}: return={sum_reward} updates={num_updates}')

returns_log.close()
agent.save(filename=f'micro_{version}', directory='checkpoints', 
           format='numpy', append='episodes')

plt.figure()
plt.plot(all_returns)
plt.show()

joblib.dump(history, f'history_{version}.pkl')

time_end = time.time()
logger.info(f"Elapsed time: {time_end - time_start:.3f}s")

path2 = r'draw.txt'
file2 = open(path2,'w+')
for i in all_returns:
    file2.write(str(i))
    file2.write('\n')

file2.close()