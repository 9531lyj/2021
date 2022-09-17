# -*- coding= utf-8 -*-
# @ Author lyj
# @ Time 2022/9/8  15:11

# 如何在 Pandas 中将 DataFrame 列转换为日期时间
# https://www.delftstack.com/zh/howto/python-pandas/how-to-convert-dataframe-column-to-datetime-in-pandas/

# 可视化 模板
# https://blog.csdn.net/qq_46614154/article/details/106255835

# 新增确诊
# 新增无症状感染
# 所有省份（包括）每日新增确诊、新增无症状感染    港澳台累积确诊

import requests
from lxml import etree

test_url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd_4.shtml'
first_url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml'
part_url = 'http://www.nhc.gov.cn'
first_kid_url = 'http://www.nhc.gov.cn/xcs/yqtb/202209/78ea88c5c23e41c391376ee9b103cfec.shtml'

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}
filename = 'child.txt'

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
# print(tree)


from selenium import webdriver
from lxml import etree
front_name = './raw/'
bro = webdriver.Firefox()
bro.get(first_kid_url)   # line -> url
page_text = bro.page_source
tree2 = etree.HTML(page_text)

def get_data_by_selenium():
    with open('child.txt', 'r') as file_obj:
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

#  丢弃
def get_data():
    with open('child.txt', 'r') as file_obj:
        i=1
        for line in file_obj:
            # print(line);  # eg  http://www.nhc.gov.cn/xcs/yqtb/202209/78ea88c5c23e41c391376ee9b103cfec.shtml
            url2 =line
            print(url2)
            kid = requests.get(url2, headers=headers)
            while(kid.status_code != 200):
                kid = requests.get(url2, headers=headers)
            print(kid.text)
            kid_tree = etree.HTML(kid.text)
            titles = []
            tit1 = kid_tree.xpath('/html/body/div[3]/div[2]/div[1]')
            titles.append(tit1)
            i+=1
            break
            # if (i==3):
            #     print(titles)
            #     for ti in titles:
            #         print(ti)
            #     break

def get_detailed_info_test1():

    with open('./raw/14截至1月24日24时新型冠状病毒感染的肺炎疫情最新情况.txt', 'r', encoding='utf-8') as kid_file:
        print(kid_file.readlines())


if __name__ == '__main__':
    get_child_page();
    # get_data();
    get_data_by_selenium()
    # get_detailed_info_test1()
    pass