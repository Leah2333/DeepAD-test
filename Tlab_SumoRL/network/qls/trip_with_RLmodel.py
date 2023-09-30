import os
from re import I
import sys
import time
import numpy as np
import pandas as pd 

# cluster_list = [8, 15, 18]

def qls_route_file(cluster_list):
    # 数据读取
    
    od_data = pd.read_csv('OD_DBSCAN.csv')
    od_data_group = od_data.groupby('cluster')
    od_cluster, depart_time = [], []
    for cluster in cluster_list: # 处理各类别
        od_cluster_data = od_data_group.get_group(cluster)
        for i in range(od_cluster_data.shape[0]):
            route = od_cluster_data['route'].iloc[i]
            if len(str.split(route)) >= 2: # 不考虑仅存在一条路段的od数据
                o = str.split(route)[0]
                d = str.split(route)[-1]
                depart = od_cluster_data['depart'].iloc[i]
                od_cluster += [[cluster, o, d, depart]]
                depart_time += [depart]
    od_data_sorted = []
    for i in np.argsort(depart_time):
        od_data_sorted += [od_cluster[i]]

    color_dict = {8:'0,0,1', 15:'0,1,0', 18:'1,0,0'}

    entrance_info = {}
    with open("qls_RL.rou.xml", "w") as routes:
        print("""<routes>""", file=routes)
        for i in range(len(od_data_sorted)):
            od = od_data_sorted[i]
            cluster, o, d, depart = int(od[0]), str(od[1]), str(od[2]), int(od[3])
            color = color_dict[cluster]
            print("""    <trip id="cluster%d_%d" color="%s" depart="%d" from="%s" to="%s"/>"""%(cluster, i, color, depart, o, d), file=routes)
            entrance_info["cluster%d_%d"%(cluster, i)] = depart
        print("</routes>", file=routes)

    np.save('vehicle_entrance_info.npy', entrance_info)
    
    


def change_sumocfg():
    with open("new.net.sumocfg", "w") as cfgfile:
        print("""
        <configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">

            <input>
                <net-file value="new.net.xml" />
                <route-files value="qls_RL.rou.xml"/>
                <additional-files value="taz.add_new.xml,poly.add.xml,basic.vType.xml,loop.xml"/>
            </input>

            <time>
                <begin value="0.0" />
                <step-length value="1" />
                <end value="3600.0" />
            </time>

            <output>
                <output-prefix value="output." />
                <summary-output value="summary.xml" />
                <tripinfo-output value="tripinfo.xml" />
                <tripinfo-output.write-unfinished value="false" />
                <edgeData id="dataset1" freq="60" withInternal="true" file="data_day1.xml"/>
                <vehroute-output value="vehroute.xml"/>
            </output>

            <processing>
                <ignore-route-errors value="true" />
                <lateral-resolution value="0.8" />
                <ignore-junction-blocker value="60" />
                <collision.action value="teleport" />
                <collision.mingap-factor value="0" />
                <time-to-teleport value="300" />
                <max-depart-delay value="900" />
                <time-to-impatience value="120" />
                <pedestrian.model value="striping" />
                <pedestrian.striping.stripe-width value="0.55" />
                <pedestrian.striping.jamtime value="60" />
            </processing>

            <routing>
                <persontrip.transfer.car-walk value="parkingAreas,ptStops,allJunctions" />
                <device.rerouting.probability value="1" />
                <device.rerouting.period value="300" />
                <device.rerouting.pre-period value="300" />
                <person-device.rerouting.probability value="1" />
                <person-device.rerouting.period value="300" />
            </routing>

            <report>
                <verbose value="true" />
                <no-step-log value="true" />
                <duration-log.statistics value="true" />
                <duration-log.disable value="false" />
                <no-warnings value="false" />
            </report>

            <random_number>
                <seed value="42" />
            </random_number>

        </configuration>""", file=cfgfile)

if __name__ == "__main__":
    cluster_list = [8, 15, 18]
    qls_route_file(cluster_list)