import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

    
def load_monitor_file(file):
    """
    Load stable-baseline monitor file.
    
    Paramters
    ---------
    file : str or Path or FileBuffer
        Monitor file.
    
    Returns
    -------
    monitor : pd.DataFrame
        Dataframe of monitor file.
    """
    monitor = pd.read_csv(file, skip_blank_lines=True, skiprows=1)
    monitor.columns = ['episode reward', 'episode length', 'episode time']
    return monitor


def plot_reward(file, window=None, save=None):
    """
    Load stable-baseline monitor file.
    
    Paramters
    ---------
    file : str or Path or FileBuffer
        Monitor file.
    window : int
        Size of the moving window. This is the number of observations used for calculating the smoothed reward curve.
    save : str or Path
        Whether to save image to a path.
    """
    monitor = load_monitor_file(file)
    plt.figure(figsize=(16, 3.5), dpi=150)
    if window is None:
        sns.lineplot(data=monitor[['episode reward']])
    else:
        monitor['smoothed episode reward'] = monitor['episode reward'].rolling(
            window=window, min_periods=1).mean()
        sns.lineplot(
            data=monitor[['episode reward', 'smoothed episode reward']])
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    if save is not None:
        plt.savefig(save, bbox_to_inches='tight')
    plt.show()
