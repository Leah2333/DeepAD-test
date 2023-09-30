import os
import sys
import math

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    import sumolib
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

def read_sumo_net(path):
    # input: path of sumo network
    net = sumolib.net.readNet(path, withInternal=False) # 'withPedestrianConnections'
    return net

def sub(p1, p2):
    return (p1[0] - p2[0], p1[1] - p2[1])

def get_angle2D(p1, p2):
    '''
    input: p1(x1,y1) p2(x2,y2) 
    return 第二个角减第一个角的角度 degree 度
    atan 角度定义：以x轴正向开始，逆时针为正
    '''
    theta1 = math.atan2(p1[1], p1[0])
    theta2 = math.atan2(p2[1], p2[0])
    dtheta = theta2 - theta1
    
    while dtheta > math.pi:
        dtheta -= 2.0 * math.pi
    while dtheta < -math.pi:
        dtheta += 2.0 * math.pi
    
    return dtheta/math.pi*180

def obtain_direction(net,fromEdge,toEdge,threshold):
    '''
    得到单个(fromEdge,toEdge)对的方向
    如果theta 为正 -> 第二个角度减第一个角度为正 -> 第一个角度逆时针才可以到达第二个角度 -> 左转
    考虑到角度的微量差距，认为两个方向角度差值在threshold(degree)以内依然是直行
    比如第二个角->第一个角差距在20度(threshold=20)以内，不认为是左右转，认为是直行
    '''
    fromEdge = net.getEdge(fromEdge)
    toEdge = net.getEdge(toEdge)
    fromEdgeDirection = sub(fromEdge.getShape()[-1], fromEdge.getShape()[0])
    toEdgeDirection = sub(toEdge.getShape()[-1], toEdge.getShape()[0])
    angle = get_angle2D(fromEdgeDirection,toEdgeDirection) 
    if math.fabs(angle) > threshold:
        if angle < 0:
            return "right"
        elif angle > 0:
            return "left"
    else:
        return "through"


def obtain_direction_from_list(net,plan_list,threshold):
    '''
    input: ['Oto0/2', '0/2to1/2', '1/2to2/2', '2/2to2/1', '2/1to3/1', '3/1to3/0', '3.0toD']
    output: ['through', 'through', 'right', 'left', 'right', 'left']
    两两组成一个方向对 所以output 比 input 少一个元素
    '''
    direction_list = []
    for i in range(len(plan_list)-1):
        direction_list.append(obtain_direction(net,plan_list[i],plan_list[i+1],threshold))
    return direction_list

def obtain_target_lane()

if __name__ == "__main__":
    net = read_sumo_net('net.net.xml')
    directions = obtain_direction(net, '1/1to2/1', '2/1to2/0', 20)
    print(directions)
    # directions = obtain_direction_from_list(net,['Oto0/2', '0/2to1/2', '1/2to2/2', '2/2to2/1', '2/1to3/1', '3/1to3/0', '3.0toD'],20)
    # print(directions)
    # test_list = [['Oto0/2', '0/2to1/2', '1/2to2/2', '2/2to2/1', '2/1to3/1', '3/1to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to1/2', '1/2to1/1', '1/1to1/0', '1/0to2/0', '2/0to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to0/1', '0/1to0/0', '0/0to1/0', '1/0to2/0', '2/0to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to0/1', '0/1to0/0', '0/0to1/0', '1/0to2/0', '2/0to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to0/1', '0/1to1/1', '1/1to2/1', '2/1to2/0', '2/0to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to0/1', '0/1to0/0', '0/0to1/0', '1/0to2/0', '2/0to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to1/2', '1/2to1/1', '1/1to0/1', '0/1to0/2', '0/2to1/2', '1/2to2/2', '2/2to2/1', '2/1to3/1', '3/1to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to1/2', '1/2to2/2', '2/2to2/1', '2/1to3/1', '3/1to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to1/2', '1/2to2/2', '2/2to2/1', '2/1to3/1', '3/1to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to0/1', '0/1to0/0', '0/0to1/0', '1/0to1/1', '1/1to2/1', '2/1to3/1', '3/1to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to0/1', '0/1to1/1', '1/1to1/2', '1/2to2/2', '2/2to2/1', '2/1to3/1', '3/1to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to1/2', '1/2to1/1', '1/1to2/1', '2/1to3/1', '3/1to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to1/2', '1/2to1/1', '1/1to2/1', '2/1to3/1', '3/1to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to1/2', '1/2to1/1', '1/1to0/1', '0/1to0/2', '0/2to1/2', '1/2to2/2', '2/2to2/1', '2/1to3/1', '3/1to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to0/1', '0/1to1/1', '1/1to2/1', '2/1to3/1', '3/1to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to0/1', '0/1to1/1', '1/1to1/2', '1/2to0/2', '0/2to0/1', '0/1to0/0', '0/0to1/0', '1/0to2/0', '2/0to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to0/1', '0/1to0/0', '0/0to1/0', '1/0to2/0', '2/0to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to1/2', '1/2to2/2', '2/2to2/1', '2/1to3/1', '3/1to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to1/2', '1/2to1/1', '1/1to2/1', '2/1to3/1', '3/1to3/0', '3.0toD'],
    #             ['Oto0/2', '0/2to1/2', '1/2to2/2', '2/2to2/1', '2/1to3/1', '3/1to3/0', '3.0toD']]
    # for plan in test_list:
    #     print(plan)
    #     print(obtain_direction_from_list(net,plan,20))
    #     print('-'*60)
        
