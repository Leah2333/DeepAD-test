import random
from Tlab_SumoRL.utils.config import CFG
from Tlab_SumoRL.utils.logger import logger


ROUTE_HEADER = """<routes>
    <vType id="typenormal" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>
    <vType id="typebus" accel="0.8" decel="4.5" sigma="0.5" length="7" minGap="3" maxSpeed="13" guiShape="bus"/>

    <route id="outright" edges="3@4#0 4@5#0 5@6#0 6@2#0 1@2#0" />
    <route id="middleright" edges="3@12#0 12@13#0 13@24#0 24@21#0" />
    <route id="middleright2" edges="4@3#0 3@12#0 12@11#0 11@10#0 " />
    <route id="middleright3" edges="6@5#0 5@9#0 9@10#0 10@16#0 16@18#0" />
    <route id="circle" edges="9@8#0 8@7#0 7@18#0 18@16#0 16@10#0" />
    <route id="circle2" edges="4@11#0 11@14#0 14@15#0 15@19#0" />
    <route id="circle3" edges="15@14#0 14@23#0 23@22#0 22@21#0" />
    <route id="circle4" edges="2@6#0 6@8#0 8@16#0 16@18#0" />
    <route id="circle5" edges="10@16#0 16@17#0 17@19#0 19@15#0" />
"""

N = 1500  # 时间


def generate_routefile(random_state=233):
    '''
    随机背景车流量
    '''
    # logger.debug(f'******** [generate_routefile]  RANDOM SEED: {random_state} ******')
    random.seed(random_state)  # 随机种子
    # 不同方向每秒的需求量
    number1 = random.uniform(0.08, 0.12)
    number2 = random.uniform(0.04, 0.09)
    number3 = random.uniform(0.1, 0.15)
    number4 = random.uniform(0.12, 0.15)
    number5 = random.uniform(0.2, 0.24)
    number6 = random.uniform(0.12, 0.15)
    number7 = random.uniform(0.19, 0.22) 
    number8 = random.uniform(0.12, 0.15)
    number9 = random.uniform(0.09, 0.12)    
    content = ROUTE_HEADER
    
    vehNr = 0
    for i in range(N):
        if random.uniform(0, 1) < number1:
            content += f'    <vehicle id="outright_{vehNr}" type="typenormal" route="outright" depart="{i}"/>\n'
            vehNr += 1
        if random.uniform(0, 1) < number2:
            content += f'    <vehicle id="middleright_{vehNr}" type="typenormal" route="middleright" depart="{i}"/>\n'
            vehNr += 1
        if random.uniform(0, 1) < number3:
            content += f'    <vehicle id="middleright2st_{vehNr}" type="typebus" route="middleright2" depart="{i}" color="blue"/>\n'
            vehNr += 1
        if random.uniform(0, 1) < number4:
            content += f'    <vehicle id="middleright3st_{vehNr}" type="typebus" route="middleright3" depart="{i}" color="blue"/>\n'
            vehNr += 1
        if random.uniform(0, 1) < number5:
            content += f'    <vehicle id="circle_{vehNr}" type="typenormal" route="circle" depart="{i}" color="1,0,0"/>\n'
            vehNr += 1
        if random.uniform(0, 1) < number6:
            content += f'    <vehicle id="circle_{vehNr}" type="typenormal" route="circle2" depart="{i}" color="1,0,0"/>\n'
            vehNr += 1
        if random.uniform(0, 1) < number7:
            content += f'    <vehicle id="circle_{vehNr}" type="typenormal" route="circle3" depart="{i}" color="1,0,0"/>\n'
            vehNr += 1
        if random.uniform(0, 1) < number7:
            content += f'    <vehicle id="circle_{vehNr}" type="typenormal" route="circle4" depart="{i}" color="1,0,0"/>\n'
            vehNr += 1
        if random.uniform(0, 1) < number8:
            content += f'    <vehicle id="circle_{vehNr}" type="typenormal" route="circle5" depart="{i}" color="1,0,0"/>\n'
            vehNr += 1
    content += "</routes>"
    
    with open(CFG.path.routes, "w") as routes:
        routes.write(content)


def generate_target_routefile(random_state=233, to_file=False):
    if random_state is None:
        entrance_time = CFG.vehicle.entrance_time
    else:
        random.seed(random_state)  # 随机种子
        entrance_time = random.randint(400, 500)
    logger.debug(f'******** [generate_target_routefile]  RANDOM SEED: {random_state} + {entrance_time} ******')
    
    if to_file:
        with open(CFG.path.target_routes, "w") as routes:
            content = f"""<routes>
            <vType vClass="passenger" id="passenger" accel="2" decel="1.5" sigma="0.5" length="4" color="255,255,255" guiShape="passenger"/>
            <vehicle id="test" type="passenger" depart="{entrance_time}" color="orange">
            <route edges="0/2to1/2 "/> 
            </vehicle>
            </routes>"""
            routes.write(content)
    print(f"entrance time {entrance_time}")
    return entrance_time
