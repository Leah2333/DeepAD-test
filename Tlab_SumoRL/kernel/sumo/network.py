import os
import sys
import re
import sumolib
if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from Tlab_SumoRL.utils.config import CFG
from Tlab_SumoRL.utils.logger import logger


def is_junction_edge(current_edge):
    return ':' in current_edge
    

def get_downstream_edges(current_edge):
    """
    Get downstream edges of the current edge.
    
    Paramters
    ---------
    current_edge : str
        ID of the current edge.
    
    Returns
    -------
    answer : list
        A list of downstream edges.
    """
    net = sumolib.net.readNet(CFG.path.network)
    edge_test = net.getEdge(current_edge).getOutgoing()
    edge_test_list = []
    for key in edge_test:
        edge_test_list.append(str(key))   
    pre_answer = []
    answer = []
    for i in edge_test_list:
        pattern = re.compile(".*id=(.*)from.*")
        pre_answer = pattern.findall(i)
        for j in pre_answer:
            answer.append(eval(j))
    return answer


def get_next_edge(current_edge, path):
    """
    Get the next edge in current path.
    
    Paramters
    ---------
    current_edge : str
        ID of the current edge.
        
    path : list of str
        The designated path.
    
    Returns
    -------
    next_edge : str
        ID of the next edge.
        
    """
    current_idx = path.index(current_edge)
    next_idx = current_idx + 1
    if next_idx < len(path):
        return path[next_idx]
    else:
        return None
    