from configparser import ConfigParser
from addict import Dict

cfg_parser = ConfigParser(allow_no_value=True)

cfg_parser.read('config.ini')
config = Dict(cfg_parser._sections)

config.env.use_gui = (config.env.use_gui.lower() == 'true') or \
    (config.env.use_gui == '1')
config.env.n_plans = int(config.env.n_plans)
config.env.random_state = int(config.env.random_state)
config.env.max_episode_timesteps = int(config.env.max_episode_timesteps)
config.vehicle.entrance_time = int(config.vehicle.entrance_time)

CFG = config
