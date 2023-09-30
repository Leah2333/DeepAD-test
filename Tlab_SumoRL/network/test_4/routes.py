import random


ROUTE_HEADER = """<routes>
        <vType vClass="passenger"  id="passenger4" accel="2" decel="1.5" sigma="0.5" length="4.5" color="255,255,255" guiShape="passenger" />
		<vType vClass="passenger"  id="passenger3" accel="3" decel="1.5" sigma="0.5" length="5" color="blue" guiShape="passenger"/>
		<vType vClass="passenger" id="passenger2" accel="2" decel="1.5" sigma="0.5" length="4.5" color="255,255,255" guiShape="passenger" />
        <route id="normal1" edges="0/1to1/1 1/1to2/1"/>
		<route id="normal2" edges="0/1to1/1 1/1to1/0"/>
		<route id="normal3" edges="0/1to1/1 1/1to1/2"/>
"""

N = 1000  # 时间


def generate_routefile(random_state=233):
    random.seed(random_state)  # 随机种子
    # 不同方向每秒的需求量
    number1 = random.uniform(0.5, 0.6)
    number2 = random.uniform(0.4, 0.7)
    number3 = random.uniform(0.8, 1)
    content = ROUTE_HEADER
    
    vehNr = 0
    for i in range(N):
        if random.uniform(0, 0.5) < number1:
            content += f'    <vehicle id="outright_{vehNr}" type="passenger4" departLane="random" lcCooperative="0.000001" route="normal1" depart="{i}"/>\n'
            vehNr += 1
        if random.uniform(0, 0.5) < number2:
            content += f'    <vehicle id="middleright_{vehNr}" type="passenger2" departLane="random" lcCooperative="0.000001" route="normal2" depart="{i}"/>\n'
            vehNr += 1
        if random.uniform(0, 0.5) < number3:
            content += f'    <vehicle id="middleright2st_{vehNr}" type="passenger3" departLane="random" lcCooperative="0.000001" route="normal3" depart="{i}" color="blue"/>\n'
            vehNr += 1
    content += "</routes>"
    
    with open("C:/Users/12611/Desktop/RL_Micro_control/Tlab_SumoRL2/network/test_2/test3.rou.xml", "w") as routes:
        routes.write(content)

generate_routefile()