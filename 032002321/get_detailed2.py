# -*- coding= utf-8 -*-
# @ Author lyj
# @ Time 2022/9/8  18:43

# 新增确诊
# 新增无症状感染
# 所有省份（包括港澳台）每日新增确诊、新增无症状感染

import requests
from lxml import etree
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}
# http://www.nhc.gov.cn/xcs/yqtb/202209/78ea88c5c23e41c391376ee9b103cfec.shtml
kid1 = r'http://www.nhc.gov.cn/xcs/yqtb/202209/78ea88c5c23e41c391376ee9b103cfec.shtml'
# def get_kid():
#     resp = requests.get(kid1)
resp = requests.get(url=kid1, headers=headers)
print(resp.text)
tree = etree.HTML(resp.text)
list1 = tree.xpath('//*[@id="xw_box"]/p[1]/text()[19]')
# print(type(list1))  # 'list'
# print(list1)
# //*[@id="xw_box"]/p[1]/span[20]
# //*[@id="xw_box"]/p[1]/text()[19]
# //*[@id="xw_box"]/p[1]/text()[23]
# /html/body/div[3]/div[2]/div[3]/p[1]/text()[23]
# //*[@id="xw_box"]/p[1]/text()[24]
for li in list1:
    print(li)
