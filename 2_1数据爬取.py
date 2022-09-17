
import requests
from lxml import etree


test_url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd_4.shtml'
first_url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml'
part_url = 'http://www.nhc.gov.cn'
first_kid_url = 'http://www.nhc.gov.cn/xcs/yqtb/202209/78ea88c5c23e41c391376ee9b103cfec.shtml'

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}
filename = 'child.txt'


from selenium import webdriver
from lxml import etree
front_name = './raw/'
bro = webdriver.Firefox()
bro.get(first_kid_url)   # line -> url
page_text = bro.page_source
tree2 = etree.HTML(page_text)

# 获取子页面链接
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


def get_data_by_selenium():
    with open('child.txt', 'r') as file_obj:
        for line in file_obj:
            # print(line);  # eg  http://www.nhc.gov.cn/xcs/yqtb/202209/78ea88c5c23e41c391376ee9b103cfec.shtml
            bro.get(line)  # line -> url
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

if __name__ == '__main__':
    get_child_page();
    # get_data();
    get_data_by_selenium()
    # get_detailed_info_test1()
    pass