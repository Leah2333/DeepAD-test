import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs

def read_xml(path):
    s = ''
    with open(path) as f:
        data = f.read()
        s = s + data
    return s

def read_elements(xml_doc,tag1,tag2):
    '''
    读取某种类型的xml元素
    tag1: 一级标签 如 edge juction tlLogic
    tag2: 二级标签 如 lane request phase
    '''
    upper_elements = xml_doc.select(tag1)
    upper_element_list = []
    lower_element_list = []
    for upper_element in upper_elements:
        attr1_dict = {}
        for attr in upper_element.attrs:
            attr1_dict[attr] = upper_element[attr]
        upper_element_list.append(attr1_dict)
        
        upper_element_id = upper_element['id']
        lower_elements = upper_element.select(tag2)
        if lower_elements != []: # 有不少junction是不带request的 可以节省时间
            for lower_element in lower_elements:
                # 把所有的元素都存进字典中 再存入一个上级的id方便索引匹配
                attr2_dict = {}
                attr2_dict['{}_id'.format(tag1)] = upper_element_id
                for attr in lower_element.attrs:
                    attr2_dict[attr] = lower_element[attr] # 字典的所有元素直接添加即可 添加好以后 再整体放到一个list中
                lower_element_list.append(attr2_dict)
            
    upper_element_df = pd.DataFrame(upper_element_list)
    lower_element_df = pd.DataFrame(lower_element_list)
    return upper_element_df, lower_element_df
    
    
def read_edges(xml_doc):
    edges_df,lanes_df = read_elements(xml_doc,'edge','lane')
    # 与lane的冲突的元素要做一个区分
    edges_df.rename(columns = {'id':'edge_id'}, inplace = True)
    edges_df.rename(columns = {'shape':'edge_shape'}, inplace = True)
    lanes_df.rename(columns = {'id': 'lane_id'}, inplace = True)
    lanes_df.rename(columns = {'index':'lane_index'}, inplace = True)
    lanes_df.rename(columns = {'shape':'lane_shape'}, inplace = True)
    return edges_df,lanes_df


def read_junctions(xml_doc):
    junctions_df,requests_df = read_elements(xml_doc,'junction','request')
    junctions_df.rename(columns = {'id': 'junction_id'}, inplace = True)
    junctions_df.rename(columns = {'type':'junction_type'}, inplace = True)
    requests_df.rename(columns = {'index': 'request_index'}, inplace = True)
    return junctions_df,requests_df


def read_tlLogic(xml_doc):
    tlLogics_df,phases_df = read_elements(xml_doc,'tllogic','phase')
    # id 和 type 是 python 关键字 需要先替换掉
    tlLogics_df.rename(columns = {'id': 'tlLogic_id'}, inplace = True)
    tlLogics_df.rename(columns = {'type':'tlLogic_type'}, inplace = True)
    return tlLogics_df,phases_df


def read_connections(xml_doc):
    # 只有一层的xml 直接读取也行
    connections = xml_doc.select('connection')
    connections_list = []
    for connection in connections:
        attr_dict = {}
        for attr in connection.attrs:
            attr_dict[attr] = connection[attr] # 所有属性添加到字典中
        connections_list.append(attr_dict)
    connections_df = pd.DataFrame(connections_list)
    # 试验了一下 连接车道肯定会小于10个，所以位数就是一位
    connections_df['vialane'] = connections_df['via'].str[-1:]
    # 读取原来的 edge  
    connections_df['viaedge'] = connections_df['via'].str[:-2]
    return connections_df


def unstack_junctions(df,flag):
    # flag: inclanes or intalnes
    '''
    把junctions中的inclanes/intlanes 拆开成两列：edge一列 laneidex 一列
    我们是先取出来 id inclines 两列 所以其他列也不会混进来
    '''
    df = df.drop('{}'.format(flag), axis=1).join(df['{}'.format(flag)].str.split(' ', expand=True).stack().reset_index(level=1, drop=True).rename('{}'.format(flag)))
    df['edge'] = df['{}'.format(flag)].str[:-2]
    df['laneindex'] = df['{}'.format(flag)].str[-1:]
    del df['{}'.format(flag)]
    return df

def lanes_join(df):
    # 每个之间空一个格 符合相应的格式
    return ' '.join(df.values)

def merge_junction_lanes(df, flag):
    '''inclanes/intalnes中合并到一行
    flag 还是选择是inclane 还是intlane'''
    df['{}'.format(flag)] = df['edge'] + '_' + df['laneindex']
    # 合并起来 他这个默认的index那一列的名称是id
    lanes = pd.DataFrame(df.groupby(['junction_id'])['{}'.format(flag)].apply(lanes_join))
    # 删除重复行
    #df.drop_duplicates(['id'],inplace = True)
    # 删除两个列 否则merge 的时候会出现inclane_x inclane_y
    return lanes

def cal_replace_list(dfe):
    edge_id_list = dfe[dfe['function'] != 'internal']['edge_id'].values
    from_list = dfe[dfe['function'] != 'internal']['from'].values
    to_list = dfe[dfe['function'] != 'internal']['to'].values
    new_edge_id_list = list(map(lambda x, y: "{}@{}".format(x,y), from_list, to_list))
    replace_df = pd.DataFrame({'new_edge':new_edge_id_list})
    replace_df.reset_index(inplace = True)
    # 提取到此时的出现次数
    occurence = replace_df.groupby(['new_edge'])['index'].rank()
    # 加入标签：比如出现一次，加0
    add_label = np.subtract(occurence.values,1)
    replace_df['occurence'] = add_label
    # 要保证加的实际上是整数！而且转换为字符串的类型
    replace_df['occurence'] = replace_df['occurence'].astype('int32').astype('str')
    # 加入出现次数的标签 方便区分
    replace_df.loc[:,'new_edge'] = (replace_df['new_edge'] + '#' + replace_df['occurence'])
    new_edge_id_list = list(replace_df['new_edge'].values)
    return edge_id_list,new_edge_id_list

def replace_all_df(dfe,dfl,dfc,inclanes,intlanes):
    '''
    取出所有需要替换的edge 并且针对dataframe 做替换
    
    '''
    edge_id_list, new_edge_id_list = cal_replace_list(dfe)
    dfe['edge_id'].replace(edge_id_list,new_edge_id_list,inplace = True)
    dfl['edge_id'].replace(edge_id_list,new_edge_id_list,inplace = True)
    dfc['from'].replace(edge_id_list,new_edge_id_list,inplace = True)
    dfc['to'].replace(edge_id_list,new_edge_id_list,inplace = True)
    # 其connection 的 via 一般是内部的道路 所以也不应该做修改 这一行可以删除掉
    dfc['viaedge'].replace(edge_id_list,new_edge_id_list,inplace = True)
    inclanes['edge'].replace(edge_id_list,new_edge_id_list,inplace = True)
    # 其实 intlanes 不需要怎么替换 基本上都没变
    intlanes['edge'].replace(edge_id_list,new_edge_id_list,inplace = True)
    return dfe,dfl,dfc,inclanes,intlanes

def process_df(xml_doc):
    '''
    整合 读入 & 处理（替换） pandas dataframe 格式
    '''
    dfe,dfl = read_edges(xml_doc)
    dft,dfp = read_tlLogic(xml_doc)
    dfj,dfr = read_junctions(xml_doc)
    dfc = read_connections(xml_doc)
    print('input finished')
    
    # 需要把 inclanes intlanes 中以空格分隔的多个edge拆分
    inclanes = unstack_junctions(dfj.loc[:,['junction_id','inclanes']],'inclanes')
    intlanes = unstack_junctions(dfj.loc[:,['junction_id','intlanes']],'intlanes')
    del dfj['inclanes']
    del dfj['intlanes']

    # 需要替换所有的edge
    dfe,dfl,dfc,inclanes,intlanes = replace_all_df(dfe,dfl,dfc,inclanes,intlanes)
    dfl.loc[:,'lane_id'] = (dfl['edge_id'] + '_' + dfl['lane_index']) # edge_id 已经被replace了，lane id 重新写
    inclanes = merge_junction_lanes(inclanes, 'inclanes')
    intlanes = merge_junction_lanes(intlanes, 'intlanes')
    dfj = pd.merge(left = dfj, right = inclanes, on='junction_id',how='left')
    dfj = pd.merge(left = dfj, right = intlanes, on='junction_id',how='left')
    print('process finished')

    return dfe,dfl,dft,dfp,dfj,dfr,dfc

def write_elements(upper_element_df,lower_element_df,tag1,tag2):
    s = '' 
    for i in range(upper_element_df.shape[0]):
        upper_element_id = upper_element_df.loc[i,'id']
        upper_attrs = upper_element_df.iloc[i,:].dropna() # 删除所有的空值项 因为意义不大
        s1 = ''
        for j in range(upper_attrs.shape[0]): # 提出edge这一行所有的属性
            s1 = s1 + ' {}="{}"'.format(upper_attrs.index[j], upper_attrs.values[j])
        s2 = '<{}{}>'.format(tag1,s1) + '\n'# 这一行edge的所有的信息
        s = s + s2
        
        lower_elements = lower_element_df.loc[lower_element_df['{}_id'.format(tag1)] == upper_element_id, :].drop_duplicates() # 在lane df中 取出所有lane的行
        
        for ii in range(lower_elements.shape[0]):
            lower_attrs = lower_elements.iloc[ii,:].dropna()
            del lower_attrs['{}_id'.format(tag1)] # 这个属性不要输入过去
            s3 = ''
            for jj in range(lower_attrs.shape[0]):
                s3 = s3 + ' {}="{}"'.format(lower_attrs.index[jj], lower_attrs.values[jj]) # 他这边要取lane index 等 所以index确实不好直接命名
            s4 = '    '+'<{}{}/>'.format(tag2,s3) + '\n'
            s = s + s4
        s = s + '</{}>'.format(tag1) + '\n'
    return s

def write_edges_xml(edge_df, lane_df):
    # 这边替换再输出执行更快
    edge_df.rename(columns = {'edge_id': 'id'}, inplace = True)
    edge_df.rename(columns = {'edge_shape': 'shape'}, inplace = True)
    lane_df.rename(columns = {'lane_id': 'id'}, inplace = True)
    #lane_df.rename(columns = {'lane_index':'index'}, inplace = True)
    lane_df.rename(columns = {'lane_shape': 'shape'}, inplace = True)
    
    # 为了方便循环，reset 一下 index
    #这边也不能直接reset index 因为它本身就带着一个index 所以用drop 不保留index
    edge_df.reset_index(drop = True, inplace = True) 
    lane_df.reset_index(drop = True, inplace = True)
    
    s = write_elements(edge_df,lane_df,'edge','lane')
    # index 会在循环的时候产生冲突
    s_final = s.replace('lane_index','index')  # 他这个虽然没有inplace = True 但是是不会改成这个形式的 要赋新值
    return s_final


def write_junctions_xml(junction_df, request_df):
    junction_df.rename(columns = {'junction_id': 'id'}, inplace = True)
    junction_df.rename(columns = {'junction_type':'type'}, inplace = True)
    junction_df.reset_index(drop = True, inplace = True) 
    request_df.reset_index(drop = True, inplace = True)
    s = write_elements(junction_df,request_df,'junction','request')
    s_final = s.replace('request_index','index')
    return s

def write_tlLogic_xml(tlLogic_df,phase_df):
    tlLogic_df.rename(columns = {'tlLogic_id': 'id'}, inplace = True)
    tlLogic_df.rename(columns = {'tlLogic_type':'type'}, inplace = True)
    tlLogic_df.reset_index(drop = True, inplace = True) 
    phase_df.reset_index(drop = True, inplace = True)
    s = write_elements(tlLogic_df,phase_df,'tllogic','phase')
    s_final = s.replace('programid','programID')
    s_final = s_final.replace('tllogic','tlLogic')
    return s_final
    
def write_connections_xml(connections_df):
    connections_df['via'] = connections_df['viaedge'] + '_' + connections_df['vialane'] # 这一个应该写到修改attr的那边
    del connections_df['vialane']
    s = ''
    for i in range(connections_df.shape[0]):
        attrs = connections_df.iloc[i,:].dropna() # 删除所有的空值项 因为意义不大
        s1 = ''
        for j in range(attrs.shape[0]): # 提出edge这一行所有的属性
            s1 = s1 + ' {}="{}"'.format(attrs.index[j], attrs.values[j])
        s2 = '<connection{}/>'.format(s1) + '\n'# 这一行edge的所有的信息
        s = s + s2
    # 默认读取出来都是小写的 不满足要求 所以需要改一下tag
    s_final = s.replace('fromlane','fromLane')
    s_final = s_final.replace('tolane','toLane')
    s_final = s_final.replace('linkindex','linkIndex')
    return s_final

def output(output_net_path,dfe,dfl,dft,dfp,dfj,dfr,dfc):
    s1 = '''<?xml version="1.0" encoding="UTF-8"?>
<!--
Luxembourg SUMO Traffic (LuST) Scenario
This project is licensed under the terms of the MIT license.
Authors: Lara CODECA [codeca@gmail.com], Matej KUBICKA [matej@matejk.cz]
-->

<net version="0.27" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">

    <location netOffset="-285448.66,-5492398.13" convBoundary="0.00,0.00,13613.76,11455.04" origBoundary="6.030969,49.549099,6.216758,49.652578" projParameter="+proj=utm +zone=32 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"/>\n'''
    s2 = write_edges_xml(dfe,dfl)
    print('write edges finished')
    s3 = write_tlLogic_xml(dft,dfp)
    print('write tlLogic finished')
    s4 = write_junctions_xml(dfj,dfr)
    print('write junctions finished')
    s5 = write_connections_xml(dfc)
    print('write connections finished')
    s6 = '</net>'
    s = s1 + s2 + s3 + s4 + s5 + s6
    with open('{}'.format(output_net_path),'w+',encoding='utf-8') as f:
        f.write(s)

def main(input_net_path,output_net_path):
    s0 = read_xml(input_net_path)
    xml_doc = bs(s0, 'lxml')
    dfe,dfl,dft,dfp,dfj,dfr,dfc = process_df(xml_doc)
    output(output_net_path,dfe,dfl,dft,dfp,dfj,dfr,dfc)

main('net.net.xml','test.net.xml')
