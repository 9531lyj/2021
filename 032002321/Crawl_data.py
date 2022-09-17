# -*- coding= utf-8 -*-
# @ Author lyj
# @ Time 2022/9/11  22:51

from selenium import webdriver
import re
import time
import pandas as pd
import requests
from lxml import etree

test_url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd_4.shtml'
first_url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml'
part_url = 'http://www.nhc.gov.cn'
first_kid_url = 'http://www.nhc.gov.cn/xcs/yqtb/202209/78ea88c5c23e41c391376ee9b103cfec.shtml'
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}

filename = 'children.txt'
province_list = [
        '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽',
        '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '海南',
        '四川', '贵州', '云南', '陕西', '甘肃', '青海', '北京', '天津',
        '上海', '重庆', '内蒙古', '广西', '西藏', '宁夏', '新疆'
    ]

def get_child_page():
    for i in range(1, 42):
        if (i==1):
            re_url = first_url;
        else :
            # 合成每一页的母网页，为了获取子连接的后部分
            next_url = '/xcs/yqtb' + f'/list_gzbd_{i}' #:
            re_url = part_url + next_url + '.shtml'
            #  eg: http://www.nhc.gov.cn/xcs/yqtb/list_gzbd_2.shtml
            #      http://www.nhc.gov.cn/xcs/yqtb/list_gzbd_3.shtml
            #  print(re_url)
        res = requests.get(url=re_url, headers=headers)
        res_text = res.text
        tree = etree.HTML(res_text)
        child_part_url = tree.xpath('/html/body/div[3]/div[2]/ul//li/a/@href')
        while ( len(child_part_url) == 0 ):  # 没有得到正常网页,重复请求
            res = requests.get(url=re_url, headers=headers)
            res_text = res.text
            tree = etree.HTML(res_text)
            child_part_url = tree.xpath('/html/body/div[3]/div[2]/ul//li/a/@href')

        with open(filename, 'a') as ob:
            for j in child_part_url:
                print(j+'was Done!')
                ob.write(part_url+j+'\n')
        print(f'Page {i} is finished!!! \n')

# 通过selenium 一页一页获取子页面文本_yj.version （可忽略）

def get_Raw_data_by_selenium():
    front_name = './raw/'
    bro = webdriver.Firefox()
    bro.get(first_kid_url)  # line -> url
    page_text = bro.page_source
    tree2 = etree.HTML(page_text)
    with open('children.txt', 'r') as file_obj:
        for line in file_obj:
            # print(line);  # eg  http://www.nhc.gov.cn/xcs/yqtb/202209/78ea88c5c23e41c391376ee9b103cfec.shtml
            bro.get(line)   # line -> url
            page_text = bro.page_source
            while ('疫情通报' not in page_text):  # 处理奇怪的网页响应
                bro.get(line)
                page_text = bro.page_source
                tree2 = etree.HTML(page_text)
            tits = tree2.xpath('//div[@class="tit"]/text()')
            paras = tree2.xpath('//div[@class="con"]//text()')
            for tit in tits:
                # print(tit)
                fname = front_name + tit + '.txt'
                with open(fname, 'a', encoding='utf-8') as f:
                    # 'gbk' codec can't encode character '\u2002' in position 0: illegal multibyte sequence
                    f.write(tit)
                    for para in paras:
                        f.write(para)
            print(fname + ' is done! ')
# 通过selenium 一页一页1.获取提炼过的数据 并 2.存入excel（待学、完成） 乐滢.ver
def get_detailed_info_Jiang():
    with open('./children.txt', 'r', encoding='utf-8') as f:
        for line in f:
            driver = webdriver.Firefox()
            driver.get(line)
            time.sleep(5)
            news = driver.page_source

            # i=1
            # # 处理没及时响应的网页
            # while('某某' not in news):
            #     driver.get(line)
            #     time.sleep(5)
            #     news = driver.page_source
            #     i+=1
            #     if(i>3):
            #         driver.quit()


            all_dict = {}
            gat_dict = {}
            sfbt_dict = {}
            sfwzz_dict = {}
            '''我国31个省（自治区、直辖市）和新疆生产建设兵团（不包括港澳台）'''
            all_dict['day'] = re.search('截至(.*?)24时', news).group(1)  # group(1)代表括号里的内容
            # 新增确诊
            all_dict['confirm_add'] = re.search('新增确诊病例<span.*?>(\d+)</span>例，', news).group(1)
            # 新增无症状
            all_dict['wuzhengzhuang'] = re.search('新增无症状感染者<span.*?>(\d+)</span>例，', news).group(1)
            print(all_dict)

            '''港澳台'''
            # 香港累计确诊
            gat_dict['香港'] = re.search('香港特别行政区<span.*?>(\d+)</span>例', news).group(1)

            # 澳门累计确诊
            gat_dict['澳门'] = re.search('澳门特别行政区<span.*?>(\d+)</span>例', news).group(1)

            # 台湾累计确诊
            gat_dict['台湾'] = re.search('台湾地区<span.*?>(\d+)</span>例', news).group(1)

            # for k,v in gat_dict.items():
            #     print(k,v)
            print(gat_dict)
            # with open()
            for i in province_list:
                res = re.search('由无症状感染者转为确诊病例.*?本土病例.*?'+ i +'<span.*?>(\d+)</span>例', news)
                if(res == None):
                    sfbt_dict[i] = '0'
                else:
                    sfbt_dict[i] = res.group(1)
                # print(res)
            print(sfbt_dict)

            #各省份新增无症状病例
            for i in province_list:
                res = re.search('新增无症状感染者.*?本土.*?'+ i +'<span.*?>(\d+)</span>例', news)
                if (res == None):
                    sfwzz_dict[i] = '0'
                else:
                    sfwzz_dict[i] = res.group(1)
            print(sfwzz_dict)
            driver.quit()

if __name__ == '__main__':
    # get_child_page() # 获取children.txt （子网页链接 10 min）
    get_detailed_info_Jiang()  # 依次访问子网页并 解析数据   ？ 并存入excel中 ？ (待学）