# -*- coding= utf-8 -*-
# @ Author lyj
# @ Time 2022/9/13  18:16

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
        # ex = '(.*)\（.'
        ex = r'(\d{4}-\d{2}-\d{2})'
        print(file_list)
        date = re.findall(ex, file_list)
        print(date)
        path = r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\contents' + '\\' + file_list
        with open(path, "r", encoding='utf-8') as f:
            file = f.readlines()
        filecontent = ''.join(file)
        ex = '(本土病例.*)'
        str1 = re.findall(ex, filecontent, re.M)
        # print(str1)
        for item in str1:
            if ('解除' not in item):
                jishu = 0
                ex = '本土病例(\d.*?)例'
                all_person_number = re.findall(ex, item)
                if (len(all_person_number) != 0):
                    # print(all_person_number)
                    province_list["中国大陆（无港澳台）"] = int(all_person_number[0])
                ex = '(\（.*?\）)?[，；。].*'
                str_test = re.findall(ex, item)

                if (str_test[0] == '' or len(str_test) == 0):  # 2020-6-23 本土病例13例，均在北京；

                    ex = '([\（，].*?[\）；]?)?[，；。].*'
                    str_test = re.findall(ex, item)
                for city in province_list.keys():
                    # ----------------------------------
                    if (len(str_test) != 0):
                        if (city in str_test[0]):
                            ex = city + '(\d*)例'
                            num = re.findall(ex, str_test[0])
                            if (len(num) != 0):
                                province_list[city] += int(num[0])
                                jishu += int(num[0])
                                # print(jishu)
                            else:
                                ex = '.*?(\d.*?)例.*?'
                                num = re.findall(ex, item)
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

        ex = '(香港特别行政区.*)'
        str2 = re.findall(ex, filecontent, re.M)
        # print(str2)
        yesterday_number = date_number - 1
        if (len(str2) != 0):
            if ("香港特别行政区" in str2[0]):
                ex = '香港特别行政区(\d*)例'
                num = re.findall(ex, str2[0])
                if (len(num) != 0):
                    xianggang_list.append(int(num[0]))
                    province_list["香港"] += xianggang_list[date_number] - xianggang_list[yesterday_number]

            if ("澳门特别行政区" in str2[0]):
                ex = '澳门特别行政区(\d*)例'
                num = re.findall(ex, str2[0])
                if (len(num) != 0):
                    aomen_list.append(int(num[0]))
                    province_list["澳门"] += aomen_list[date_number] - aomen_list[yesterday_number]

            if ("台湾地区" or "中国台湾" in str2[0]):
                ex = '台湾.*?(\d*)例'
                num = re.findall(ex, str2[0])
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
    df.to_excel('中国每日本土新增确诊人数（转置版）.xlsx')
    df = df.T
    df.to_excel('中国每日本土新增确诊人数.xlsx')
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
        ex = r'(\d{4}-\d{2}-\d{2})'
        date = re.findall(ex, file_list)
        path = r'D:\Working_Dir\Python.works\MadeinPycharm\untitled\Yiqing\contents' + '\\' + file_list
        with open(path, "r", encoding='utf-8') as f:
            file = f.readlines()
        filecontent = ''.join(file)
        if ("无症状" in filecontent):
            ex = "(新增无症状感染者.*)"
            str_test = re.findall(ex, filecontent)
            # print(str_test)
            # print(date)

            if (len(str_test) != 0):  # 匹配目标段落
                ex = "新增无症状感染者(\d+)例"  # 匹配新增无症状感染者后的总人数
                all_infected_num_list = re.findall(ex, str_test[0])
                # if(len(all_infected_num_list)!=0):
                # print(all_infected_num_list)

                ex = "新增无症状感染者\d+例[，]?(（.*?）)?"
                bracket_content = re.findall(ex, str_test[0])
                if (len(bracket_content) != 0 and bracket_content[0] != ''):  # 匹配括号
                    # print(bracket_content)
                    ex = ".*?(\d+).+"
                    input_num = re.findall(ex, bracket_content[0])  # 匹配括号里是否有数字
                    if (len(input_num) != 0):
                        # print(input_num)
                        province_list["中国大陆（无港澳台）"] = int(all_infected_num_list[0]) - int(input_num[0])
                        print(str(date[0]) + '日无具体具体各省份信息！！！')
                    # else:  #括号里如果没有数字代表全为境外输入

                else:  # 无括号
                    ex = "本土(\d+)例"
                    all_infected_num_list = re.findall(ex, str_test[0])
                    # print(str_test[0])
                    if (len(all_infected_num_list) != 0):
                        # print(all_infected_num_list)
                        province_list["中国大陆（无港澳台）"] = int(all_infected_num_list[0])
                        ex = "本土\d+例[，]?(（.*?）)?"  # 匹配本土100例后的括号里的内容
                        every_province_list = re.findall(ex, str_test[0])
                        if (len(every_province_list) != 0 and every_province_list[0] != ''):
                            # print(every_province_list)
                            jishu = 0
                            for city in province_list.keys():
                                # ----------------------------------
                                if (len(str_test) != 0):
                                    if (city in str_test[0]):
                                        ex = city + '(\d*)例'
                                        num = re.findall(ex, str_test[0])
                                        if (len(num) != 0):  # 正常找到多少例：如括号内的北京2例
                                            province_list[city] += int(num[0])

                                            jishu += int(num[0])
                                            # print(jishu)
                                        else:  # 本土病例x例（在山西）
                                            ex = '本土(\d.*?)例.*?'
                                            num = re.findall(ex, str_test[0])
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
    df.to_excel('中国每日本土新增无症状人数（转置版）.xlsx')
    df = df.T
    df.to_excel('中国每日本土新增无症状人数.xlsx')
    print("中国每日本土新增无症状人数已完成！！！")
    pass

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
    print("All raw pages are done!")
    get_new_confirmed(newPath)
    get_asymptomatic(newPath)
