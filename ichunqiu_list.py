# -*- coding: utf-8 -*-
#www.5a5x.com
#获取源码


import urllib
import requests
import random
import time
from lxml import etree
from pymongo import MongoClient

my_headers = [    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
                  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
                  "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
                  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
                  "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
                  'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
                  'Opera/9.25 (Windows NT 5.1; U; en)',
                  'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
                  'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
                  'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
                  'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
                  "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
                  "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                  'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36']
headers = {
    'user-agent': random.choice(my_headers),
    'Connection': 'keep-alive',
    'host': 'bbs.ichunqiu.com',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Enocding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'referer': 'https://bbs.ichunqiu.com/forum.php',
}
#'cookie': 'aUZ1_2132_saltkey=Rdwz5wuM; aUZ1_2132_lastvisit=1539745820; __jsluid=1bf94b62d37ddefec84b183c170019f3; UM_distinctid=16680379465fa-01cc2f0f3358a4-5c10301c-13c680-16680379467111; aUZ1_2132_atarget=1; aUZ1_2132_home_diymode=1; aUZ1_2132__refer=%252Fhome.php%253Fmod%253Dspacecp%2526ac%253Dusergroup%2526gid%253D11; aUZ1_2132_visitedfid=59D41D49D81D60; CNZZDATA1262179880=79877067-1539746917-https%253A%252F%252Fwww.baidu.com%252F%7C1540363829; aUZ1_2132_st_p=0%7C1540366561%7Cdb26d0f99e34527802f8d33ea261736c; aUZ1_2132_viewid=tid_40334; Hm_lvt_a05b2675ca344b30c2cc9dc221706782=1539749418,1540198601,1540366569; aUZ1_2132_sid=qHPF9B; aUZ1_2132_st_t=0%7C1540366929%7C736bd877a3eaa0debf3a919935237c3e; aUZ1_2132_forum_lastvisit=D_60_1539749458D_49_1540198643D_81_1540198665D_59_1540366929; aUZ1_2132_seccode=397.10dbfc9ffca1d8e153; aUZ1_2132_lastact=1540367005%09forum.php%09; Hm_lpvt_a05b2675ca344b30c2cc9dc221706782=1540367007'

def get_id(page):
    url = 'https://bbs.ichunqiu.com/forum.php?mod=forumdisplay&fid=59&orderby=dateline&orderby=dateline&filter=author&page={0}'.format(page)
    dict_list = []
    page_source = requests.get(url, headers=headers).content
    html = etree.HTML(page_source)
    content_list = html.xpath("//*[starts-with(@id,'normalthread_')]")
    for content in content_list:
        post_id = content.xpath("@id")[0].replace('normalthread_', '')
        post_url = 'https://bbs.ichunqiu.com/thread-{0}-1-1.html'.format(post_id)
        post_time = content.xpath("tr/th/div[2]/i[1]/span/span/@title")
        if len(post_time) != 0:
            post_time = post_time[0]
        else:
            post_time = ''
        dict = {'_id': post_id,
                'post_url': post_url,
                'post_time': post_time,
                'crawl_id_time': time.time()}
        print(dict)
        dict_list.append(dict)
    return dict_list

def save_mongo(dict_list):
    conn = MongoClient('192.168.0.50', 27017)
    db = conn.ichunqiu
    my_set = db.test_1024
    try:
        my_set.insert_many(dict_list)
        print('******************insert database success!*************************')
    except:
        for dict in dict_list:
            try:
                my_set.insert(dict)
            except:
                print('###################insert database fail!!#######################')
        print('******************insert database success!*************************')
if __name__ == '__main__':
    page = 1
    while page <= 109:
        dict_list = get_id(page)
        save_mongo(dict_list)
        page = page + 1