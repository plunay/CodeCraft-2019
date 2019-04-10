# -*- coding: utf-8 -*-
import re
import pandas as pd

def parse_file(filename):
    data = []
    with open(filename,'r',encoding='utf-8') as f:
        for line in f.readlines():
            if line.startswith('#'):
                columns_name = re.findall('\w+', line)
            else:
                # here we don't parse '-', -1 -> 1
                temp = [int(i) for i in re.findall('\d+', line)]
                data.append(temp)
    # convert to DataFrame
    data = pd.DataFrame(data, columns=columns_name)
    data.index = data['id'].values
    del data['id']
    return data

def parse_answer(filename):   
    data = [] 
    f = open('./toyconfig/answer.txt', 'r', encoding='utf-8')    
    for line in f.readlines():
        if line.startswith('#'):
            column_name = re.findall('\w+', line)
        else:
            temp = [int(i) for i in re.findall('\d+', line)]
            data.append(temp)
    maxlength = max(len(i) for i in data)
    for i in range(len(data)):
        while len(data[i]) < maxlength:
            data[i].append(0)
    while len(column_name) < maxlength:
        column_name.append('RoadId')
    
    data = pd.DataFrame(data, columns= column_name)
    data.index = data['carId'].values
    del data['carId']
    
    return data
