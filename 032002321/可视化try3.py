import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import os
from multiprocessing.dummy import Pool
import pandas as pd
import pyecharts as pye
import re


file_name = r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\中国每日本土新增无症状人数.xlsx'
df = pd.read_excel(file_name)
full_time_list = df.columns


file_name = r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\中国每日本土新增确诊人数（转置版）.xlsx'
df = pd.read_excel(file_name)
province_list = list[df]
# print(province_list)
# print('==========================================================')
data = []
total_num = []
i=0
for row in df.index.values:  # 获取行号的索引，并对其进行遍历：
    # 根据row来获取每一行指定的数据 并利用to_dict转成字典
    all_province_dic = df.loc[row, ['河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽',
        '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '海南',
        '四川', '贵州', '云南', '陕西', '甘肃', '青海', '北京', '天津',
        '上海', '重庆', '内蒙古', '广西', '西藏', '宁夏', '新疆']].to_dict()
    all_num_list=df.loc[row, ['中国大陆（无港澳台）']].to_list()
    # print(all_num_list)
    total_num.append(all_num_list)
    # test_data.append(all_province_dic)
    # print(all_province_dic)
    # print(all_num_list)
    data_list=[]
    for city in all_province_dic.keys(): #获得
        each_city_dic = {}
        each_city_dic["name"]=city
        each_city_dic_value_list=[]
        each_city_dic_value_list.append(all_province_dic[city])
        if(all_num_list[0]==0): #被除数为0
            num=0.00
        else:
            num=all_province_dic[city]/all_num_list[0]
        each_city_dic_value_list.append(num)
        each_city_dic_value_list.append(city)
        each_city_dic["value"]=each_city_dic_value_list
        data_list.append(each_city_dic)
        # print(each_city_dic)
    i+=1
    data_dic={}
    data_dic["data"]=data_list
    data_dic["time"]=full_time_list[i].split('.')[1]
    data.append(data_dic)



# time_list = [str(d) + "年" for d in range(1993, 2019)]
time_list=[]
for num in full_time_list:
        if(num!="Unnamed: 0"):
            time_list.append(num.split('.')[1])

print(time_list)
print(data[0], len(data))