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
    """
    lanes_df 读进来了 但是没用到
    """
    edges_df,lanes_df = read_elements(xml_doc,'edge','lane')
    # 与lane的冲突的元素要做一个区分
    edges_df.rename(columns = {'id':'edge_id'}, inplace = True)
    edges_df.rename(columns = {'shape':'edge_shape'}, inplace = True)
    lanes_df.rename(columns = {'id': 'lane_id'}, inplace = True)
    lanes_df.rename(columns = {'index':'lane_index'}, inplace = True)
    lanes_df.rename(columns = {'shape':'lane_shape'}, inplace = True)
    return edges_df,lanes_df


def read_trips(xml_doc):
    # 只有一层的xml 直接读取也行
    trips = xml_doc.select('trip')
    trips_list = []
    for trip in trips:
        attr_dict = {}
        for attr in trip.attrs:
            attr_dict[attr] = trip[attr] # 所有属性添加到字典中
        trips_list.append(attr_dict)
    trips_df = pd.DataFrame(trips_list)
    return trips_df


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

def replace_all_df(dfe,dft):
    '''
    取出所有需要替换的edge 并且针对dataframe 做替换
    '''
    edge_id_list, new_edge_id_list = cal_replace_list(dfe)
    dft['from'].replace(edge_id_list,new_edge_id_list,inplace = True)
    dft['to'].replace(edge_id_list,new_edge_id_list,inplace = True)
    return dft

def process_df(xml_doc_net, xml_doc_trip):
    '''
    整合 读入 & 处理（替换） pandas dataframe 格式
    '''
    dfe,dfl = read_edges(xml_doc_net)
    dft = read_trips(xml_doc_trip)
    print('input finished')
    # 需要替换所有的edge
    dft = replace_all_df(dfe,dft)
    print('process finished')
    return dft

    
def write_trips_xml(trips_df):
    s = ''
    for i in range(trips_df.shape[0]):
        attrs = trips_df.iloc[i,:].dropna() # 删除所有的空值项 因为意义不大
        s1 = ''
        for j in range(attrs.shape[0]): # 提出edge这一行所有的属性
            s1 = s1 + ' {}="{}"'.format(attrs.index[j], attrs.values[j])
        s2 = '<trip{}/>'.format(s1) + '\n'# 这一行edge的所有的信息
        s = s + s2
    # 默认读取出来都是小写的 不满足要求 所以需要改一下tag
    return s

def output(output_net_path,dft):
    s1 = '''<?xml version="1.0" encoding="UTF-8"?>\n<trips>\n'''
    s2 = write_trips_xml(dft)
    print('write trips finished')
    s3 = '</trips>'
    s = s1 + s2 + s3
    with open('{}'.format(output_net_path),'w+',encoding='utf-8') as f:
        f.write(s)

def main(input_net_path,input_trip_path,output_trip_path):
    """
    input_net_path: 原来-未改ID之前的net 读进来 计算转换关系
    input_trip_path: trip.xml
    output_trip_path: 改后的trip.xml
    """
    s_net = read_xml(input_net_path)
    s_trip = read_xml(input_trip_path)
    xml_doc1 = bs(s_net, 'lxml')
    xml_doc2 = bs(s_trip,'lxml')
    dft = process_df(xml_doc1,xml_doc2)
    output(output_trip_path,dft)

if __name__ == "__main__":
    # 原始网络(未改ID)，需要改的trip，改后的trip
    main('net.net.xml','test2.rou.xml','changed.trip.xml')


