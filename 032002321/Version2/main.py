# -*- coding= utf-8 -*-
# @ Author lyj
# @ Time 2022/9/13  18:16

import pyecharts.options as opts
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Timeline, Grid, Bar, Map, Pie, Line
from typing import List

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
import time

options = Options()
options.headless = True  # 设置不弹出浏览器

first_url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml'
part_url = 'http://www.nhc.gov.cn/xcs/yqtb'
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}
url_ = ''
info_path = r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\contents'
newPath = r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\contents'

def get_response(url):
    resp = requests.get(url=url, headers=headers)
    return resp

def get_child_links():
    kid_links = []
    for i in range(1, 42):
        if (i==1):
            url_ = first_url
        else:
            url_ = part_url+f'/list_gzbd_{i}.shtml'
        # print(url)
        resp = get_response(url_)  # 访问正常母页面
        resp_text = resp.text
        tree = etree.HTML(resp_text)  # 解析母网页
        child_part_urls = tree.xpath('/html/body/div[3]/div[2]/ul//li/a/@href')
        while ( len(child_part_urls) == 0 ):  # 没有得到正常网页,重复请求
            resp = get_response(url_)
            res_text = resp.text
            tree = etree.HTML(res_text)
            child_part_urls = tree.xpath('/html/body/div[3]/div[2]/ul//li/a/@href')
        # 获取子页面的后部分链接的列表
        # eg:    child_part_url  /xcs/yqtb/202208/8fbbe614bd0c4a5ca9cf8a9e4c289e9a.shtml
        for child_part_url in child_part_urls:
            kid_link = 'http://www.nhc.gov.cn' +child_part_url
            # eg:  'http://www.nhc.gov.cn/xcs/yqtb/202209/093a5fe2183b42169296326741d81565.shtml'
            kid_links.append(kid_link)
        # print(kid_links)
        # kid_links.append(kid_link)
        # break
        print(f'page {i} is done!')
    return kid_links
    pass


def get_child_text_multiPool(line):
        bro = webdriver.Firefox(options=options)  # 设置不弹出浏览器
        bro.get(line)
        page_text = bro.page_source
        tree = etree.HTML(page_text)
        while ('疫情通报' not in page_text):  # 是否获得正常页面
            bro.get(line)
            page_text = bro.page_source
            tree = etree.HTML(page_text)
            sleep(1)
        bro.quit()          # 及时退出浏览器
        # 获取子页面详细信息（标题，段落，发布时间）
        tits = tree.xpath('//div[@class="tit"]/text()')
        paras = tree.xpath('//div[@class="con"]//text()')
        dates = tree.xpath('/html/body/div[3]/div[2]/div[2]/span[1]/text()')  # /html/body/div[3]/div[2]/div[2]/span[1]
        launch_time = dates[0].split('：')[1].strip()
        # dat = tree.xpath('/html/body/div[3]/div[2]/div[2]/span[1]')[0]  # date => 具体时间
        # 将子页面信息保存路径拼接
        kid_text_name = launch_time + tits[0] + '.txt'
        newPath = r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\contents'
        if not os.path.exists(newPath):  # 路径不存在则创建新文件夹，
            os.mkdir(newPath)
        else:
            # 将子页面信息保存的目标路径拼接
            destination = newPath + '\\' + kid_text_name
            with open(destination, 'a', encoding='utf-8') as f:  # binary mode doesn't take an encoding argument
                # 'gbk' codec can't encode character '\u2002' in position 0: illegal multibyte sequence
                f.write(destination)
                for para in paras:
                    f.write(para)
            print(destination, ' is over! ')  # 打印抓取页面成功提示信息

# 以下获取文本详细数据的两个函数（get_new_confirmed，get_asymptomatic）参考福州大学2020级计算机03班瞿林杰同学函数
# get 每个省份新增确诊（含港澳台），参考"lj_re_test3.py"
def get_new_confirmed(path):
    path_list = os.listdir(path)
    # path_list = sorted(path_list, reverse=True)  #
    # date_time=str(date[0])
    time_city_dic = {}
    date_number = 0
    xianggang_list = [0]
    aomen_list = [0]
    taiwan_list = [0]
    for file_list in path_list:
        date_number = date_number + 1
        province_list = {'河北': 0, '山西': 0, '辽宁': 0, '吉林': 0, '黑龙江': 0, '江苏': 0, '浙江': 0, '安徽': 0, '福建': 0,
                         '江西': 0, '山东': 0, '河南': 0, '湖北': 0, '湖南': 0, '广东': 0, '海南': 0, '四川': 0, '贵州': 0, '云南': 0,
                         '陕西': 0, '甘肃': 0, '青海': 0, '台湾': 0, '内蒙古': 0, '广西': 0, '西藏': 0, '宁夏': 0, '新疆': 0, '北京': 0,
                         '天津': 0, '上海': 0, '重庆': 0, '香港': 0, '澳门': 0, '兵团': 0, '中国大陆（无港澳台）': 0}
        patt = r'(\d{4}-\d{2}-\d{2})'
        print(file_list)
        date = re.findall(patt, file_list)
        print(date)
        path = r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\contents' + '\\' + file_list
        with open(path, "r", encoding='utf-8') as f:
            file = f.readlines()
        filecontent = ''.join(file)
        patt = '(本土病例.*)'
        str1 = re.findall(patt, filecontent, re.M)
        # print(str1)
        for item in str1:
            if ('解除' not in item):
                jishu = 0
                patt = '本土病例(\d.*?)例'
                all_person_number = re.findall(patt, item)
                if (len(all_person_number) != 0):
                    # print(all_person_number)
                    province_list["中国大陆（无港澳台）"] = int(all_person_number[0])
                patt = '(\（.*?\）)?[，；。].*'
                str_test = re.findall(patt, item)

                if (str_test[0] == '' or len(str_test) == 0):  # 2020-6-23 本土病例13例，均在北京；

                    patt = '([\（，].*?[\）；]?)?[，；。].*'
                    str_test = re.findall(patt, item)
                for city in province_list.keys():
                    # ----------------------------------
                    if (len(str_test) != 0):
                        if (city in str_test[0]):
                            patt = city + '(\d*)例'
                            num = re.findall(patt, str_test[0])
                            if (len(num) != 0):
                                province_list[city] += int(num[0])
                                jishu += int(num[0])
                                # print(jishu)
                            else:
                                patt = '.*?(\d.*?)例.*?'
                                num = re.findall(patt, item)
                                if (len(num) != 0):  # 本土病例x例（在山西）
                                    # -----------------------------------
                                    if (city == '河北' and "河北区" in str_test[0]):  # 2022-02-03 天津:河北区三例
                                        continue
                                    # --------------------------------------
                                    # print(city + "1111")
                                    province_list[city] += int(num[0])
                                    jishu += int(num[0])


                                else:
                                    # print(city+"2222")
                                    province_list[city] += 1  # 2020-05-03 1例为本土病例（在山西）
                                    province_list["中国大陆（无港澳台）"] += 1
                # if(len(all_person_number) != 0 and jishu!=int(province_list["中国大陆（无港澳台）"])):
                #     print("no!!!!!!!!!!!!!!!")
                #     print(province_list["中国大陆（无港澳台）"])
                #     print(jishu)

        patt = '(香港特别行政区.*)'
        str2 = re.findall(patt, filecontent, re.M)
        # print(str2)
        yesterday_number = date_number - 1
        if (len(str2) != 0):
            if ("香港特别行政区" in str2[0]):
                patt = '香港特别行政区(\d*)例'
                num = re.findall(patt, str2[0])
                if (len(num) != 0):
                    xianggang_list.append(int(num[0]))
                    province_list["香港"] += xianggang_list[date_number] - xianggang_list[yesterday_number]

            if ("澳门特别行政区" in str2[0]):
                patt = '澳门特别行政区(\d*)例'
                num = re.findall(patt, str2[0])
                if (len(num) != 0):
                    aomen_list.append(int(num[0]))
                    province_list["澳门"] += aomen_list[date_number] - aomen_list[yesterday_number]

            if ("台湾地区" or "中国台湾" in str2[0]):
                patt = '台湾.*?(\d*)例'
                num = re.findall(patt, str2[0])
                if (len(num) != 0):
                    taiwan_list.append(int(num[0]))
                    province_list["台湾"] += taiwan_list[date_number] - taiwan_list[yesterday_number]
        else:
            xianggang_list.append(int(xianggang_list[yesterday_number]))
            taiwan_list.append(int(taiwan_list[yesterday_number]))
            aomen_list.append(int(aomen_list[yesterday_number]))

        # print(dic)
        time_specific = str(date_number) + '.' + date[0]
        time_city_dic[time_specific] = province_list
        print(str(date[0]) + '日信息录入完毕！！！')
    # df=pd.DataFrame(lists,index=date_list)
    # df.to_excel('ex2.xlsx')
    df = pd.DataFrame.from_dict(time_city_dic, orient='index')
    df.to_excel(r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\中国每日本土新增确诊人数（转置版）.xlsx')
    df = df.T
    df.to_excel(r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\中国每日本土新增确诊人数.xlsx')
    print("中国每日本土新增确诊人数已完成！！！")

# get 本土新增无症状 "lj_re_test4.py"
def get_asymptomatic(path):  # 获取无症状
    path_list = os.listdir(path)
    date_number = 0
    time_city_dic = {}
    for file_list in path_list:
        date_number += 1
        province_list = {'河北': 0, '山西': 0, '辽宁': 0, '吉林': 0, '黑龙江': 0, '江苏': 0, '浙江': 0, '安徽': 0,
                         '福建': 0,
                         '江西': 0, '山东': 0, '河南': 0, '湖北': 0, '湖南': 0, '广东': 0, '海南': 0, '四川': 0, '贵州': 0,
                         '云南': 0,
                         '陕西': 0, '甘肃': 0, '青海': 0, '内蒙古': 0, '广西': 0, '西藏': 0, '宁夏': 0,
                         '新疆': 0, '北京': 0,
                         '天津': 0, '上海': 0, '重庆': 0, '台湾': 0, '香港': 0, '澳门': 0, '兵团': 0, '中国大陆（无港澳台）': 0}
        patt = r'(\d{4}-\d{2}-\d{2})'
        date = re.findall(patt, file_list)
        path = r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\contents' + '\\' + file_list
        with open(path, "r", encoding='utf-8') as f:
            file = f.readlines()
        filecontent = ''.join(file)
        if ("无症状" in filecontent):
            patt = "(新增无症状感染者.*)"
            str_test = re.findall(patt, filecontent)
            # print(str_test)
            # print(date)

            if (len(str_test) != 0):  # 匹配目标段落
                patt = "新增无症状感染者(\d+)例"  # 匹配新增无症状感染者后的总人数
                all_infected_num_list = re.findall(patt, str_test[0])
                # if(len(all_infected_num_list)!=0):
                # print(all_infected_num_list)

                patt = "新增无症状感染者\d+例[，]?(（.*?）)?"
                bracket_content = re.findall(patt, str_test[0])
                if (len(bracket_content) != 0 and bracket_content[0] != ''):  # 匹配括号
                    # print(bracket_content)
                    patt = ".*?(\d+).+"
                    input_num = re.findall(patt, bracket_content[0])  # 匹配括号里是否有数字
                    if (len(input_num) != 0):
                        # print(input_num)
                        province_list["中国大陆（无港澳台）"] = int(all_infected_num_list[0]) - int(input_num[0])
                        print(str(date[0]) + '日无具体具体各省份信息！！！')
                    # else:  #括号里如果没有数字代表全为境外输入

                else:  # 无括号
                    patt = "本土(\d+)例"
                    all_infected_num_list = re.findall(patt, str_test[0])
                    # print(str_test[0])
                    if (len(all_infected_num_list) != 0):
                        # print(all_infected_num_list)
                        province_list["中国大陆（无港澳台）"] = int(all_infected_num_list[0])
                        patt = "本土\d+例[，]?(（.*?）)?"  # 匹配本土100例后的括号里的内容
                        every_province_list = re.findall(patt, str_test[0])
                        if (len(every_province_list) != 0 and every_province_list[0] != ''):
                            # print(every_province_list)
                            jishu = 0
                            for city in province_list.keys():
                                # ----------------------------------
                                if (len(str_test) != 0):
                                    if (city in str_test[0]):
                                        patt = city + '(\d*)例'
                                        num = re.findall(patt, str_test[0])
                                        if (len(num) != 0):  # 正常找到多少例：如括号内的北京2例
                                            province_list[city] += int(num[0])

                                            jishu += int(num[0])
                                            # print(jishu)
                                        else:  # 本土病例x例（在山西）
                                            patt = '本土(\d.*?)例.*?'
                                            num = re.findall(patt, str_test[0])
                                            if (len(num) != 0):
                                                # -----------------------------------
                                                if (city == '河北' and "河北区" in str_test[0]):  # 2022-02-03 天津:河北区三例
                                                    continue
                                                # --------------------------------------
                                                # print(city + "1111")
                                                province_list[city] += int(num[0])
                                                jishu += int(num[0])

                                            else:
                                                # print(city + "2222")
                                                province_list[city] += 1  # 2020-05-03 1例为本土病例（在山西）
                                                province_list["中国大陆（无港澳台）"] += 1
                            # if (len(all_infected_num_list[0]) != 0 and jishu != int(province_list["中国大陆（无港澳台）"])):
                            #     print("no!!!!!!!!!!!!!!!")
                            #     print(province_list["中国大陆（无港澳台）"])
                            #     print(jishu)
        time_specific = str(date_number) + '.' + date[0]
        time_city_dic[time_specific] = province_list
        print(str(date[0]) + '日信息录入完毕！！！')
    df = pd.DataFrame.from_dict(time_city_dic, orient='index')
    df.to_excel(r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\中国每日本土新增无症状人数（转置版）.xlsx')
    df = df.T
    df.to_excel(r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\中国每日本土新增无症状人数.xlsx')
    print("中国每日本土新增无症状人数已完成！！！")

time_list = []
time1_list = []
total_num = []
total_num1 = []
data = []

def form_Data_Vis():
    file_name = r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\中国每日本土新增无症状人数.xlsx'
    df = pd.read_excel(file_name)
    full_time_list = df.columns

    file_name = r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\中国每日本土新增确诊人数（转置版）.xlsx'
    df = pd.read_excel(file_name)
    province_list = list[df]
    # print(province_list)
    # print('==========================================================')
    i = 0
    for row in df.index.values:  # 获取行号的索引，并对其进行遍历：
        # 根据row来获取每一行指定的数据 并利用to_dict转成字典
        all_province_dic = df.loc[row, ['河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽',
                                        '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '海南',
                                        '四川', '贵州', '云南', '陕西', '甘肃', '青海', '北京', '天津',
                                        '上海', '重庆', '内蒙古', '广西', '西藏', '宁夏', '新疆']].to_dict()
        all_num_list = df.loc[row, ['中国大陆（无港澳台）']].to_list()
        # print(all_num_list)
        total_num.append(all_num_list[0])
        total_num1.append(int(all_num_list[0]))
        # test_data.append(all_province_dic)
        # print(all_province_dic)
        # print(all_num_list)
        data_list = []
        for city in all_province_dic.keys():  # 获得
            each_city_dic = {}
            each_city_dic["name"] = city
            each_city_dic_value_list = []
            each_city_dic_value_list.append(all_province_dic[city])
            if (all_num_list[0] == 0):  # 被除数为0
                num = 0.00
            else:
                num = all_province_dic[city] / all_num_list[0]
            each_city_dic_value_list.append(num)
            each_city_dic_value_list.append(city)
            each_city_dic["value"] = each_city_dic_value_list
            data_list.append(each_city_dic)
        i += 1
        data_dic = {}
        data_dic["data"] = data_list
        data_dic["time"] = full_time_list[i].split('.')[1]
        data.append(data_dic)

    for num in full_time_list:
        if (num != "Unnamed: 0"):
            time_list.append(num.split('.')[1])
            time1_list.append(num.split('.')[1] + "年")
    return data


def get_2020_chart_newAdd(year: str):
    minNum=0
    maxNum=130
    map_data = [
        [[x["name"], x["value"]] for x in d["data"]] for d in data if d["time"] == year
    ][0]
    min_data, max_data = (minNum, maxNum)
    data_mark: List = []
    i = 0
    # for x in time_list[600:950]:
    for x in time_list:
        if x == year:
            data_mark.append(total_num[i])
            # print(total_num[i],' ',str(i))
        else:
            data_mark.append("")
        i = i + 1
    # print(data_mark)
    map_chart = (
        Map()
        .add(
            series_name="",
            data_pair=map_data,
            zoom=1,
            center=[119.5, 34.5],
            is_map_symbol_show=False,
            itemstyle_opts={
                "normal": {"areaColor": "#323c48", "borderColor": "#404a59"},
                "emphasis": {
                    "label": {"show": Timeline},
                    "areaColor": "rgba(255,255,255, 0.5)",
                },
            },
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="" + str(year) + " ——2020中国每日本土新增确诊人数",
                subtitle="",
                pos_left="center",
                pos_top="top",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=25, color="rgba(255,255,255, 0.9)"
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter=JsCode(
                    """function(params) {
                    if ('value' in params.data) {
                        return params.data.value[2] + ': ' + params.data.value[0];
                    }
                }"""
                ),
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="30",
                pos_top="center",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    line_chart = (
        #添加疫情开始到今日的折线图
        Line()
        .add_xaxis(time_list)
        # .add_xaxis(time_list[600:950])
        # .add_yaxis("", total_num1[600:950])
        .add_yaxis("", total_num1)
        .add_yaxis(
            "",
            data_mark,
            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True)) # 是否保留数字 ？
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="自2020-01-11中国每日本土新增确诊(单位:人）", pos_left="72%", pos_top="5%"
            )
        )
    )
    bar_x_data = [x[0] for x in map_data]
    bar_y_data = [{"name": x[0], "value": x[1][0]} for x in map_data]
    bar = (
        Bar()
        .add_xaxis(xaxis_data=bar_x_data)
        .add_yaxis(
            series_name="",
            y_axis=bar_y_data,
            label_opts=opts.LabelOpts(
                is_show=True, position="right", formatter="{b} : {c}"
            ),
        )
        .reversal_axis()
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                max_=maxNum, axislabel_opts=opts.LabelOpts(is_show=False)
            ),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(is_show=False),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="10",
                pos_top="top",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    pie_data = [[x[0], x[1][0]] for x in map_data]
    pie = (
        Pie()
        .add(
            series_name="",
            data_pair=pie_data,
            radius=["15%", "35%"],
            center=["80%", "82%"],
            itemstyle_opts=opts.ItemStyleOpts(
                border_width=1, border_color="rgba(0,0,0,0.3)"
            ),
        )
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b} {d}%"),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    grid_chart = (
        Grid()
        .add(
            bar,
            grid_opts=opts.GridOpts(
                pos_left="10", pos_right="45%", pos_top="50%", pos_bottom="5"
            ),
        )
        .add(
            line_chart,
            grid_opts=opts.GridOpts(
                pos_left="65%", pos_right="80", pos_top="10%", pos_bottom="50%"
            ),
        )
        .add(pie, grid_opts=opts.GridOpts(pos_left="45%", pos_top="60%"))
        .add(map_chart, grid_opts=opts.GridOpts())
    )
    # print(map_data[0])
    # print(type(total_num[885]))
    return grid_chart

def get_2021_chart_newAdd(year: str):
    minNum = 0
    maxNum=130
    map_data = [
        [[x["name"], x["value"]] for x in d["data"]] for d in data if d["time"] == year
    ][0]
    min_data, max_data = (minNum, maxNum)
    data_mark: List = []
    i = 0
    # for x in time_list[600:950]:
    for x in time_list:
        if x == year:
            data_mark.append(total_num[i])
            # print(total_num[i],' ',str(i))
        else:
            data_mark.append("")
        i = i + 1
    # print(data_mark)
    map_chart = (
        Map()
        .add(
            series_name="",
            data_pair=map_data,
            zoom=1,
            center=[119.5, 34.5],
            is_map_symbol_show=False,
            itemstyle_opts={
                "normal": {"areaColor": "#323c48", "borderColor": "#404a59"},
                "emphasis": {
                    "label": {"show": Timeline},
                    "areaColor": "rgba(255,255,255, 0.5)",
                },
            },
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="" + str(year) + " ——2021中国每日本土新增确诊人数",
                subtitle="",
                pos_left="center",
                pos_top="top",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=25, color="rgba(255,255,255, 0.9)"
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter=JsCode(
                    """function(params) {
                    if ('value' in params.data) {
                        return params.data.value[2] + ': ' + params.data.value[0];
                    }
                }"""
                ),
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="30",
                pos_top="center",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    line_chart = (
        #添加疫情开始到今日的折线图
        Line()
        .add_xaxis(time_list)
        # .add_xaxis(time_list[600:950])
        # .add_yaxis("", total_num1[600:950])
        .add_yaxis("", total_num1)
        .add_yaxis(
            "",
            data_mark,
            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True)) # 是否保留数字 ？
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="自2020-01-11中国每日本土新增确诊(单位:人）", pos_left="72%", pos_top="5%"
            )
        )
    )
    bar_x_data = [x[0] for x in map_data]
    bar_y_data = [{"name": x[0], "value": x[1][0]} for x in map_data]
    bar = (
        Bar()
        .add_xaxis(xaxis_data=bar_x_data)
        .add_yaxis(
            series_name="",
            y_axis=bar_y_data,
            label_opts=opts.LabelOpts(
                is_show=True, position="right", formatter="{b} : {c}"
            ),
        )
        .reversal_axis()
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                max_=maxNum, axislabel_opts=opts.LabelOpts(is_show=False)
            ),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(is_show=False),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="10",
                pos_top="top",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    pie_data = [[x[0], x[1][0]] for x in map_data]
    pie = (
        Pie()
        .add(
            series_name="",
            data_pair=pie_data,
            radius=["15%", "35%"],
            center=["80%", "82%"],
            itemstyle_opts=opts.ItemStyleOpts(
                border_width=1, border_color="rgba(0,0,0,0.3)"
            ),
        )
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b} {d}%"),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    grid_chart = (
        Grid()
        .add(
            bar,
            grid_opts=opts.GridOpts(
                pos_left="10", pos_right="45%", pos_top="50%", pos_bottom="5"
            ),
        )
        .add(
            line_chart,
            grid_opts=opts.GridOpts(
                pos_left="65%", pos_right="80", pos_top="10%", pos_bottom="50%"
            ),
        )
        .add(pie, grid_opts=opts.GridOpts(pos_left="45%", pos_top="60%"))
        .add(map_chart, grid_opts=opts.GridOpts())
    )
    # print(map_data[0])
    # print(type(total_num[885]))
    return grid_chart

def get_2022_chart_newAdd(year: str):
    minNum = 0
    maxNum=130
    map_data = [
        [[x["name"], x["value"]] for x in d["data"]] for d in data if d["time"] == year
    ][0]
    min_data, max_data = (minNum, maxNum)
    data_mark: List = []
    i = 0
    # for x in time_list[600:950]:
    for x in time_list:
        if x == year:
            data_mark.append(total_num[i])
            # print(total_num[i],' ',str(i))
        else:
            data_mark.append("")
        i = i + 1
    # print(data_mark)
    map_chart = (
        Map()
        .add(
            series_name="",
            data_pair=map_data,
            zoom=1,
            center=[119.5, 34.5],
            is_map_symbol_show=False,
            itemstyle_opts={
                "normal": {"areaColor": "#323c48", "borderColor": "#404a59"},
                "emphasis": {
                    "label": {"show": Timeline},
                    "areaColor": "rgba(255,255,255, 0.5)",
                },
            },
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="" + str(year) + " ——2022中国每日本土新增确诊人数",
                subtitle="",
                pos_left="center",
                pos_top="top",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=25, color="rgba(255,255,255, 0.9)"
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter=JsCode(
                    """function(params) {
                    if ('value' in params.data) {
                        return params.data.value[2] + ': ' + params.data.value[0];
                    }
                }"""
                ),
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="30",
                pos_top="center",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    line_chart = (
        #添加疫情开始到今日的折线图
        Line()
        .add_xaxis(time_list)
        # .add_xaxis(time_list[600:950])
        # .add_yaxis("", total_num1[600:950])
        .add_yaxis("", total_num1)
        .add_yaxis(
            "",
            data_mark,
            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True)) # 是否保留数字 ？
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="自2020-01-11中国每日本土新增确诊(单位:人）", pos_left="72%", pos_top="5%"
            )
        )
    )
    bar_x_data = [x[0] for x in map_data]
    bar_y_data = [{"name": x[0], "value": x[1][0]} for x in map_data]
    bar = (
        Bar()
        .add_xaxis(xaxis_data=bar_x_data)
        .add_yaxis(
            series_name="",
            y_axis=bar_y_data,
            label_opts=opts.LabelOpts(
                is_show=True, position="right", formatter="{b} : {c}"
            ),
        )
        .reversal_axis()
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                max_=maxNum, axislabel_opts=opts.LabelOpts(is_show=False)
            ),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(is_show=False),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="10",
                pos_top="top",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    pie_data = [[x[0], x[1][0]] for x in map_data]
    pie = (
        Pie()
        .add(
            series_name="",
            data_pair=pie_data,
            radius=["15%", "35%"],
            center=["80%", "82%"],
            itemstyle_opts=opts.ItemStyleOpts(
                border_width=1, border_color="rgba(0,0,0,0.3)"
            ),
        )
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b} {d}%"),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    grid_chart = (
        Grid()
        .add(
            bar,
            grid_opts=opts.GridOpts(
                pos_left="10", pos_right="45%", pos_top="50%", pos_bottom="5"
            ),
        )
        .add(
            line_chart,
            grid_opts=opts.GridOpts(
                pos_left="65%", pos_right="80", pos_top="10%", pos_bottom="50%"
            ),
        )
        .add(pie, grid_opts=opts.GridOpts(pos_left="45%", pos_top="60%"))
        .add(map_chart, grid_opts=opts.GridOpts())
    )
    # print(map_data[0])
    # print(type(total_num[885]))
    return grid_chart

def VisNewAdd():
    timeline2020 = Timeline(
        init_opts=opts.InitOpts(width="1600px", height="900px", theme=ThemeType.DARK)
    )
    timeline2021 = Timeline(
        init_opts=opts.InitOpts(width="1600px", height="900px", theme=ThemeType.DARK)
    )
    timeline2022 = Timeline(
        init_opts=opts.InitOpts(width="1600px", height="900px", theme=ThemeType.DARK)
    )
    # print(time_list)
    # j=0
    # for y in time_list[600:950]:
    for y in time_list:
        if ('2020' in y):
            g2020 = get_2020_chart_newAdd(year=y)
            timeline2020.add(g2020, time_point=str(y))
        elif ('2021' in y):
            g2021 = get_2021_chart_newAdd(year=y)
            timeline2021.add(g2021, time_point=str(y))
        elif ('2022' in y):
            g2022 = get_2022_chart_newAdd(year=y)
            timeline2022.add(g2022, time_point=str(y))
        print(y)
    timeline2020.add_schema(
        orient="vertical",
        is_auto_play=True,
        is_inverse=True,
        play_interval=5000,
        pos_left="null",
        pos_right="5",
        pos_top="20",
        pos_bottom="20",
        width="60",
        label_opts=opts.LabelOpts(is_show=True, color="#fff"),
    )

    timeline2020.render("2020年china新增确诊（自2020-01-11起）.html")

    # ============================2021==============================================
    timeline2021.add_schema(
        orient="vertical",
        is_auto_play=True,
        is_inverse=True,
        play_interval=5000,
        pos_left="null",
        pos_right="5",
        pos_top="20",
        pos_bottom="20",
        width="60",
        label_opts=opts.LabelOpts(is_show=True, color="#fff"),
    )
    timeline2021.render("2021年china新增确诊（自2021-01-01起）.html")
    # ============================2022==============================================
    timeline2022.add_schema(
        orient="vertical",
        is_auto_play=True,
        is_inverse=True,
        play_interval=5000,
        pos_left="null",
        pos_right="5",
        pos_top="20",
        pos_bottom="20",
        width="60",
        label_opts=opts.LabelOpts(is_show=True, color="#fff"),
    )
    timeline2022.render("2022年china新增确诊（自2021-01-01起）.html")

    print("新增确诊可视化 Over!")

def get_2020_chart_Asym(year: str):
    minNum=0
    maxNum=50
    map_data = [
        [[x["name"], x["value"]] for x in d["data"]] for d in data if d["time"] == year
    ][0]
    min_data, max_data = (minNum, maxNum)
    data_mark: List = []
    i = 0
    # for x in time_list[600:950]:
    for x in time_list:
        if x == year:
            data_mark.append(total_num[i])
            # print(total_num[i],' ',str(i))
        else:
            data_mark.append("")
        i = i + 1
    # print(data_mark)
    map_chart = (
        Map()
        .add(
            series_name="",
            data_pair=map_data,
            zoom=1,
            center=[119.5, 34.5],
            is_map_symbol_show=False,
            itemstyle_opts={
                "normal": {"areaColor": "#323c48", "borderColor": "#404a59"},
                "emphasis": {
                    "label": {"show": Timeline},
                    "areaColor": "rgba(255,255,255, 0.5)",
                },
            },
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="" + str(year) + " ——2020中国每日本土新增无症状人数",
                subtitle="",
                pos_left="center",
                pos_top="top",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=25, color="rgba(255,255,255, 0.9)"
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter=JsCode(
                    """function(params) {
                    if ('value' in params.data) {
                        return params.data.value[2] + ': ' + params.data.value[0];
                    }
                }"""
                ),
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="30",
                pos_top="center",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    line_chart = (
        #添加疫情开始到今日的折线图
        Line()
        .add_xaxis(time_list)
        # .add_xaxis(time_list[600:950])
        # .add_yaxis("", total_num1[600:950])
        .add_yaxis("", total_num1)
        .add_yaxis(
            "",
            data_mark,
            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True)) # 是否保留数字 ？
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="自2020-01-11中国每日本土新增无症状(单位:人）", pos_left="72%", pos_top="5%"
            )
        )
    )
    bar_x_data = [x[0] for x in map_data]
    bar_y_data = [{"name": x[0], "value": x[1][0]} for x in map_data]
    bar = (
        Bar()
        .add_xaxis(xaxis_data=bar_x_data)
        .add_yaxis(
            series_name="",
            y_axis=bar_y_data,
            label_opts=opts.LabelOpts(
                is_show=True, position="right", formatter="{b} : {c}"
            ),
        )
        .reversal_axis()
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                max_=maxNum, axislabel_opts=opts.LabelOpts(is_show=False)
            ),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(is_show=False),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="10",
                pos_top="top",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    pie_data = [[x[0], x[1][0]] for x in map_data]
    pie = (
        Pie()
        .add(
            series_name="",
            data_pair=pie_data,
            radius=["15%", "35%"],
            center=["80%", "82%"],
            itemstyle_opts=opts.ItemStyleOpts(
                border_width=1, border_color="rgba(0,0,0,0.3)"
            ),
        )
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b} {d}%"),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    grid_chart = (
        Grid()
        .add(
            bar,
            grid_opts=opts.GridOpts(
                pos_left="10", pos_right="45%", pos_top="50%", pos_bottom="5"
            ),
        )
        .add(
            line_chart,
            grid_opts=opts.GridOpts(
                pos_left="65%", pos_right="80", pos_top="10%", pos_bottom="50%"
            ),
        )
        .add(pie, grid_opts=opts.GridOpts(pos_left="45%", pos_top="60%"))
        .add(map_chart, grid_opts=opts.GridOpts())
    )
    # print(map_data[0])
    # print(type(total_num[885]))
    return grid_chart

def get_2021_chart_Asym(year: str):
    minNum = 0
    maxNum = 50
    map_data = [
        [[x["name"], x["value"]] for x in d["data"]] for d in data if d["time"] == year
    ][0]
    min_data, max_data = (minNum, maxNum)
    data_mark: List = []
    i = 0
    # for x in time_list[600:950]:
    for x in time_list:
        if x == year:
            data_mark.append(total_num[i])
            # print(total_num[i],' ',str(i))
        else:
            data_mark.append("")
        i = i + 1
    # print(data_mark)
    map_chart = (
        Map()
        .add(
            series_name="",
            data_pair=map_data,
            zoom=1,
            center=[119.5, 34.5],
            is_map_symbol_show=False,
            itemstyle_opts={
                "normal": {"areaColor": "#323c48", "borderColor": "#404a59"},
                "emphasis": {
                    "label": {"show": Timeline},
                    "areaColor": "rgba(255,255,255, 0.5)",
                },
            },
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="" + str(year) + " ——2021中国每日本土新增无症状人数",
                subtitle="",
                pos_left="center",
                pos_top="top",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=25, color="rgba(255,255,255, 0.9)"
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter=JsCode(
                    """function(params) {
                    if ('value' in params.data) {
                        return params.data.value[2] + ': ' + params.data.value[0];
                    }
                }"""
                ),
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="30",
                pos_top="center",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    line_chart = (
        #添加疫情开始到今日的折线图
        Line()
        .add_xaxis(time_list)
        # .add_xaxis(time_list[600:950])
        # .add_yaxis("", total_num1[600:950])
        .add_yaxis("", total_num1)
        .add_yaxis(
            "",
            data_mark,
            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True)) # 是否保留数字 ？
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="自2020-01-11中国每日本土新增无症状(单位:人）", pos_left="72%", pos_top="5%"
            )
        )
    )
    bar_x_data = [x[0] for x in map_data]
    bar_y_data = [{"name": x[0], "value": x[1][0]} for x in map_data]
    bar = (
        Bar()
        .add_xaxis(xaxis_data=bar_x_data)
        .add_yaxis(
            series_name="",
            y_axis=bar_y_data,
            label_opts=opts.LabelOpts(
                is_show=True, position="right", formatter="{b} : {c}"
            ),
        )
        .reversal_axis()
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                max_=maxNum, axislabel_opts=opts.LabelOpts(is_show=False)
            ),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(is_show=False),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="10",
                pos_top="top",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    pie_data = [[x[0], x[1][0]] for x in map_data]
    pie = (
        Pie()
        .add(
            series_name="",
            data_pair=pie_data,
            radius=["15%", "35%"],
            center=["80%", "82%"],
            itemstyle_opts=opts.ItemStyleOpts(
                border_width=1, border_color="rgba(0,0,0,0.3)"
            ),
        )
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b} {d}%"),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    grid_chart = (
        Grid()
        .add(
            bar,
            grid_opts=opts.GridOpts(
                pos_left="10", pos_right="45%", pos_top="50%", pos_bottom="5"
            ),
        )
        .add(
            line_chart,
            grid_opts=opts.GridOpts(
                pos_left="65%", pos_right="80", pos_top="10%", pos_bottom="50%"
            ),
        )
        .add(pie, grid_opts=opts.GridOpts(pos_left="45%", pos_top="60%"))
        .add(map_chart, grid_opts=opts.GridOpts())
    )
    # print(map_data[0])
    # print(type(total_num[885]))
    return grid_chart

def get_2022_chart_Asym(year: str):
    minNum = 0
    maxNum = 50
    map_data = [
        [[x["name"], x["value"]] for x in d["data"]] for d in data if d["time"] == year
    ][0]
    min_data, max_data = (minNum, maxNum)
    data_mark: List = []
    i = 0
    # for x in time_list[600:950]:
    for x in time_list:
        if x == year:
            data_mark.append(total_num[i])
            # print(total_num[i],' ',str(i))
        else:
            data_mark.append("")
        i = i + 1
    # print(data_mark)
    map_chart = (
        Map()
        .add(
            series_name="",
            data_pair=map_data,
            zoom=1,
            center=[119.5, 34.5],
            is_map_symbol_show=False,
            itemstyle_opts={
                "normal": {"areaColor": "#323c48", "borderColor": "#404a59"},
                "emphasis": {
                    "label": {"show": Timeline},
                    "areaColor": "rgba(255,255,255, 0.5)",
                },
            },
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="" + str(year) + " ——2022中国每日本土新增无症状人数",
                subtitle="",
                pos_left="center",
                pos_top="top",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=25, color="rgba(255,255,255, 0.9)"
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter=JsCode(
                    """function(params) {
                    if ('value' in params.data) {
                        return params.data.value[2] + ': ' + params.data.value[0];
                    }
                }"""
                ),
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="30",
                pos_top="center",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    line_chart = (
        #添加疫情开始到今日的折线图
        Line()
        .add_xaxis(time_list)
        # .add_xaxis(time_list[600:950])
        # .add_yaxis("", total_num1[600:950])
        .add_yaxis("", total_num1)
        .add_yaxis(
            "",
            data_mark,
            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True)) # 是否保留数字 ？
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="自2020-01-11中国每日本土新增无症状(单位:人）", pos_left="72%", pos_top="5%"
            )
        )
    )
    bar_x_data = [x[0] for x in map_data]
    bar_y_data = [{"name": x[0], "value": x[1][0]} for x in map_data]
    bar = (
        Bar()
        .add_xaxis(xaxis_data=bar_x_data)
        .add_yaxis(
            series_name="",
            y_axis=bar_y_data,
            label_opts=opts.LabelOpts(
                is_show=True, position="right", formatter="{b} : {c}"
            ),
        )
        .reversal_axis()
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                max_=maxNum, axislabel_opts=opts.LabelOpts(is_show=False)
            ),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(is_show=False),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="10",
                pos_top="top",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "yellow", "orangered"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
        )
    )

    pie_data = [[x[0], x[1][0]] for x in map_data]
    pie = (
        Pie()
        .add(
            series_name="",
            data_pair=pie_data,
            radius=["15%", "35%"],
            center=["80%", "82%"],
            itemstyle_opts=opts.ItemStyleOpts(
                border_width=1, border_color="rgba(0,0,0,0.3)"
            ),
        )
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b} {d}%"),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    grid_chart = (
        Grid()
        .add(
            bar,
            grid_opts=opts.GridOpts(
                pos_left="10", pos_right="45%", pos_top="50%", pos_bottom="5"
            ),
        )
        .add(
            line_chart,
            grid_opts=opts.GridOpts(
                pos_left="65%", pos_right="80", pos_top="10%", pos_bottom="50%"
            ),
        )
        .add(pie, grid_opts=opts.GridOpts(pos_left="45%", pos_top="60%"))
        .add(map_chart, grid_opts=opts.GridOpts())
    )
    # print(map_data[0])
    # print(type(total_num[885]))
    return grid_chart

def Vis_Asympo():
    timeline2020 = Timeline(
        init_opts=opts.InitOpts(width="1600px", height="900px", theme=ThemeType.DARK)
    )
    timeline2021 = Timeline(
        init_opts=opts.InitOpts(width="1600px", height="900px", theme=ThemeType.DARK)
    )
    timeline2022 = Timeline(
        init_opts=opts.InitOpts(width="1600px", height="900px", theme=ThemeType.DARK)
    )
    # print(time_list)
    # j=0
    # for y in time_list[600:950]:
    for y in time_list:
        if ('2020' in y):
            g2020 = get_2020_chart_Asym(year=y)
            timeline2020.add(g2020, time_point=str(y))
        elif ('2021' in y):
            g2021 = get_2021_chart_Asym(year=y)
            timeline2021.add(g2021, time_point=str(y))
        elif ('2022' in y):
            g2022 = get_2022_chart_Asym(year=y)
            timeline2022.add(g2022, time_point=str(y))
        print(y)
    timeline2020.add_schema(
        orient="vertical",
        is_auto_play=True,
        is_inverse=True,
        play_interval=5000,
        pos_left="null",
        pos_right="5",
        pos_top="20",
        pos_bottom="20",
        width="60",
        label_opts=opts.LabelOpts(is_show=True, color="#fff"),
    )

    timeline2020.render("2020年china新增无症状（自2020-01-11起）.html")

    # ============================2021==============================================
    timeline2021.add_schema(
        orient="vertical",
        is_auto_play=True,
        is_inverse=True,
        play_interval=5000,
        pos_left="null",
        pos_right="5",
        pos_top="20",
        pos_bottom="20",
        width="60",
        label_opts=opts.LabelOpts(is_show=True, color="#fff"),
    )
    timeline2021.render("2021年china新增无症状（自2021-01-01起）.html")
    # ============================2022==============================================
    timeline2022.add_schema(
        orient="vertical",
        is_auto_play=True,
        is_inverse=True,
        play_interval=5000,
        pos_left="null",
        pos_right="5",
        pos_top="20",
        pos_bottom="20",
        width="60",
        label_opts=opts.LabelOpts(is_show=True, color="#fff"),
    )
    timeline2022.render("2022年china新增无症状（自2021-01-01起）.html")

    print("新增无症状可视化Over!")


if __name__ == '__main__':
    # kids_urls = get_child_links()
    # num = len(kids_urls)
    # # 生成kids.txt文件 ,以访问子链接（网页）
    # with open('kids.txt', 'w', encoding='utf-8') as f:
    #     kids = '\n'.join(kids_urls)
    #     f.write(kids)
    # print(num, ' page links were collected.')
    # =======================================# =======================================
    # kid_lists =[]  # 相当于 kids_urls
    # with open('kids.txt', 'r', encoding='utf-8') as f:
    #     for li in f:
    #         kid_lists.append(li.strip())
    # =======================================# =======================================

    # pool = Pool(8)
    # # 多线程获取文本内容 20mins
    # pool.map(get_child_text_multiPool, kids_urls)
    # pool.map(get_child_text_multiPool, kid_lists)

    # print("=============All Raw pages are done!=============\n")
    # if not os.path.exists(r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing'):
    #     os.mkdir(r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing')
    # get_new_confirmed(newPath)
    # get_asymptomatic(newPath)
    # print("=============2 Excel formed successfully!============\n")
    # =======================================# =======================================
    data1 = form_Data_Vis()
    # print(time_list)
    VisNewAdd()
    Vis_Asympo()
    print("-==========================Over !(>=<) Over !===================================")

