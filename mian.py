# -*- coding: utf-8 -*-

#引入库
import requests
from bs4 import BeautifulSoup

# 基础URL
base_url = 'https://hayqbhgr.slider.kz/#'

def get_search_url():
    global url
    query_string = input('请输入搜索关键词：')
    url = base_url + query_string
    return url

# 发送HTTP请求获取网页内容
get_search_url()
response = requests.get(url)




